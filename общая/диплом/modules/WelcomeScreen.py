#  widget - это имя, присваиваемое компоненту пользовательского интерфейса,
#  с которым пользователь может взаимодействовать 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (    
    QDialog, # это базовый класс диалогового окна
    QTableWidget
)
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QStackedWidget
from PyQt5.uic import loadUi # загрузка интерфейса, созданного в Qt Creator

import sqlite3
from datetime import date

from modules.Manager import Manager
from modules.database import showSelect


class WelcomeScreen(QDialog):
    """
    Это класс окна приветствия.
    """
    def __init__(self):
        """
        Это конструктор класса
        """
        super(WelcomeScreen, self).__init__()
        loadUi("views/welcomescreen.ui", self)  # загружаем интерфейс.
        self.model = showSelect()
        self.AvtorButton.clicked.connect(self.sign_out)
        self.AvtorButton.hide()
        self.stackedWidget.currentChanged.connect(self.hiddenButton)  
        self.PasswordField.setEchoMode(QLineEdit.Password)  # скрываем пароль
        self.SignInButton.clicked.connect(self.check_user)  # нажатие на кнопку и вызов функции

        self.insert_button.clicked.connect(self.insert)  # нажатие на кнопку и вызов функци



        self.pages = {
            1: {
                'select':''
            },
            2:{
            'buttons': False,
            'select':"""SELECT 
                o.id AS "ID_заказа",
                o.order_date AS "Дата_заказа",
                o.total_price AS "Общая_цена",
                o.status AS "Статус_заказа",
                a.address AS "Адрес",
                a.city AS "Город",
                a.postal_code AS "Почтовый_индекс",
                p.id AS "ID_товара",
                p.name AS "Название_товара",
                p.description AS "Описание_товара",
                p.price AS "Цена_товара",
                p.image_url AS "Изображение_товара",
                c.id AS "ID_категории",
                c.name AS "Название_категории",
                oi.quantity AS "Количество",
                oi.price AS "Цена_позиции"
            FROM 
                Orders o
            JOIN 
                Addresses a ON o.address_id = a.id
            JOIN 
                Order_Items oi ON o.id = oi.order_id
            JOIN 
                Products p ON oi.product_id = p.id
            JOIN 
                Categories c ON p.category_id = c.id

       """},
       3: {
           'buttons': True,
           'select': 'select * from Products',
           'insert': 'insert into Products (id, name, description, price, category_id, image_url) values (?,?,?,?,?,?)'
       }
}   


    def hiddenButton(self):
        if self.stackedWidget.currentWidget() == self.Avtorisation:  
            self.AvtorButton.hide()
        else:
            self.AvtorButton.show()
        
        
    def sign_out(self):
        self.stackedWidget.setCurrentWidget(self.Avtorisation)
        
    def signupfunction(self): # создаем функцию регистрации        
        user = self.LoginField.text() # создаем пользователя и получаем из поля ввода логина введенный текст
        password = self.PasswordField.text() # создаем пароль и получаем из поля ввода пароля введенный текст
        return user, password # выводит логин и пароль       
    
    def hide_label(self, count):
        line_edits = []
        # Проходим по всем элементам в QVBoxLayout
        for i in range(self.verticalLayout_3.count()):
            item = self.verticalLayout_3.itemAt(i)
            widget = item.widget()
            widget.hide()
            
            # Проверяем, является ли виджет QLineEdit
            if isinstance(widget, QLineEdit):
                line_edits.append(widget)
        # Теперь line_edits содержит список всех QLineEdit в QVBoxLayout
        self.lines = line_edits[count:]
        for i in line_edits[count:]:
            i.show()

    def hide_buttons(self, role):
        button_edits = []
        
        # Проходим по всем элементам в QVBoxLayout
        for i in range(self.verticalLayout_2.count()):
            item = self.verticalLayout_2.itemAt(i)
            widget = item.widget()
            
            # Проверяем, является ли виджет QPushButton
            if isinstance(widget, QPushButton):
                button_edits.append(widget)
        
        # Если role == True, показываем все кнопки
        if role:
            for button in button_edits:
                button.show()
        # Если role == False, скрываем все кнопки
        else:
            for button in button_edits:
                button.hide()

    def check_user(self):
        try:
            user, password = self.signupfunction()
            print(user, password)
            if len(user)==0 or len(password)==0: # если пользователь оставил пустые поля
                self.ErrorField.setText("Заполните все поля") # выводим ошибку в поле
            else:
                self.ErrorField.setText(" ") # выводим ошибку в поле
                
                self.typeUser = self.model.execute_query('SELECT role FROM Users WHERE email=(?) and password=(?)', user, password, fetch_one=True) # получаем тип пользователя, логин и пароль которого был введен
                self.typeUser = self.typeUser[0] # получает только один тип пользователя
                print(self.typeUser)
                if self.typeUser == None:
                    self.ErrorField.setText("Пользователь с такими данными не найден")              
                else:    
                    cols = self.model.showdata(self.tableMasteraZayavki, query=self.pages[self.typeUser]['select'])
                    self.stackedWidget.setCurrentWidget(self.user)
                    self.hide_buttons(self.pages[self.typeUser]['buttons'])
                    if self.typeUser == 2:
                        self.hide_label(16)
                    else:
                        self.hide_label(11-cols)
                
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None

    def insert(self):
   
        values = [i.text() for i in self.lines]

        self.model.execute_query(self.pages[self.typeUser]['insert'], *values)
        self.model.showdata(self.tableMasteraZayavki, query=self.pages[self.typeUser]['select']) 