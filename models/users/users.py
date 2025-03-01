from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QStyledItemDelegate, QPushButton, QMainWindow, QStyleOptionButton, QStyle
from models.users.addUser import addUserWindow

class UserManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi("gui/user_management/userManagementhome.ui", self)  # Load the .ui file for the GUI
        self.main_window = main_window

        # Find GUI elements defined in the .ui file
        self.viewUsers = self.findChild(QPushButton, "viewUsersBtn")  # The QTableView
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.addUser = self.findChild(QPushButton, "addUserBtn")  # "Create" button
        self.updateUser = self.findChild(QPushButton, "updateUserBtn")
        self.deleteUser = self.findChild(QPushButton, "deleteUserBtn")

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action
        if self.addUser:
            self.addUser.clicked.connect(self.addUserFunction)  # Connect go back button to close action

    def goBack(self):
        self.close()  # Close the Projects window
        self.main_window.show()  # Show the main window

    def addUserFunction(self):
        #Navigate to add users window
        self.second_window = addUserWindow(self)  # Pass self as reference
        self.second_window.show()
        self.hide()