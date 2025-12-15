from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from database import connect

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        box = BoxLayout(orientation="vertical", padding=20, spacing=10)
        box.add_widget(Label(text="LOGIN APP KASIR", font_size=24, size_hint_y=None, height=50))
        
        self.username = TextInput(hint_text="Username", multiline=False)
        self.password = TextInput(hint_text="Password", password=True, multiline=False)
        box.add_widget(self.username)
        box.add_widget(self.password)

        btn_login = Button(text="Login", size_hint_y=None, height=45)
        btn_login.bind(on_press=self.login)
        box.add_widget(btn_login)

        self.add_widget(box)

    def login(self, *args):
        u = self.username.text.strip()
        p = self.password.text.strip()
        if not u or not p:
            Popup(title="Error", content=Label(text="Username atau password kosong"), size_hint=(.7,.3)).open()
            return

        conn = connect()
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (u,p))
        row = c.fetchone()
        conn.close()

        if not row:
            Popup(title="Error", content=Label(text="Username atau password salah"), size_hint=(.7,.3)).open()
            return

        role = row[0]
        if role == "admin":
            self.manager.current = "admin"
        else:
            self.manager.current = "kasir"