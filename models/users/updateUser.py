import re

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox

from database.db_connection import get_connection


class UpdateUserWindow(QWidget):
    def __init__(self, prev_window, user_data):
        super().__init__()
        uic.loadUi("gui/user_management/updateUser.ui", self)  # Load the .ui file for updating user
        self.prev_window = prev_window
        self.user_data = user_data
        # Find GUI elements defined in the .ui file
        self.updateUserBtn = self.findChild(QPushButton, "updateUserButton")

        # Find and populate GUI elements with user data
        self.userName = self.findChild(QWidget, "userName")
        self.userPwd = self.findChild(QWidget, "userPwd")
        self.emailID = self.findChild(QWidget, "emailID")
        self.roleField = self.findChild(QWidget, "roleField")
        self.userRolecombo = self.findChild(QWidget, "userRolecombo")

        # Preload data into text fields
        self.userName.setText(user_data.get("Name", ""))
        self.userPwd.setText(user_data.get("Password", ""))
        self.emailID.setText(user_data.get("Email", ""))
        # self.userRolecombo.setItemText(0, user_data.get("Role", ""))
        self.populateRolesComboBox()
        self.userRolecombo.setCurrentText(user_data.get("Role", ""))

        if self.updateUserBtn:
            self.updateUserBtn.clicked.connect(self.handle_updateUser)

    def goBack(self):
        # self.prev_window.refresh_projects()  # Refresh the ProjectsWindow data
        self.close()  # Close the Create Project window
        self.prev_window.refresh_users()
        self.prev_window.show()  # Show the ProjectsWindow

    def handle_updateUser(self):
        def is_valid_email(email):
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_regex, email)

        u_userid = self.user_data.get('UserID')
        u_name = self.userName.text()
        u_pwd = self.userPwd.text()
        u_emailid = self.emailID.text()

        # index = self.userRolecombo.currentIndex()
        # if index == 0:  # Index 0 is "Select a role"
        #     QMessageBox.warning(self, "Invalid Selection", "Please select a valid role.")
        #     self.userRolecombo.setCurrentIndex(0)  # Reset to no selection
        #     # self.handle_addUser
        if not u_name or not u_pwd or not u_emailid:
            QMessageBox.warning(self, "Invalid Input", "All fields must be filled out.")
        elif not is_valid_email(u_emailid):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
        else:

            # u_role = self.userRole.text()
            # userRolecombo = self.userRolecombo.text()
            userRolecombo_value = self.userRolecombo.currentText()
            # Insert the user details into the database
            self.update_user(u_userid, u_name, u_pwd, u_emailid, userRolecombo_value)
            self.goBack()

        # edit the below to add useres to user table

    def update_user(self, u_userid, u_name, u_pwd, u_emailid, userRolecombo_value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE User SET Name = ?, Email = ?, Password=?, Role = ? WHERE UserID = ?",
            (u_name, u_emailid, u_pwd, userRolecombo_value, u_userid))
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
        # # Set up Save and Cancel button actions
        # self.saveButton = self.findChild(QPushButton, "saveBtn")
        # self.cancelButton = self.findChild(QPushButton, "cancelBtn")


    #     if self.saveButton:
    #         self.saveButton.clicked.connect(self.save_user)  # Save changes
    #     if self.cancelButton:
    #         self.cancelButton.clicked.connect(self.cancel_update)  # Go back to user management window
    #
    # def save_user(self):
    #     # Retrieve updated data
    #     updated_name = self.nameField.text()
    #     updated_email = self.emailField.text()
    #     updated_role = self.roleField.text()
    #
    #     # Perform update in the database
    #     conn = get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("""
    #         UPDATE User
    #         SET name = %s, email = %s, role = %s
    #         WHERE id = %s
    #     """, (updated_name, updated_email, updated_role, self.user_data["id"]))
    #     conn.commit()
    #     conn.close()
    #
    #     # Refresh user management table
    #     self.prev_window.refresh_users()
    #     self.close()
    #     self.prev_window.show()
    #
    # def cancel_update(self):
    #     # Close the update window and return to the parent window
    #     self.close()
    #     self.prev_window.show()