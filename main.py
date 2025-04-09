import sys
from PyQt5 import QtWidgets, uic
from database.db_connection import get_connection  # Assume this function connects to your DB
# from main_page import MainWindow  # Import the MainWindow for home
from main_page import MainWindow
from utils import utils
from controllers import home_controller
from session import Session


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        # Load the UI file
        uic.loadUi("gui/login.ui", self)

        # Connect the login button to the handler
        self.loginButton = self.findChild(QtWidgets.QPushButton, "loginButton")  # Adjust the button name
        self.singupButton = self.findChild(QtWidgets.QPushButton, "registerButton")  # Adjust the button name
        self.usernameInput = self.findChild(QtWidgets.QLineEdit, "uemailID")  # Adjust the field name
        self.passwordInput = self.findChild(QtWidgets.QLineEdit, "uPassword")  # Adjust the field name
        self.loginButton.clicked.connect(self.handle_login)
        self.singupButton.clicked.connect(self.handle_signup)

    def handle_signup(self):
        home_controller.handle_singup_btn(self)

    def handle_login(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        # Validate the inputs
        # if not username or not password:
        #     QtWidgets.QMessageBox.warning(self, "Login Failed", "Username and password cannot be empty.")
        #     return

        # self.home_window = MainWindow(self)
        # self.home_window.show()
        # self.close()  # Close the login window

        # Check the database for user credentials
        if self.validate_user(username, password):
            # Login successful - Open home window
            self.home_window = MainWindow(self)
            self.home_window.show()
            self.close()  # Close the login window
        else:
            # Login failed - Show error message
            QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    @staticmethod
    def validate_user(username, password):
        """
        Query the User table to validate username and password.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT UserID, Name, Email, Role FROM User WHERE Email = ? AND Password = ?"
            cursor.execute(query, (username, password))
            columns = [desc[0] for desc in cursor.description]
            users = [dict(zip(columns, row)) for row in cursor.fetchall()]
            if users:
                Session().set_user(users[0])
            conn.close()
            return bool(users)  # True if user exists, False otherwise
        except Exception as e:
            print(f"Error validating user: {e}")
            return False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    stylesheet = utils.load_stylesheet("styles/style.qss")
    app.setStyleSheet(stylesheet)
    # Start with LoginWindow
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
