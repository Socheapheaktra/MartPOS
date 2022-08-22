from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.config import Config

import re
import mysql.connector

Builder.load_file('userinterface/userinterface.kv')

class UserInterfaceWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd="1234"'',
            database='pos'
        )
        self.mycursor = self.mydb.cursor()

        self.cart = []
        self.qty = []
        self.total = 0.00

    def checkOut(self):
        self.ids.products.clear_widgets()
        self.ids.receipt_preview.text = 'The Collector\n123 Main St\Knowhere, Space\n\nTel: (+855)92 605-441\nReceipt No: \nDate: \n\n'
        self.ids.cur_product.text = 'Default Product'
        self.ids.cur_price.text = '0.00'
        self.ids.code_inp.text = ''

    def update_purchases(self):
        pcode = self.ids.code_inp.text
        products_container = self.ids.products

        sql = 'SELECT * FROM stocks WHERE product_code=%s'
        values = [pcode]
        self.mycursor.execute(sql, values)
        target_code = self.mycursor.fetchall()
        if target_code is None:
            pass
        else:
            for x in target_code:
                product_code = x[1]
                product_name = x[2]
                product_weight = x[3]
                product_price = x[4]
            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)
            code = Label(text=pcode, size_hint_x=.25, color=(.06, .45, .45, 1))
            name = Label(text=str(product_name), size_hint_x=.3, color=(.06, .45, .45, 1))
            qty = Label(text="1", size_hint_x=.1, color=(.06, .45, .45, 1))
            disc = Label(text="$ 0.00", size_hint_x=.1, color=(.06, .45, .45, 1))
            price = Label(text=("$ " + str(product_price)), size_hint_x=.1, color=(.06, .45, .45, 1))
            total = Label(text=("$ " + str(product_price + self.total)), size_hint_x=.15, color=(.06, .45, .45, 1))
            details.add_widget(code)
            details.add_widget(name)
            details.add_widget(qty)
            details.add_widget(disc)
            details.add_widget(price)
            details.add_widget(total)

            #Update Preview
            pname = str(product_name)

            pprice = product_price
            pqty = str(1)
            self.total += pprice
            purchase_total = '`\n\nTotal\t\t\t\t\t\t\t\t' + "$ " + str(self.total)
            self.ids.cur_product.text = pname
            self.ids.cur_price.text = ("$ " + str(pprice))
            preview = self.ids.receipt_preview
            prev_text = preview.text
            _prev = prev_text.find('`')
            if _prev > 0:
                prev_text = prev_text[:_prev]
            ptarget = -1
            for i, c in enumerate(self.cart):
                if c == pcode:
                    ptarget = i
            if ptarget >= 0:
                pqty = self.qty[ptarget]+1
                self.qty[ptarget] = pqty
                expr = '%s\t\tx\d\t'%(pname)
                rexpr = pname + '\t\tx' + str(pqty) + '\t'
                nu_text = re.sub(expr, rexpr, prev_text)
                preview.text = nu_text + purchase_total
            else:
                self.cart.append(pcode)
                self.qty.append(1)
                nu_preview = '\n'.join([prev_text, pname + '\t\tx' + pqty + '\t\t' + "$ " + str(pprice), purchase_total])
                preview.text = nu_preview

    def log_out(self):
        self.parent.parent.current = "scrn_si"
        self.ids.file_dropdown.dismiss()

class UserInterfaceApp(App):
    def build(self):
        return UserInterfaceWindow()

if __name__ == "__main__":
    ui = UserInterfaceApp()
    ui.run()