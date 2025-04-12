import json

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, QPushButton, QMainWindow, QStyleOptionButton, QStyle
from PyQt5.QtGui import QIcon
from database.db_connection import get_connection
from controllers import home_controller
from session import Session
from utils import utils

class ProjectCreateWindow(QWidget):
    def __init__(self, prev_window, main_window, row=None, result=None):
        super().__init__()
        uic.loadUi("gui/project/create_project.ui", self)  # Load the .ui file for the GUI
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
        self.calculateFailure.clicked.connect(self.handle_calculate)
        self.row = row
        self.result = result
        if row:
            self.projectName.setText(row["ProjectName"])
            self.description.setPlainText(row["Description"])
            self.submitButton.setText("Update Project")

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

    def handle_calculate(self):
        print("clicked")
        if self.row:
            project_details = self.get_project_details(self.row['ProjectID'])
            try:
                results = json.loads(project_details['Results'])
            except:
                results = {}
            home_controller.handle_calc_btn(self, self.main_window, self.row, results)
        else:
            project_name = self.projectName.text()
            description = self.description.toPlainText()
            if project_name and description:
                data = self.create_project(project_name, description)
                home_controller.handle_calc_btn(self, self.main_window, data['ProjectID'])
            else:
                utils.confirm_delete(self, "Error", f"Please Fill All Fields")


    def handle_submit(self):
        project_name = self.projectName.text()
        description = self.description.toPlainText()

        # Insert the project into the database
        if self.row:
            self.update_project(project_name, description, self.row['ProjectID'])
        else:
            self.create_project(project_name, description)

        # Refresh ProjectsWindow and go back
        self.goBack()

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
        # Get the ID of the inserted row
        inserted_id = cursor.lastrowid

        # Now fetch the inserted row
        cursor.execute("SELECT * FROM Project WHERE ProjectID = ?", (inserted_id,))
        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.commit()
        conn.close()
        return projects[0]

    def update_project(self, project_name, description, project_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Project SET ProjectName = ?, Description = ? WHERE UserID = ? and ProjectID = ?",
            (project_name, description, self.user["UserID"], project_id))
        conn.commit()
        conn.close()

    def get_project_details(self, project_id):
        conn = get_connection()
        cursor = conn.cursor()
        # Now fetch the inserted row
        cursor.execute("SELECT * FROM Project WHERE ProjectID = ?", (project_id,))
        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.commit()
        conn.close()
        return projects[0]
