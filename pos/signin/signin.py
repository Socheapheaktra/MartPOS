from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.config import Config
from subprocess import call
from kivy.core.window import Window

import mysql.connector

Builder.load_file('signin/signin.kv')

class CallAdmin(object):
    def __init__(self, path="D:/Study(TRA)/Python/MartPOS/pos/admin/admin.py"):
        self.path = path

    def call_admin_file(self):
        call(["python", "{}".format(self.path)])

class SigninWindow(BoxLayout):
    admin = CallAdmin()

    def __init__(self, **kwargs):
        super(SigninWindow, self).__init__(**kwargs)

    def close_app(self, obj):
        App.get_running_app().stop()
        Window.close()

    def validate_user(self):
        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        username = user.text
        password = pwd.text

        user_pwd = ''
        user_des = ''

        if username == "" or password == "":
            info.text = "[color=#FF0000]Username or Password Required[/color]"
        else:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd="1234"'',
                database='pos'
            )
            mycursor = mydb.cursor()
            sql = 'SELECT * FROM users WHERE user_name=%s'
            values = (username, )
            mycursor.execute(sql, values)
            target_user = mycursor.fetchall()
            for x in target_user:
                user_pwd = x[4]
                user_des = x[5]
            if target_user == []:
                info.text = "[color=#FF0000]Invalid Username[/color]"
            else:
                if password == user_pwd:
                    des = user_des
                    info.text = "[color=#00FF00]Logged in successfully[/color]"
                    if des == "Administrator":
                        self.parent.parent.current = "scrn_admin"
                        self.ids.username_field.text = ""
                        self.ids.pwd_field.text = ""
                        self.ids.info.text = ""
                    else:
                        self.parent.parent.current = "scrn_op"
                        self.ids.username_field.text = ""
                        self.ids.pwd_field.text = ""
                        self.ids.info.text = ""
                else:
                    info.text = "[color=#FF0000]Incorrect Password[/color]"


class SigninApp(App):

    def build(self):
        return SigninWindow()

if __name__ == "__main__":
    sa = SigninApp()
    sa.run()