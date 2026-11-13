import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

CITIES = {
    "Cairo": (30.0444, 31.2357),
    "Alexandria": (31.2001, 29.9187),
    "Giza": (30.0131, 31.2089),
    "Mansoura": (31.0409, 31.3785),
    "Tanta": (30.7865, 31.0004),
    "Assiut": (27.1783, 31.1859),
    "Luxor": (25.6872, 32.6396),
    "Aswan": (24.0889, 32.8998),
    "Suez": (29.9668, 32.5498),
    "Port Said": (31.2653, 32.3019),
}
STEPS = ["Fa7s el telefon...", "Tat-beet tazkerat el salah...", "Tat-beet el azkar...", "Ta3deel el mawa3eed..."]


class AdhanApp(App):
    def build(self):
        self.flag = os.path.join(self.user_data_dir, "running")
        root = BoxLayout(orientation="vertical", padding=24, spacing=14)
        self.status = Label(text=self.status_text(), font_size="18sp", size_hint_y=0.3)
        self.city = Spinner(text=self.saved_city(), values=list(CITIES), size_hint_y=0.12)
        self.start_btn = Button(text="Ebda2 (Start)", font_size="20sp")
        self.start_btn.bind(on_release=self.begin_intro)
        stop_btn = Button(text="Eqaf (Stop)", font_size="20sp", background_color=(0.8, 0.2, 0.2, 1))
        stop_btn.bind(on_release=self.stop_service)
        batt = Button(text="Esma7 lel app yeshtaghal fel khalfeya", size_hint_y=0.12)
        batt.bind(on_release=self.battery_settings)
        for w in (self.status, self.city, self.start_btn, stop_btn, batt):
            root.add_widget(w)
        return root

    def on_start(self):
        try:
            from android.permissions import request_permissions
            request_permissions(["android.permission.POST_NOTIFICATIONS"])
        except Exception:
            pass

    def saved_city(self):
        try:
            return json.load(open(os.path.join(self.user_data_dir, "city.json")))["name"]
        except Exception:
            return "Cairo"

    def status_text(self):
        return "SHAGHAL" if os.path.exists(self.flag) else "Mawa2ef (mesh shaghal)"

    def begin_intro(self, *_):
        self.i = 0
        self.start_btn.disabled = True
        Clock.schedule_interval(self.step, 0.7)

    def step(self, dt):
        if self.i < len(STEPS):
            self.status.text = STEPS[self.i]
            self.i += 1
            return True
        self.status.text = "TAM! Eshta, el telefon geh 3ala el nour."
        self.start_service()
        self.start_btn.disabled = False
        return False

    def start_service(self):
        name = self.city.text
        lat, lng = CITIES[name]
        json.dump({"name": name}, open(os.path.join(self.user_data_dir, "city.json"), "w"))
        try:
            from android import AndroidService
            svc = AndroidService("تذكير الصلاة والأذكار", "شغال بإذن الله")
            svc.start(json.dumps({"lat": lat, "lng": lng, "name": name}))
            open(self.flag, "w").write("1")
        except Exception as e:
            self.status.text = "Error: %s" % e

    def stop_service(self, *_):
        try:
            from android import AndroidService
            AndroidService().stop()
        except Exception:
            pass
        try:
            os.remove(self.flag)
        except OSError:
            pass
        self.status.text = "Et2afal. Mafish 7aga shaghala."

    def battery_settings(self, *_):
        try:
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            autoclass("org.kivy.android.PythonActivity").mActivity.startActivity(
                Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
        except Exception as e:
            self.status.text = "Error: %s" % e


AdhanApp().run()
