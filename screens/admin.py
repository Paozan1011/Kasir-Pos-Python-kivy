from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from database import connect
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import os

PDF_PATH = "/storage/emulated/0/kasir_app/laporan_admin.pdf"

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        root.add_widget(Label(text="ADMIN", font_size=26, size_hint_y=None, height=50))

        # Input barcode
        self.scan = TextInput(hint_text="Scan / Input Barcode", multiline=False, size_hint_y=None, height=45)
        self.scan.bind(on_text_validate=self.scan_barcode)
        root.add_widget(self.scan)

        # Tombol tambah barang manual
        btn_add = Button(text="Tambah Barang Manual", size_hint_y=None, height=45, background_color=(0,0.7,0,1))
        btn_add.bind(on_press=lambda x: self.popup_add(""))
        root.add_widget(btn_add)

        # Grid list barang
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        root.add_widget(scroll)

        # Tombol PDF
        btn_pdf = Button(text="Export PDF", size_hint_y=None, height=45, background_color=(0.5,0,0.5,1))
        btn_pdf.bind(on_press=self.export_pdf)
        root.add_widget(btn_pdf)

        # Laporan penjualan
        btn_laporan = Button(text="Lihat Laporan Penjualan", size_hint_y=None, height=45, background_color=(0,0.5,1,1))
        btn_laporan.bind(on_press=lambda x: setattr(self.manager, "current", "laporan"))
        root.add_widget(btn_laporan)

        # Logout
        btn_logout = Button(text="Logout", size_hint_y=None, height=45, background_color=(0.8,0,0,1))
        btn_logout.bind(on_press=lambda x: setattr(self.manager, "current", "login"))
        root.add_widget(btn_logout)

        self.add_widget(root)
        self.refresh()

    def refresh(self):
        self.grid.clear_widgets()
        conn = connect()
        c = conn.cursor()
        for pid, b, n, p, s in c.execute("SELECT id,barcode,name,price,stock FROM products ORDER BY name"):
            row = BoxLayout(size_hint_y=None, height=45, spacing=5)
            row.add_widget(Label(text=b or "-", size_hint_x=.25))
            row.add_widget(Label(text=n, size_hint_x=.35))
            row.add_widget(Label(text=str(p), size_hint_x=.15))
            row.add_widget(Label(text=str(s), size_hint_x=.1))

            btn_edit = Button(text="Edit", size_hint_x=.1, background_color=(0,0.5,0,1))
            btn_edit.bind(on_press=lambda x, pid=pid: self.popup_edit(pid))
            btn_del = Button(text="Hapus", size_hint_x=.1, background_color=(0.7,0.1,0.1,1))
            btn_del.bind(on_press=lambda x, pid=pid: self.delete(pid))
            row.add_widget(btn_edit)
            row.add_widget(btn_del)
            self.grid.add_widget(row)
        conn.close()

    def scan_barcode(self, instance):
        barcode = instance.text.strip()
        instance.text = ""
        self.popup_add(barcode)

    def popup_add(self, barcode=""):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        inp_barcode = TextInput(text=barcode, hint_text="Barcode", multiline=False)
        inp_name = TextInput(hint_text="Nama Barang", multiline=False)
        inp_price = TextInput(hint_text="Harga", input_filter="int", multiline=False)
        inp_stock = TextInput(hint_text="Stok", input_filter="int", multiline=False)
        box.add_widget(inp_barcode)
        box.add_widget(inp_name)
        box.add_widget(inp_price)
        box.add_widget(inp_stock)

        popup = Popup(title="Tambah Barang", content=box, size_hint=(.8,.7))
        btn = Button(text="Simpan", size_hint_y=None, height=45)
        btn.bind(on_press=lambda x: self.save(inp_barcode.text, inp_name.text, inp_price.text, inp_stock.text, popup))
        box.add_widget(btn)
        popup.open()

    def save(self, b, n, p, s, popup):
        if not b or not n or not p or not s: return
        conn = connect()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO products(barcode,name,price,stock) VALUES(?,?,?,?)",(b,n,int(p),int(s)))
        conn.commit()
        conn.close()
        popup.dismiss()
        self.refresh()

    def popup_edit(self, pid):
        conn = connect()
        c = conn.cursor()
        c.execute("SELECT barcode,name,price,stock FROM products WHERE id=?",(pid,))
        row = c.fetchone()
        conn.close()
        if not row: return
        barcode,name,price,stock = row
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        inp_name = TextInput(text=name, multiline=False)
        inp_price = TextInput(text=str(price), input_filter="int")
        inp_stock = TextInput(text=str(stock), input_filter="int")
        box.add_widget(Label(text=f"Barcode: {barcode}"))
        box.add_widget(inp_name)
        box.add_widget(inp_price)
        box.add_widget(inp_stock)
        popup = Popup(title="Edit Barang", content=box, size_hint=(.8,.7))
        btn = Button(text="Simpan Perubahan", size_hint_y=None, height=45)
        btn.bind(on_press=lambda x: self.update(pid, inp_name.text, inp_price.text, inp_stock.text, popup))
        box.add_widget(btn)
        popup.open()

    def update(self, pid, n, p, s, popup):
        conn = connect()
        c = conn.cursor()
        c.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?",(n,int(p),int(s),pid))
        conn.commit()
        conn.close()
        popup.dismiss()
        self.refresh()

    def delete(self, pid):
        conn = connect()
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=?",(pid,))
        conn.commit()
        conn.close()
        self.refresh()

    def export_pdf(self, *args):
        os.makedirs("/storage/emulated/0/kasir_app", exist_ok=True)
        doc = SimpleDocTemplate(PDF_PATH, pagesize=A4)
        styles = getSampleStyleSheet()
        content = [Paragraph("DATA BARANG", styles["Title"])]
        conn = connect()
        c = conn.cursor()
        for pid,b,n,p,s in c.execute("SELECT id,barcode,name,price,stock FROM products ORDER BY name"):
            content.append(Paragraph(f"{b} | {n} | Rp {p} | Stok {s}", styles["Normal"]))
        conn.close()
        doc.build(content)
        Popup(title="Sukses", content=Label(text="PDF berhasil dibuat"), size_hint=(.7,.3)).open()