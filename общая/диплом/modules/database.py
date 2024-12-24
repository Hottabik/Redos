from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
import sqlite3


import sqlite3

class Model:
    def __init__(self) -> None:
        self.db = 'db.db'
        self.connection = self.connect()

    def connect(self):
        try:
            return sqlite3.connect(self.db)
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None
        
    def execute_query(self, query: str, *args, fetch_one: bool = False) -> any:
        """
        Выполняет запрос к базе данных.

        Параметры:
            query (str): SQL-запрос для выполнения.
            *args: Параметры для подстановки в запрос.
            fetch_one (bool): Нужно ли извлечь один результат.

        Возвращает:
            Первый столбец первой строки, если fetch_one равно True и результат существует; иначе None.
        """
        try:
            cursor = self.connection.cursor()
            data = cursor.execute(query, args)
            
            if fetch_one:
                result = data.fetchone()
                if result is not None:
                    return result
                else:
                    return None
            self.connection.commit()
            return data
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None
        

class showSelect(Model):
    def __init__(self):
        super().__init__()  # Наследуем функциональность выполнения запросов

    def showdata(self, table_widget, query):
        try:
            data = self.execute_query(query)
            
            col_names = [i[0] for i in data.description]
            data_rows = data.fetchall()

            table_widget.setColumnCount(len(col_names))
            table_widget.setHorizontalHeaderLabels(col_names)
            table_widget.setRowCount(0)

            for i, row in enumerate(data_rows):
                table_widget.setRowCount(table_widget.rowCount() + 1)
                for j, elem in enumerate(row):
                    table_widget.setItem(i, j, QTableWidgetItem(str(elem)))

            table_widget.resizeColumnsToContents()
            print("Столбцов:", len(col_names))
            return len(col_names)
        except Exception as e:
            print(f"Ошибка при отображении данных: {e}")
            return 0


