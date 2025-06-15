import json
import math
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
from PyQt5.QtWidgets import (
    QWidget, QApplication, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit, QLabel, QHeaderView, QComboBox
)

import constants
from database.db_connection import get_connection
from session import Session
from utils import utils

class ComponentViewWindow(QWidget):
    def __init__(self, prev_window, main_window, row=None):
        super().__init__()
        uic.loadUi("gui/component/view_component.ui", self)  # Load the .ui file for the GUI
        self.prev_window = prev_window
        self.main_window = main_window
        self.user = Session().get_user()

        # Find GUI elements defined in the .ui file
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.submitButton = self.findChild(QPushButton, "submitBtn")
        self.homeButton = self.findChild(QPushButton, "homeBtn")
        if self.homeButton:
            self.homeBtn.setIcon(QIcon("static/icons/home.png"))
            self.homeButton.clicked.connect(self.handle_home)

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action

        if self.submitButton:
            self.submitButton.clicked.connect(self.handle_submit)
        self.row = row
        self.result = None
        self.valid_data = False

        self.saveButton = self.findChild(QPushButton, "nextBtm")
        if self.saveButton:
            self.saveButton.clicked.connect(self.save_table_data)

        self.env_values = self.get_depends_values()

        if row:
            self.label_2.setText(row["name"])
            pop_columns = ["theetta1", "theetta2"]
            for item in row["formula"].split("*"):
                if item.strip() not in ['λref']:
                    pop_columns.append(item.strip())
            pop_columns.extend(["env_variable", "env_value", "type"])
            # Connect + button
            col_keys = ["Name", "Type", "Reference", "Reference Failure Rate", "Reference Temperature",
                                     "Delete"]
            self.setup_table_layout(self.component_table, col_keys)
            self.setup_table_layout(self.tableView_2, pop_columns)

            self.addRowButton.clicked.connect(
                lambda: self.add_row_to_table(self.component_table, col_keys, first_column_value=self.row['name'])
            )
            self.addRowButton2.clicked.connect(lambda: self.add_row_to_table(self.tableView_2, pop_columns))

            result = self.get_components()
            keys = ['name', 'type', 'reference', 'λref', 'theetta1']
            self.populate_table_with_data(self.component_table, result, keys)
            data = self.get_env_values()

            self.populate_table_with_data(self.tableView_2, data, pop_columns)
        # else:
        #     # Connect + button
        #     self.setup_table_layout(self.component_table,
        #                             ["Name", "Type", "Reference", "Reference Failure Rate", "Reference Temperature",
        #                              "Delete"])
        #     self.setup_table_layout(self.tableView_2,
        #                             ["Ref Temp", "Optn Temp", "Pi_T", "Pi_U", "Pi_D", "Pi_Q", "Pi_L", "Pi_K", "Pi_E",
        #                              "Pi_S", "Pi_I", "env variable", "env value", "type"])
        #
        #     self.addRowButton.clicked.connect(
        #         lambda: self.add_row_to_table(self.component_table, 5, first_column_value=self.row['name'])
        #     )
        #     self.addRowButton2.clicked.connect(lambda: self.add_row_to_table(self.tableView_2, 14))

    def get_table_data(self, tableWidget: QTableWidget):
        table_data = []

        for row in range(tableWidget.rowCount()):
            row_data = {}
            for column in range(tableWidget.columnCount()):  # skip the last column if it's Delete
                header_item = tableWidget.horizontalHeaderItem(column)
                if not header_item:
                    continue
                header = header_item.text()

                widget = tableWidget.cellWidget(row, column)
                if isinstance(widget, QComboBox):
                    value = widget.currentText()
                elif isinstance(widget, QLineEdit):
                    value = widget.text()
                elif widget is not None:
                    value = widget.text() if hasattr(widget, 'text') else str(widget)
                else:
                    item = tableWidget.item(row, column)
                    value = item.text() if item else ""

                row_data[header] = value
            table_data.append(row_data)

        return table_data

    def save_table_data(self):
        print(self.row)

        json_data = self.get_table_data(self.component_table)
        print(json_data)  # or save to a file

        json_data2 = self.get_table_data(self.tableView_2)
        print(json_data2)

        if self.row and len(json_data) > 0  and len(json_data2) > 0:
            utils.append_to_json_file(self.row)

    def setup_table_layout(self, table_widget, column_keys):
        """
        Initializes column layout and header labels.
        """
        column_count = len(column_keys)
        table_widget.setColumnCount(column_count + 1)
        table_widget.setHorizontalHeaderLabels(column_keys + ["Delete"])
        table_widget.setRowCount(0)

        header = table_widget.horizontalHeader()

        for i in range(column_count):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(column_count, QHeaderView.ResizeToContents)

    def populate_table_with_data(self, table_widget, data_list, column_keys):
        self.setup_table_layout(table_widget, column_keys)

        for row_idx, item in enumerate(data_list):
            table_widget.insertRow(row_idx)

            for col_idx, key in enumerate(column_keys):
                value = item.get(key, "") if isinstance(item, dict) else getattr(item, key, "")

                if key == "env_variable":
                    combo = QComboBox()
                    combo.addItems(self.env_values)  # <- Replace with your values
                    if value:
                        index = combo.findText(str(value))
                        if index != -1:
                            combo.setCurrentIndex(index)
                    table_widget.setCellWidget(row_idx, col_idx, combo)
                else:
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() | Qt.ItemIsEditable)
                    table_widget.setItem(row_idx, col_idx, cell)

            # Add Delete button at the end
            btn = QPushButton("Delete")
            btn.clicked.connect(self.make_delete_handler(table_widget))
            table_widget.setCellWidget(row_idx, len(column_keys), btn)

    def make_delete_handler(self, table_widget):
        def handler():
            button = self.sender()
            if button:
                index = table_widget.indexAt(button.pos())
                if index.isValid():
                    table_widget.removeRow(index.row())

        return handler

    # def add_row_to_table(self, table_widget, column_count, first_column_value=None):
    def add_row_to_table(self, table_widget, column_keys, first_column_value=None):
        """
        Adds a new editable row with a Delete button at the end.
        Optionally pre-fills the first column with a value.
        """
        row_position = table_widget.rowCount()
        table_widget.insertRow(row_position)

        for col, key in enumerate(column_keys):
            if key == "env_variable":
                combo = QComboBox()
                combo.addItems(self.env_values)  # Customize your options here
                table_widget.setCellWidget(row_position, col, combo)
            else:
                item = QTableWidgetItem("")
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                if col == 0 and first_column_value is not None:
                    item.setText(str(first_column_value))
                table_widget.setItem(row_position, col, item)

        # Add Delete button at the last column
        btn = QPushButton("Delete")
        btn.clicked.connect(self.make_delete_handler(table_widget))
        table_widget.setCellWidget(row_position, len(column_keys), btn)

    def delete_row(self, row):
        self.component_table.removeRow(row)

    def refresh_data(self, result):
        count = 1
        self.findChild(QLabel, f"compval_{count}").setText(f"Component   : {result['name']}")
        count += 1
        for item in result['additional_data']:
            for key in item:
                if key in ['name']:
                    continue
                if not item[key]:
                    continue
                self.findChild(QLabel, f"compval_{count}").setText(f"{key.capitalize()}   : {item[key]}")
                count += 1
        items = []
        if count %2 == 0:
            count += 1
        for item in result['values']:
            self.findChild(QLabel, f"compval_{count}").setText(f"{item} = {result['values'][item]['value']}")
            if "deps" in result['values'][item]:
                for key_item in result['values'][item]['deps']:
                    if key_item in ['type']:
                        continue
                    if key_item not in items:
                        count += 1
                        items.append(key_item)
                        key_item_val = key_item
                        if key_item in constants.key_map:
                            key_item_val = constants.key_map[key_item]
                        self.findChild(QLabel, f"compval_{count}").setText(f"{key_item_val} = {result['values'][item]['deps'][key_item]}")
            count += 1
        if count % 2 == 0:
            count += 1
        equation_values = "λ = "
        for item in result["values"]:
            if equation_values != "λ = ":
                equation_values += " * "
            equation_values += f"{result['values'][item]['value']}"
        self.findChild(QLabel, f"compval_{count}").setText(equation_values)
        count += 1
        if count % 2 == 0:
            count += 1
        lambda_val = 0
        try:
            lambda_val = eval(equation_values.split('λ = ')[-1].strip())
            self.findChild(QLabel, f"compval_{count}").setText(f"λ = {lambda_val} * 10\u207B\u2079")
        except:
            self.resultValue.setText(f" Please verify all options are selected correctly")
        duration_hr = result['duration']
        count += 1
        if count%2 ==0:
            count += 1
        self.findChild(QLabel, f"compval_{count}").setText("Reliability R(t) =  e^{-λt} ")
        count += 2
        self.findChild(QLabel, f"compval_{count}").setText(f"= e^{{-{lambda_val* (10 ** -9):.12f}*{duration_hr}}}")
        reliability = math.exp(-(lambda_val* (10 ** -9)) * float(duration_hr))
        count += 2
        self.findChild(QLabel, f"compval_{count}").setText(f" R(t) =  {reliability:.12f}")
        print(result)
    def goBack(self):
        try:
            self.prev_window.refresh_projects()  # Refresh the ProjectsWindow data
        except:
            pass
        self.close()  # Close the Create Project window
        self.prev_window.show()  # Show the ProjectsWindow

    def handle_home(self):
        self.close()
        self.main_window.show()

    def handle_submit(self):
        project_name = self.projectName.text()
        description = self.description.toPlainText()
        user_id = 1  # Example ID, replace with actual logic

        # Insert the project into the database
        if self.row:
            self.update_project(project_name, description, self.row['ProjectID'])
        else:
            self.create_project(project_name, description)

        # Refresh ProjectsWindow and go back
        self.goBack()

    def get_components(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM components WHERE name = ?", (self.row['name'],))
        columns = [desc[0] for desc in cursor.description]
        components = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        # if projects:
        #     return projects[0]['Results']
        return components

    def get_env_values(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM env_factors WHERE component = ?", (self.row['name'],))
        columns = [desc[0] for desc in cursor.description]
        components = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        # if projects:
        #     return projects[0]['Results']
        return components

    def create_project(self, project_name, description):
        conn = get_connection()
        cursor = conn.cursor()
        if self.result:
            cursor.execute(
                "INSERT INTO Project (ProjectName, Description, CreatedDate, LastModified , UserID, Results)"
                "VALUES (?, ?, datetime('now'), datetime('now'), ?, ?)",
                (project_name, description, self.user["UserID"], json.dumps(self.result)))
        else:
            cursor.execute(
                "INSERT INTO Project (ProjectName, Description, CreatedDate, LastModified , UserID) VALUES (?, ?, datetime('now'), datetime('now'), ?)",
                (project_name, description, self.user["UserID"]))
        conn.commit()
        conn.close()

    def update_project(self, project_name, description, project_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Project SET ProjectName = ?, Description = ? WHERE UserID = ? and ProjectID = ?",
            (project_name, description, self.user["UserID"], project_id))
        conn.commit()
        conn.close()

    def get_depends_values(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM env_values")
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Map rows to dictionaries
        result_list = [dict(zip(column_names, comp)) for comp in results]
        conn.close()
        items = []
        for item in result_list:
            if item["value"] is not None and item["value"] not in items:
                items.append(item["value"])
        return items
