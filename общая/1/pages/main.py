from PyQt5.QtWidgets import QApplication, QDialog, QStackedWidget, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.uic import loadUi
import sys
import sqlite3


class MyApp(QDialog):
    def __init__(self):
        super(MyApp, self).__init__()
        loadUi('../views/dialog.ui', self)
        self.connect = sqlite3.connect("../uchet.db")
        self.clientID = None
        self.cursor = self.connect.cursor()

        self.stacedWidget = self.findChild(QStackedWidget, "stackedWidget")
        self.stacedWidget.setCurrentIndex(5)
        
        self.loginFiled = self.findChild(QLineEdit, "lineEdit")
        self.passwordFiled = self.findChild(QLineEdit, "lineEdit_2")
        
        self.lognButton = self.findChild(QPushButton, "pushButton")

        self.lognButton.clicked.connect(self.login)

        self.errorFiled = self.findChild(QLabel, "error")

        self.createButton = self.findChild(QPushButton, "pushButton_2")
        self.createButton.clicked.connect(lambda: self.stacedWidget.setCurrentIndex(4) if self.clientID else self.errorFiled.setText('Вы не авторизованны'))
        self.backButton = self.findChild(QPushButton, "pushButton_3")
        self.backButton.clicked.connect(lambda: [self.stacedWidget.setCurrentIndex(5), setattr(self, 'clientID', None)])
        self.saveButtn = self.findChild(QPushButton, "saveButton")
        self.saveButtn.clicked.connect(self.add)

        self.operTable = self.findChild(QTableWidget, 'tableWidget_4')
        self.managerTable = self.findChild(QTableWidget, 'tableWidget')
        self.masterTable = self.findChild(QTableWidget, 'tableWidget_3')
        self.zakTable = self.findChild(QTableWidget, 'tableWidget_2')

        self.startdate = self.findChild(QLineEdit, "lineEdit_3")
        self.orgTechType = self.findChild(QLineEdit, "lineEdit_4")
        self.orgTechModel = self.findChild(QLineEdit, "lineEdit_10")
        self.problemDescryption = self.findChild(QLineEdit, "lineEdit_11")
        self.requeststatusID = self.findChild(QLineEdit, "lineEdit_5")
        self.completionDate = self.findChild(QLineEdit, "lineEdit_6")
        self.repairParts = self.findChild(QLineEdit, "lineEdit_12")
        self.masterID = self.findChild(QLineEdit, "lineEdit_7")
        self.client_ID = self.findChild(QLineEdit, "lineEdit_9")

        

    def login(self):
        loginText = self.loginFiled.text()
        passText = self.passwordFiled.text()
        
        self.cursor.execute("SELECT * FROM users WHERE login = ?", (loginText,))
        result = self.cursor.fetchone()
        print(result)
        
        if result is None:
            self.errorFiled.setText('Пользователь не найдет!')
        else:
            rusultPass = result[-2]
            self.clientID = result[0]
            rusultRole = result[-1]

            if rusultPass == passText:
                self.errorFiled.setText("")
                if rusultRole == 1:
                    self.stacedWidget.setCurrentIndex(0)
                    self.loadDate (self.clientID, self.managerTable)
                elif rusultRole == 2:
                    self.stacedWidget.setCurrentIndex(3)
                    self.loadDate (self.clientID, self.masterTable)
                elif rusultRole == 3:
                    self.stacedWidget.setCurrentIndex(1)
                    self.loadDate (self.clientID, self.operTable)
            else:
                self.errorFiled.setText('Неверный пароль!')
    def loadDate(self, client_ID, table):
        try:
            req = self.cursor.execute('''SELECT
                                        r.IDrequest as "Номер заявки",
                                        r.startDate as "Дата начала",
                                        ot.orgTechType as "Код клиента",
                                        r.orgTechModel as "Дата создания",
                                        r.problemDescryption as "Время заказа",
                                        rs.requestStatus as "Статус заявки",
                                        r.completionDate as "Дата завершения аренды",
                                        r.repairParts as "Время в минутах",
                                        u.fio as "ФИО кончультанта",
                                        c.fio as "ФИО клиента"
                                    FROM requests 
                                    LEFT JOIN orgTechTypes ot on r.orgTechTypeID = ot.orgTechType
                                    LEFT JOIN requestStatuses rs on r.requestStatusID = rs.IDrequestStatus
                                    LEFT JOIN users u on r.masterID = u.IDuser
                                    LEFT JOIN users c on r.clientID = c.IDuser
                                    WHERE r.clientID = ?''', (client_ID,))

            headers = [column[0] for column in req.description]  
            table.setColumnCount(len(headers))  
            table.setHorizontalHeaderLabels(headers)  

            data = req.fetchall()  
            table.setRowCount(0)  
            for i, row in enumerate(data):  
                table.insertRow(i)
                for l, cow in enumerate(row):
                    table.setItem(i, l, QTableWidgetItem(str(cow)))
            table.resizeColumnsToContents()  
        except sqlite3.Error as e:  
            self.errorFiled.setText(f"Ошибка базы данных: {e}")
            print(f"Database error: {e}")

    def add(self):
        if self.clientID:
            date = self.startdate.text()
            orgTechType = self.orgTechType.text()
            orgTechModel = self.orgTechModel.text()
            problemDescryption = self.problemDescryption.text()
            requestStatusID = self.requeststatusID.text()
            completionDate = self.completionDate.text()
            repairParts = self.repairParts.text()
            masterID = self.masterID.text()
            clientID = self.client_ID.text()

            if not all([date, orgTechType, orgTechModel, problemDescryption, requestStatusID, masterID, clientID]):
                print("Ошибка: Одно или несколько полей не заполнены.")
                return
            
            try:
                orgTechType = int(orgTechType)
                requestStatusID = int(requestStatusID)
                masterID = int(masterID)
                clientID = int(clientID)
            except ValueError:
                print("Ошибка: поля orgTechType, orgTechModel, problemDescryption, requestStatusID, masterID и clientID должны быть числами.")
                return

            try:
                self.cursor.execute(
                    '''INSERT INTO requests
                    (startDate, orgTechTypeID, orgTechModel, problemDescryption, requestStatusID, completionDate, repairParts, masterID, clientID)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (date, orgTechType, orgTechModel, problemDescryption, requestStatusID, completionDate, repairParts, masterID, clientID))
                self.connect.commit()

                last_id = self.cursor.lastrowid

                print("Добавлена запись!")
            except sqlite3.Error as e:
                print(f"ошибка: {e}")
            
        else:
            self.errorFiled.setText("Вы не авторизованны")
        

            



            
        



    
        
    






app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec_())