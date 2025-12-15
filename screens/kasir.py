# ================================
# IMPORT KOMPONEN KIVY
# ================================
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

# ================================
# IMPORT MODUL INTERNAL
# ================================
from database import connect, now   # koneksi database & waktu transaksi
from utilist import rupiah          # format rupiah

# ================================
# IMPORT PYTHON STANDARD
# ================================
import os
import random

# ================================
# KONFIGURASI PATH STRUK
# ================================
STRUK_PATH = "/storage/emulated/0/kasir_app/struk.pdf"


class KasirScreen(Screen):
    """
    Screen Kasir
    Digunakan untuk melakukan transaksi penjualan
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Menyimpan total harga belanja
        self.total = 0

        # Menyimpan daftar ID produk yang dibeli
        self.cart = []

        # Bangun tampilan UI
        self.build_ui()

    def on_pre_enter(self, *args):
        """
        Method ini otomatis dipanggil setiap kali
        screen kasir dibuka.

        FUNGSI UTAMA:
        - Memuat ulang data produk terbaru
        - Sinkron dengan admin (jika admin tambah/edit produk)
        """
        self.load_produk()

    def build_ui(self):
        """
        Membuat tampilan antarmuka kasir
        """
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Judul
        root.add_widget(
            Label(
                text="KASIR",
                font_size=24,
                size_hint_y=None,
                height=50
            )
        )

        # List produk
        self.list_produk = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.list_produk.bind(minimum_height=self.list_produk.setter("height"))

        scroll = ScrollView(size_hint_y=0.6)
        scroll.add_widget(self.list_produk)
        root.add_widget(scroll)

        # Label total belanja
        self.lbl_total = Label(
            text="Total: Rp 0",
            font_size=20,
            size_hint_y=None,
            height=40
        )
        root.add_widget(self.lbl_total)

        # Input uang bayar
        self.pay = TextInput(
            hint_text="Uang Bayar",
            input_filter="int",
            multiline=False
        )
        root.add_widget(self.pay)

        # Tombol bayar
        btn_bayar = Button(
            text="BAYAR & CETAK STRUK",
            size_hint_y=None,
            height=50,
            background_color=(0, 0.6, 0, 1)
        )
        btn_bayar.bind(on_press=self.bayar)
        root.add_widget(btn_bayar)

        # Tombol logout
        btn_logout = Button(
            text="Logout",
            size_hint_y=None,
            height=45,
            background_color=(0.8, 0, 0, 1)
        )
        btn_logout.bind(on_press=lambda x: setattr(self.manager, "current", "login"))
        root.add_widget(btn_logout)

        self.add_widget(root)

    def load_produk(self):
        """
        Mengambil data produk dari database
        dan menampilkannya di layar kasir
        """
        self.list_produk.clear_widgets()

        conn = connect()
        c = conn.cursor()

        # Ambil produk yang stoknya masih ada
        for pid, name, price, stock in c.execute(
            "SELECT id, name, price, stock FROM products WHERE stock > 0 ORDER BY name"
        ):
            btn = Button(
                text=f"{name} | Rp {rupiah(price)} | Stok: {stock}",
                size_hint_y=None,
                height=45,
                background_color=(0, 0.6, 1, 1)
            )

            # Jika tombol produk ditekan → tambahkan ke keranjang
            btn.bind(on_press=lambda x, pid=pid, price=price: self.add(pid, price))
            self.list_produk.add_widget(btn)

        conn.close()

    def add(self, pid, price):
        """
        Menambahkan produk ke keranjang
        """
        self.total += price
        self.cart.append(pid)
        self.lbl_total.text = f"Total: Rp {rupiah(self.total)}"

    def bayar(self, *args):
        """
        Proses pembayaran:
        - Validasi uang bayar
        - Simpan transaksi
        - Kurangi stok
        - Cetak struk
        """
        if not self.pay.text:
            Popup(
                title="Error",
                content=Label(text="Masukkan jumlah bayar"),
                size_hint=(0.7, 0.3)
            ).open()
            return

        bayar = int(self.pay.text)

        if bayar < self.total:
            Popup(
                title="Error",
                content=Label(text="Uang kurang"),
                size_hint=(0.7, 0.3)
            ).open()
            return

        conn = connect()
        c = conn.cursor()

        # Kurangi stok setiap produk yang dibeli
        for pid in self.cart:
            c.execute(
                "UPDATE products SET stock = stock - 1 WHERE id = ?",
                (pid,)
            )

        # Simpan transaksi ke tabel sales
        c.execute(
            "INSERT INTO sales(total, date) VALUES (?, ?)",
            (self.total, now())
        )

        conn.commit()
        conn.close()

        # Cetak struk (PDF)
        self.cetak_pdf(bayar)

        Popup(
            title="Transaksi Berhasil",
            content=Label(
                text=f"Kembalian: Rp {rupiah(bayar - self.total)}"
            ),
            size_hint=(0.7, 0.3)
        ).open()

        # Reset transaksi
        self.total = 0
        self.cart.clear()
        self.pay.text = ""
        self.lbl_total.text = "Total: Rp 0"
        self.load_produk()

    def cetak_pdf(self, bayar):
        """
        Membuat struk transaksi dalam bentuk PDF
        """
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.pagesizes import A6
        from reportlab.lib.styles import getSampleStyleSheet

        os.makedirs("/storage/emulated/0/kasir_app", exist_ok=True)

        doc = SimpleDocTemplate(STRUK_PATH, pagesize=A6)
        styles = getSampleStyleSheet()

        content = [
            Paragraph("STRUK TRANSAKSI", styles["Title"]),
            Paragraph(f"Tanggal: {now()}", styles["Normal"]),
            Paragraph(f"No: {random.randint(1000,9999)}", styles["Normal"]),
            Paragraph(" ", styles["Normal"])
        ]

        conn = connect()
        c = conn.cursor()

        # Tampilkan daftar produk yang dibeli
        for pid in self.cart:
            c.execute("SELECT name, price FROM products WHERE id=?", (pid,))
            row = c.fetchone()
            if row:
                name, price = row
                content.append(
                    Paragraph(f"{name} | Rp {rupiah(price)}", styles["Normal"])
                )

        conn.close()

        content.append(Paragraph(" ", styles["Normal"]))
        content.append(Paragraph(f"Total: Rp {rupiah(self.total)}", styles["Normal"]))
        content.append(Paragraph(f"Bayar: Rp {rupiah(bayar)}", styles["Normal"]))
        content.append(Paragraph(f"Kembali: Rp {rupiah(bayar - self.total)}", styles["Normal"]))

        doc.build(content)