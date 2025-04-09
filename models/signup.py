import re

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QStyledItemDelegate, QPushButton, QMainWindow, QStyleOptionButton, \
    QStyle, QComboBox, QMessageBox
from database.db_connection import get_connection


class RegisterUserWindow(QMainWindow):
    def __init__(self, prev_window):
        super().__init__()
        uic.loadUi("gui/user_management/register_user.ui", self)  # Load the .ui file for the GUI
        self.prev_window = prev_window

        # Find GUI elements defined in the .ui file
        # self.viewUsers = self.findChild(QPushButton, "userID")  # The QTableView
        # self.goBackButton = self.findChild(QPushButton, "userName")  # "Back" button
        # self.addUser = self.findChild(QPushButton, "userpwd")  # "Create" button
        # self.updateUser = self.findChild(QPushButton, "emailID")
        # self.deleteUser = self.findChild(QPushButton, "userRole")
        self.addUserBtn = self.findChild(QPushButton, "addUserButton")
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button


        self.userRolecombo.setItemText(0, "Select a role")
        # self.userRolecombo.setItemData(0, 0)  # if True
        # self.userRolecombo.setItemData(0, 0, Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.populateRolesComboBox()
        self.userRolecombo.currentIndexChanged.connect(self.validate_combo_selection)

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action
        if self.addUserBtn:
            self.addUserBtn.clicked.connect(self.handle_addUser)


    def validate_combo_selection(self, index):
        if index == 0:  # Index 0 is "Select a role"
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid role.")
            self.userRolecombo.setCurrentIndex(0)  # Reset to no selection


    def goBack(self):
        # self.prev_window.refresh_projects()  # Refresh the ProjectsWindow data
        self.close()  # Close the Create Project window
        self.prev_window.show()  # Show the ProjectsWindow



    def handle_addUser(self):
        def is_valid_email(email):
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_regex, email)
        f_name = self.firstName.text()
        l_name = self.lastName.text()
        u_pwd = self.password.text()
        u_emailid = self.emailID.text()
        index = self.userRolecombo.currentIndex()
        if not f_name or not l_name or not u_pwd or not u_emailid:
            QMessageBox.warning(self, "Invalid Input", "All fields must be filled out.")
        elif index == 0:  # Index 0 is "Select a role"
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid role.")
            self.userRolecombo.setCurrentIndex(0)  # Reset to no selection
            # self.handle_addUser
        elif not is_valid_email(u_emailid):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
        else:
            u_name = f"{f_name} {l_name}"
            # u_role = self.userRole.text()
            # userRolecombo = self.userRolecombo.text()
            userRolecombo_value = self.userRolecombo.currentText()
            # Insert the user details into the database
            self.create_user(u_name, u_pwd, u_emailid, userRolecombo_value)
            self.goBack()

        # edit the below to add useres to user table

    @staticmethod
    def create_user(u_name, u_pwd, u_emailid, userRolecombo_value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO User (Name, Password, Email, Role) VALUES (?, ?, ?, ?)",
            (u_name, u_pwd, u_emailid, userRolecombo_value))
        conn.commit()
        conn.close()

    def populateRolesComboBox(self):
        # Connect to the database
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch data from the roles table
        cursor.execute("SELECT role_name FROM roles")
        rows = cursor.fetchall()

        # Add each role to the combo box
        for row in rows:
            self.userRolecombo.addItem(row[0])  # Assuming roles_name is in the first column

        # Close the connection
        conn.close()
