from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from database import connect
from utilist import rupiah
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
import os

PDF_LAPORAN = "/storage/emulated/0/kasir_app/laporan_penjualan.pdf"
XLSX_LAPORAN = "/storage/emulated/0/kasir_app/laporan_penjualan.xlsx"

class LaporanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        root.add_widget(Label(text="LAPORAN PENJUALAN", font_size=22, size_hint_y=None, height=50))

        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        root.add_widget(scroll)

        btn_pdf = Button(text="Export PDF", size_hint_y=None, height=45, background_color=(0.5,0,0.5,1))
        btn_pdf.bind(on_press=self.export_pdf)
        root.add_widget(btn_pdf)

        btn_excel = Button(text="Export Excel", size_hint_y=None, height=45, background_color=(0,0.5,0.7,1))
        btn_excel.bind(on_press=self.export_excel)
        root.add_widget(btn_excel)

        btn_back = Button(text="Kembali", size_hint_y=None, height=45, background_color=(0.7,0.3,0,1))
        btn_back.bind(on_press=lambda x: setattr(self.manager,'current','admin'))
        root.add_widget(btn_back)

        self.add_widget(root)
        self.load_laporan()

    def load_laporan(self):
        self.grid.clear_widgets()
        conn = connect()
        c = conn.cursor()
        for tid,total,date in c.execute("SELECT id,total,date FROM sales ORDER BY date DESC"):
            self.grid.add_widget(Label(text=f"{tid} | {rupiah(total)} | {date}", size_hint_y=None, height=35))
        conn.close()

    def export_pdf(self, *args):
        os.makedirs("/storage/emulated/0/kasir_app", exist_ok=True)
        doc = SimpleDocTemplate(PDF_LAPORAN, pagesize=A4)
        styles = getSampleStyleSheet()
        content = [Paragraph("LAPORAN PENJUALAN", styles["Title"])]
        conn = connect()
        c = conn.cursor()
        for tid,total,date in c.execute("SELECT id,total,date FROM sales ORDER BY date DESC"):
            content.append(Paragraph(f"{tid} | {rupiah(total)} | {date}", styles["Normal"]))
        conn.close()
        doc.build(content)
        Popup(title="Sukses", content=Label(text=f"PDF berhasil dibuat di {PDF_LAPORAN}"), size_hint=(.7,.3)).open()

    def export_excel(self, *args):
        os.makedirs("/storage/emulated/0/kasir_app", exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.title = "Laporan Penjualan"
        ws.append(["ID", "Total (Rp)", "Tanggal"])
        conn = connect()
        c = conn.cursor()
        for tid,total,date in c.execute("SELECT id,total,date FROM sales ORDER BY date DESC"):
            ws.append([tid, total, date])
        conn.close()
        wb.save(XLSX_LAPORAN)
        Popup(title="Sukses", content=Label(text=f"Excel berhasil dibuat di {XLSX_LAPORAN}"), size_hint=(.7,.3)).open()