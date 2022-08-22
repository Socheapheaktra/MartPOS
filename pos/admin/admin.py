from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config
from subprocess import call

from collections import OrderedDict
from pymongo import MongoClient
from utils.datatable import DataTable
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as FCK
import mysql.connector

Builder.load_file('admin/admin.kv')


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (.7, .7)

class CallSignIn(object):
    def __init__(self, path="D:/Study(TRA)/Python/MartPOS/pos/main.py"):
        self.path = path

    def call_signin_file(self):
        call(["Python", "{}".format(self.path)])


class AdminWindow(BoxLayout):
    signin = CallSignIn()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notify = Notify()

    def display_users(self):
        content = self.ids.scrn_contents
        content.clear_widgets()
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def display_products(self):
        product_scrn = self.ids.scrn_product_contents
        product_scrn.clear_widgets()
        products = self.get_products()
        prod_table = DataTable(table=products)
        product_scrn.add_widget(prod_table)

    def display_spinner(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        product_code = []
        product_name = []
        spinvals = []
        sql = 'SELECT * FROM stocks'
        mycursor.execute(sql)
        products = mycursor.fetchall()
        for product in products:
            product_code.append(product[1])
            name = product[2]
            if len(name) > 30:
                name = name[:30] + "..."
            product_name.append(name)
        for x in range(len(product_code)):
            line = ' | '.join([product_code[x], product_name[x]])
            spinvals.append(line)
        self.ids.target_product.values = spinvals

    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text="Product Code", multiline=False)
        crud_name = TextInput(hint_text="Product Name", multiline=False)
        crud_weight = TextInput(hint_text="Product Weight", multiline=False)
        crud_stock = TextInput(hint_text="Product In Stock", multiline=False)
        crud_sold = TextInput(hint_text="Product Sold", multiline=False)
        crud_order = TextInput(hint_text="Product Order", multiline=False)
        crud_purchase = TextInput(hint_text="Product Last Purchase", multiline=False)
        crud_submit = Button(text="Add", size_hint_x=None, width=100, on_release=lambda x:
        self.add_product(crud_code.text, crud_name.text, crud_weight.text,
                         crud_stock.text, crud_sold.text,
                         crud_order.text, crud_purchase.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(crud_order)
        target.add_widget(crud_purchase)
        target.add_widget(crud_submit)

    def add_product(self, code, name, weight, stock, sold, order, purchase):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        content = self.ids.scrn_product_contents
        content.clear_widgets()
        if code == '' or name == '' or weight == '' or stock == '' or order == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b]'
                                              '[/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            sql = 'INSERT INTO stocks(product_code, product_name, product_weight, in_stock,' \
                  'sold, ordered, last_purchase) VALUES(%s,%s,%s,%s,%s,%s,%s)'
            values = [code, name, weight, stock, sold, order, purchase]

            mycursor.execute(sql, values)
            mydb.commit()

        self.ids.ops_fields_p.clear_widgets()
        products = self.get_products()
        prod_table = DataTable(table=products)
        content.add_widget(prod_table)

    def add_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name', multiline=False)
        crud_last = TextInput(hint_text='Last Name', multiline=False)
        crud_user = TextInput(hint_text='Username', multiline=False)
        crud_pwd = TextInput(hint_text='Password', multiline=False)
        crud_des = Spinner(text='Operator', values=['Operator', 'Administrator'])
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x:
                             self.add_user(crud_first.text, crud_last.text, crud_user.text,
                                           crud_pwd.text, crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def add_user(self, first, last, user, pwd, des):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        content = self.ids.scrn_contents
        content.clear_widgets()
        if first == '' or last == '' or user == '' or pwd == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b]'
                                              '[/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            sql = 'INSERT INTO users(first_name, last_name, user_name, password,' \
                  'designation, date) VALUES(%s,%s,%s,%s,%s,%s)'
            values = [first, last, user, pwd, des, datetime.now()]

            mycursor.execute(sql, values)
            mydb.commit()

        self.ids.ops_fields.clear_widgets()
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def update_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name', multiline=False)
        crud_last = TextInput(hint_text='Last Name', multiline=False)
        crud_user = TextInput(hint_text='Username', multiline=False)
        crud_pwd = TextInput(hint_text='Password', multiline=False)
        crud_des = Spinner(text='Operator', values=['Operator', 'Administrator'])
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x:
                             self.update_user(crud_first.text, crud_last.text, crud_user.text,
                                              crud_pwd.text, crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def update_user(self, first, last, user, pwd, des):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        content = self.ids.scrn_contents
        content.clear_widgets()
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Username Required[/b]'
                                              '[/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            sql = 'SELECT * FROM users WHERE user_name=%s'
            values = [user]
            mycursor.execute(sql, values)
            target_user = mycursor.fetchall()
            first_name = ''
            last_name = ''
            password = ''
            if target_user is None:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b]'
                                                  '[/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                for i in target_user:
                    first_name = i[1]
                    last_name = i[2]
                    password = i[4]
                if first == '':
                    first = first_name
                if last == '':
                    last = last_name
                if pwd == '':
                    pwd = password
                sql = 'UPDATE users SET first_name=%s, last_name=%s, password=%s,' \
                      'designation=%s WHERE user_name=%s'
                values = [first, last, pwd, des, user]
                mycursor.execute(sql, values)
                mydb.commit()

        self.ids.ops_fields.clear_widgets()
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text="Product Code", multiline=False, input_filter="int")
        crud_stock = TextInput(hint_text="Product In Stock", multiline=False, input_filter="int")
        crud_sold = TextInput(hint_text="Product Sold", multiline=False, input_filter="int")
        crud_order = TextInput(hint_text="Product Order", multiline=False)
        crud_purchase = TextInput(hint_text="Product Last Purchase", multiline=False)
        crud_submit = Button(text="Update", size_hint_x=None, width=100,
                             on_release=lambda x:
                             self.update_product(crud_code.text, crud_stock.text, crud_sold.text, crud_order.text,
                                                 crud_purchase.text))
        target.add_widget(crud_code)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(crud_order)
        target.add_widget(crud_purchase)
        target.add_widget(crud_submit)

    def update_product(self, code, stock, sold, order, purchase):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        content = self.ids.scrn_product_contents
        content.clear_widgets()

        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Product Code Required[/b]'
                                              '[/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            sql = 'SELECT * FROM stocks WHERE product_code=%s'
            values = [code]
            mycursor.execute(sql, values)
            target_product = mycursor.fetchall()
            product_in_stock = ''
            product_sold = ''
            product_order = ''
            product_purchase = ''
            if target_product == []:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Product Code[/b]'
                                                  '[/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                for x in target_product:
                    product_in_stock = x[5]
                    product_sold = x[6]
                    product_order = x[7]
                    product_purchase = x[8]
                if stock == '':
                    stock = product_in_stock
                if sold == '':
                    sold = product_sold
                if order == '':
                    order = product_order
                if purchase == '':
                    purchase = product_purchase


                new_stock = int(stock) - int(sold)

                sql = 'UPDATE stocks SET in_stock=%s, sold=%s, ordered=%s, last_purchase=%s WHERE product_code=%s'
                values = [new_stock, sold, order, purchase, code, ]

                mycursor.execute(sql, values)
                mydb.commit()

        self.ids.ops_fields_p.clear_widgets()
        products = self.get_products()
        prod_table = DataTable(table=products)
        content.add_widget(prod_table)

    def remove_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_user = TextInput(hint_text="User Name")
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x:
                             self.remove_user(crud_user.text))
        target.add_widget(crud_user)
        target.add_widget(crud_submit)

    def remove_user(self, user):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        content = self.ids.scrn_contents
        content.clear_widgets()
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Username Required[/b]'
                                              '[/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            sql = 'SELECT * FROM users WHERE user_name=%s'
            values = [user]
            mycursor.execute(sql, values)
            target_user = mycursor.fetchall()
            if target_user is None:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b]'
                                                  '[/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                sql = 'DELETE FROM users WHERE user_name=%s'
                values = [user]
                mycursor.execute(sql, values)
                mydb.commit()

        self.ids.ops_fields.clear_widgets()
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text="Product Code", multiline=False)
        crud_submit = Button(text="Remove", size_hint_x=None, width=100,
                             on_release=lambda x:
                             self.remove_product(crud_code.text))
        target.add_widget(crud_code)
        target.add_widget(crud_submit)

    def remove_product(self, code):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        content = self.ids.scrn_product_contents
        content.clear_widgets()
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Product Code Required[/b]'
                                              '[/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            sql = 'SELECT * FROM stocks WHERE product_code=%s'
            values = [code]
            mycursor.execute(sql, values)
            target_product = mycursor.fetchall()
            if target_product is None:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Product Code[/b]'
                                                  '[/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                sql = 'DELETE FROM stocks WHERE product_code=%s'
                values = [code]
                mycursor.execute(sql, values)
                mydb.commit()

        self.ids.ops_fields_p.clear_widgets()
        products = self.get_products()
        prod_table = DataTable(table=products)
        content.add_widget(prod_table)

    def get_users(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234""",
            database="pos"
        )
        mycursor = mydb.cursor()
        _users = OrderedDict()
        _users['first_names'] = {}
        _users['last_names'] = {}
        _users['user_names'] = {}
        _users['passwords'] = {}
        _users['designations'] = {}
        first_names = []
        last_names = []
        user_names = []
        passwords = []
        designations = []

        sql = "SELECT * FROM users"
        mycursor.execute(sql)
        users = mycursor.fetchall()

        for user in users:
            first_names.append(user[1])
            last_names.append(user[2])
            user_names.append(user[3])
            pwd = user[4]
            if len(pwd) > 10:
                pwd = pwd[:10] + "..."
            passwords.append(pwd)
            designations.append(user[5])
        # print(designations)
        users_length = len(first_names)
        index = 0
        while index < users_length:
            _users['first_names'][index] = first_names[index]
            _users['last_names'][index] = last_names[index]
            _users['user_names'][index] = user_names[index]
            _users['passwords'][index] = passwords[index]
            _users['designations'][index] = designations[index]

            index += 1

        return _users

    def get_products(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        mycursor = mydb.cursor()
        _stocks = OrderedDict()
        _stocks['product_code'] = {}
        _stocks['product_name'] = {}
        _stocks['product_weight'] = {}
        _stocks['in_stock'] = {}
        _stocks['sold'] = {}
        _stocks['order'] = {}
        _stocks['last_purchase'] = {}

        product_code = []
        product_name = []
        product_weight = []
        in_stock = []
        sold = []
        order = []
        last_purchase = []
        sql = 'SELECT * FROM stocks'
        mycursor.execute(sql)
        products = mycursor.fetchall()
        for product in products:
            product_code.append(product[1])
            name = product[2]
            if len(name) > 10:
                name = name[:10] + "..."
            product_name.append(name)
            product_weight.append(product[3])
            in_stock.append(product[5])
            try:
                sold.append(product[6])
            except KeyError:
                sold.append('')
            try:
                order.append(product[7])
            except KeyError:
                order.append('')
            try:
                last_purchase.append(product[8])
            except KeyError:
                last_purchase.append('')
        # print(designations)
        products_length = len(product_code)
        index = 0
        while index < products_length:
            _stocks['product_code'][index] = product_code[index]
            _stocks['product_name'][index] = product_name[index]
            _stocks['product_weight'][index] = product_weight[index]
            _stocks['in_stock'][index] = in_stock[index]
            _stocks['sold'][index] = sold[index]
            _stocks['order'][index] = order[index]
            _stocks['last_purchase'][index] = last_purchase[index]

            index += 1

        return _stocks

    def view_stats(self):
        plt.cla()
        self.ids.analysis_res.clear_widgets()
        target_product = self.ids.target_product.text
        target = target_product[:target_product.find(' | ')]
        name = target_product[target_product.find(' | '):]

        df = pd.read_csv('admin/products_purchase.csv')
        purchases = []
        dates = []
        count = 0
        for x in range(len(df)):
            if str(df.Product_Code[x]) == target:
                purchases.append(df.Purchased[x])
                dates.append(count)
                count += 1
        plt.bar(dates, purchases, color='teal', label=name)
        plt.ylabel('Total Purchases')
        plt.xlabel('day')

        self.ids.analysis_res.add_widget(FCK(plt.gcf()))

    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'
        elif instance.text == "Manage Users":
            self.ids.scrn_mngr.current = 'scrn_content'
        else:
            self.ids.scrn_mngr.current = 'scrn_analysis'

    def close_app(self, obj):
        App.get_running_app().stop()
        Window.close()

    def log_out(self):
        self.parent.parent.current = "scrn_si"
        self.ids.file_dropdown.dismiss()

class AdminApp(App):
    def build(self):
        return AdminWindow()


if __name__ == "__main__":
    AdminApp().run()
