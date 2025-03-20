from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QStyledItemDelegate, QPushButton, QMainWindow, QStyleOptionButton, \
    QStyle, QTableWidgetItem, QMessageBox

from database.db_connection import get_connection
from models.users.addUser import addUserWindow
from models.users.updateUser import UpdateUserWindow


class UserManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi("gui/user_management/userManagementhome.ui", self)  # Load the .ui file for the GUI
        self.main_window = main_window

        # Find GUI elements defined in the .ui file

        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.addUserBtn = self.findChild(QPushButton, "addUserBtn")  # "Create" button
        self.table = self.findChild(QWidget, "tableView")  # The QTableView

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action
        if self.addUserBtn:
            self.addUserBtn.clicked.connect(self.addUserFunction)  # Connect go back button to close action

        # Load and display initial data
        self.refresh_users()  # Populate the table when the window is opened

    def refresh_users(self):
        self.data = self.get_all_users()
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
            edit_button.clicked.connect(lambda _, r=row: self.on_edit_click(r))
            self.table.setCellWidget(row, len(entry), edit_button)

            # Delete button (🗑️)
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("static/icons/icons-delete.png"))
            delete_button.clicked.connect(lambda _, r=row: self.confirm_delete(r))  # FIXED LAMBDA ISSUE
            self.table.setCellWidget(row, len(entry) + 1, delete_button)

    @staticmethod
    def get_all_users():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User")
        columns = [desc[0] for desc in cursor.description]
        users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return users

    def goBack(self):
        self.close()  # Close the Users window
        self.main_window.show()  # Show the main window

    #
    def addUserFunction(self):
        # Navigate to add users window
        self.second_window = addUserWindow(self)  # Pass self as reference
        self.second_window.show()
        self.hide()

    def on_edit_click(self, row):
        # Get the data of the selected row
        user_data = self.data[row]

        # Open the Update User window and pass the user_data
        self.update_window = UpdateUserWindow(self, user_data)
        self.update_window.show()
        self.hide()
# add reresh components and rename as refresh user here

    def confirm_delete(self, row):
        # Get the user ID or identifier of the selected row
        user_data = self.data[row]
        user_id = user_data.get("UserID")  # Assuming "id" is the unique identifier for the user

        # Show a confirmation dialog
        confirm_box = QMessageBox()
        confirm_box.setIcon(QMessageBox.Warning)
        confirm_box.setWindowTitle("Confirm Delete")
        confirm_box.setText("Are you sure you want to delete this user?")
        confirm_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = confirm_box.exec()

        if result == QMessageBox.Yes:
            # Perform deletion in the database
            print(type(user_id))
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM User WHERE UserID = ?", (user_id,))
                conn.commit()
                conn.close()

                # Remove the user from the table
                self.data.pop(row)
                self.refresh_users()

                # Show success message
                success_box = QMessageBox()
                success_box.setIcon(QMessageBox.Information)
                success_box.setWindowTitle("User Deleted")
                success_box.setText(f"User with ID {user_id} has been successfully deleted.")
                success_box.exec()
            except Exception as e:
                conn.close()

                # Show error message
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setWindowTitle("Error")
                error_box.setText(f"An error occurred: {str(e)}")
                error_box.exec()

