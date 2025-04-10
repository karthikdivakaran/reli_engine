from PyQt5 import uic
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QMessageBox, QPushButton
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QIcon
from database.db_connection import get_connection
from models.component.create_comp import ComponentCreateWindow


class ComponentsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi("gui/component/components.ui", self)  # Load the .ui file for the GUI
        self.main_window = main_window
        self.data = []

        # Find GUI elements defined in the .ui file
        self.table = self.findChild(QWidget, "tableView")  # The QTableView
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.createButton = self.findChild(QPushButton, "createComp")  # "Create" button

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action

        if self.createButton:
            self.createButton.clicked.connect(self.handle_create)

        # Load and display initial data
        self.refresh_components()  # Populate the table when the window is opened

    def refresh_components(self):
        # Fetch updated data from the database
        self.data = self.get_all_components()

        # Prepare data with an extra column for buttons
        headers = list(self.data[0].keys()) if self.data else []
        if headers:
            headers.append("")
            headers.append("")
        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Populate table
        for row, entry in enumerate(self.data):
            for col, key in enumerate(entry):
                self.table.setItem(row, col, QTableWidgetItem(str(entry[key])))

            # Edit button (✏️)
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("static/icons/icons-edit.png"))
            # edit_button.setObjectName("editBtn")
            edit_button.setFixedSize(24, 24)
            edit_button.setStyleSheet("border: none; padding: 0px; background-color: #fff;")
            edit_button.clicked.connect(lambda _, r=row: self.on_edit_click(r))
            self.table.setCellWidget(row, len(entry), edit_button)

            # Delete button (🗑️)
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("static/icons/icons-delete.png"))
            delete_button.setFixedSize(24, 24)
            delete_button.setObjectName("editBtn")
            delete_button.setStyleSheet("border: none; padding: 0px; background-color: #fff;")
            delete_button.clicked.connect(lambda _, r=row: self.confirm_delete(r))  # FIXED LAMBDA ISSUE
            self.table.setCellWidget(row, len(entry) + 1, delete_button)

            # Configure headers for better appearance
            header = self.table.horizontalHeader()
            # header.setSectionResizeMode(0, header.ResizeToContents)
            header.setSectionResizeMode(1, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(2, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(3, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(4, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(6, header.Stretch)  # Stretch the last column

    def handle_create(self):
        # Navigate to the Components Create Window
        self.second_window = ComponentCreateWindow(self)  # Pass self as reference
        self.second_window.show()
        self.hide()

    def goBack(self):
        self.close()  # Close the Components window
        self.main_window.show()  # Show the main window

    @staticmethod
    def get_all_components():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM components")
        columns = [desc[0] for desc in cursor.description]
        components = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return components

    def on_edit_click(self, row):
        print(f"Edit button clicked on row {row}")
        self.second_window = ComponentCreateWindow(self, self.data[row])  # Pass self as reference
        self.second_window.show()
        self.hide()

    def confirm_delete(self, row):
        """ Show confirmation dialog before deleting a row """
        msg = QMessageBox(self)  # Ensure it has a parent
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirm Delete")
        msg.setText(f"Are you sure you want to delete row {row + 1}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        result = msg.exec_()  # Properly show dialog

        if result == QMessageBox.Yes:
            self.on_delete_click(row)

    def on_delete_click(self, row):
        """ Remove the row from the table """
        try:
            self.delete_project(self.data[row]['componentid'])
            print(f"Row {row} deleted {self.data[row]['componentid']}")
            self.refresh_components()
        except Exception as e:
            print(f"Error deleting row {row}: {e}")

    def delete_project(self, comp_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM components WHERE componentid = ?", (comp_id,))
        conn.commit()
        conn.close()

