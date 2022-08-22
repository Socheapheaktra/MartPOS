from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from utils.datatable import DataTable
from signin.signin import SigninWindow
from admin.admin import *
from userinterface.userinterface import UserInterfaceWindow
from collections import OrderedDict
from kivy.uix.popup import Popup

class MainWindow(BoxLayout):

    signin_widget = SigninWindow()
    admin_widget = AdminWindow()
    userinterface_widget = UserInterfaceWindow()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.scrn_si.add_widget(self.signin_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)
        self.ids.scrn_op.add_widget(self.userinterface_widget)

class MainApp(App):
    def build(self):

        return MainWindow()


if __name__ == "__main__":
    MainApp().run()

