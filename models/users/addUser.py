from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QStyledItemDelegate, QPushButton, QMainWindow, QStyleOptionButton, QStyle
from database.db_connection import get_connection


class addUserWindow(QWidget):
    def __init__(self, prev_window):
        super().__init__()
        uic.loadUi("gui/user_management/addUser.ui", self)  # Load the .ui file for the GUI
        self.prev_window = prev_window

        # Find GUI elements defined in the .ui file
        # self.viewUsers = self.findChild(QPushButton, "userID")  # The QTableView
        # self.goBackButton = self.findChild(QPushButton, "userName")  # "Back" button
        # self.addUser = self.findChild(QPushButton, "userpwd")  # "Create" button
        # self.updateUser = self.findChild(QPushButton, "emailID")
        # self.deleteUser = self.findChild(QPushButton, "userRole")
        self.addUserBtn = self.findChild(QPushButton, "addUserButton")
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action
        if self.addUserBtn:
            self.addUserBtn.clicked.connect(self.handle_addUser)

    def goBack(self):
        # self.prev_window.refresh_projects()  # Refresh the ProjectsWindow data
        self.close()  # Close the Create Project window
        self.prev_window.show()  # Show the ProjectsWindow

    def handle_addUser(self):

        u_name = self.userName.text()
        u_pwd = self.userpwd.text()
        u_emailid = self.emailID.text()
        u_role = self.userRole.text()
        # Insert the user details into the database
        self.create_user(u_name, u_pwd, u_emailid,u_role)
        self.goBack()

        #edit the below to add useres to user table
    # @staticmethod
    # def create_project(project_name, description, user_id):
    #     conn = get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         "INSERT INTO Project (ProjectName, Description, CreatedDate, LastModified , UserID) VALUES (?, ?, datetime('now'), datetime('now'), ?)",
    #         (project_name, description, user_id))
    #     conn.commit()
    #     conn.close()