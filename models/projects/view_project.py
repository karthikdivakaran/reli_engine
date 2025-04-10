import json

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QIcon
from database.db_connection import get_connection
from session import Session

class ProjectViewWindow(QWidget):
    def __init__(self, prev_window, main_window, row=None):
        super().__init__()
        uic.loadUi("gui/project/view_project.ui", self)  # Load the .ui file for the GUI
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
        self.row = row
        if row:
            result = self.get_project()
            self.projectName.setText(row["ProjectName"])
            self.projectDescription.setText(row["Description"])
            if result:
                try:
                    result = json.loads(result)
                    self.formula.setText(result['formula'])
                    self.refresh_data(result)
                except:
                    pass
    def refresh_data(self, result):
        count = 1
        items = []
        for item in result['values']:
            self.findChild(QLabel, f"compval_{count}").setText(f"{item} = {result['values'][item]['value']}")
            if "deps" in result['values'][item]:
                for key_item in result['values'][item]['deps']:
                    if key_item not in items:
                        count += 1
                        items.append(key_item)
                        self.findChild(QLabel, f"compval_{count}").setText(f"{key_item} = {result['values'][item]['deps'][key_item]}")
            count += 1

        equation_values = "λ = "
        for item in result["values"]:
            if equation_values != "λ = ":
                equation_values += " * "
            equation_values += f"{result['values'][item]['value']}"
        self.findChild(QLabel, f"compval_{count}").setText(equation_values)
        count += 1
        try:
            self.findChild(QLabel, f"compval_{count}").setText(f"λ = {eval(equation_values.split('λ = ')[-1].strip())}")
        except:
            self.resultValue.setText(f" Please verify all options are selected correctly")
        print(result)
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

    def handle_submit(self):
        project_name = self.projectName.text()
        description = self.description.toPlainText()
        user_id = 1  # Example ID, replace with actual logic

        # Insert the project into the database
        if self.row:
            self.update_project(project_name, description, self.row['ProjectID'])
        else:
            self.create_project(project_name, description)

        # Refresh ProjectsWindow and go back
        self.goBack()

    def get_project(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Project WHERE ProjectID = ?", (self.row['ProjectID'],))
        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if projects:
            return projects[0]['Results']
        return None

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
        conn.commit()
        conn.close()

    def update_project(self, project_name, description, project_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Project SET ProjectName = ?, Description = ? WHERE UserID = ? and ProjectID = ?",
            (project_name, description, self.user["UserID"], project_id))
        conn.commit()
        conn.close()
