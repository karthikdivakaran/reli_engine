from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QStyledItemDelegate, QPushButton, QMainWindow, QStyleOptionButton, QStyle
from database.db_connection import get_connection

class ProjectCreateWindow(QWidget):
    def __init__(self, prev_window):
        super().__init__()
        uic.loadUi("gui/project/create_project.ui", self)  # Load the .ui file for the GUI
        self.prev_window = prev_window

        # Find GUI elements defined in the .ui file
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.submitButton = self.findChild(QPushButton, "submitBtn")

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action

        if self.submitButton:
            self.submitButton.clicked.connect(self.handle_submit)

    def goBack(self):
        self.prev_window.refresh_projects()  # Refresh the ProjectsWindow data
        self.close()  # Close the Create Project window
        self.prev_window.show()  # Show the ProjectsWindow

    def handle_submit(self):
        project_name = self.projectName.text()
        description = self.description.toPlainText()
        user_id = 1  # Example ID, replace with actual logic

        # Insert the project into the database
        self.create_project(project_name, description, user_id)

        # Refresh ProjectsWindow and go back
        self.goBack()

    @staticmethod
    def create_project(project_name, description, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Project (ProjectName, Description, CreatedDate, LastModified , UserID) VALUES (?, ?, datetime('now'), datetime('now'), ?)",
            (project_name, description, user_id))
        conn.commit()
        conn.close()
