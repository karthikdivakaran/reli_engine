import sys
from PyQt5 import QtWidgets, uic
from controllers import home_controller
# from main import LoginWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        # super(MainWindow, self).__init__()
        # Load the UI file
        uic.loadUi("gui/home.ui", self)
        self.main_window = main_window
        # Example: Connect a button clicked signal
        self.projectsBtn.clicked.connect(self.handle_project_click)
        self.componentBtn.clicked.connect(self.handle_component_click)
        self.calculationBtn.clicked.connect(self.handle_calculation_eng)
        self.userManagementBtn.clicked.connect(self.handle_users)

    def handle_project_click(self):
        home_controller.handle_project_btn(self)

    def handle_component_click(self):
        home_controller.handle_component_btn(self)

    def handle_calculation_eng(self):
        home_controller.handle_calc_btn(self)

    def handle_users(self):
        home_controller.handle_users_btn(self)


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

