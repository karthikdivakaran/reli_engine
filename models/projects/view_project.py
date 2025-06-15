import json
import math
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QIcon

import constants
from database.db_connection import get_connection
from session import Session
from utils import utils

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
        self.result = None
        if row:
            result = self.get_project()
            self.projectName.setText(row["ProjectName"])
            self.projectDescription.setText(row["Description"])
            if result:
                try:
                    result = json.loads(result)
                    self.formula.setText(result['formula'])
                    self.refresh_data(result)
                    self.result = result
                except:
                    pass
        if self.result:
            self.exportPdf.setIcon(QIcon("static/icons/pdf.png"))
            self.exportDoc.setIcon(QIcon("static/icons/word.png"))
            self.exportXls.setIcon(QIcon("static/icons/excel.png"))
            self.exportPdf.clicked.connect(self.export_result_to_pdf)
            self.exportDoc.clicked.connect(self.export_result_to_word)
            self.exportXls.clicked.connect(self.export_result_to_excel)
        else:
            self.exportPdf.setVisible(False)
            self.exportDoc.setVisible(False)
            self.exportXls.setVisible(False)

    def refresh_data(self, result):
        count = 1
        self.findChild(QLabel, f"compval_{count}").setText(f"Component   : {result['name']}")
        count += 1
        for item in result['additional_data']:
            for key in item:
                if key in ['name']:
                    continue
                if not item[key]:
                    continue
                self.findChild(QLabel, f"compval_{count}").setText(f"{key.capitalize()}   : {item[key]}")
                count += 1
        items = []
        if count %2 == 0:
            count += 1
        for item in result['values']:
            self.findChild(QLabel, f"compval_{count}").setText(f"{item} = {result['values'][item]['value']}")
            if "deps" in result['values'][item]:
                for key_item in result['values'][item]['deps']:
                    if key_item in ['type']:
                        continue
                    if key_item not in items:
                        count += 1
                        items.append(key_item)
                        key_item_val = key_item
                        if key_item in constants.key_map:
                            key_item_val = constants.key_map[key_item]
                        self.findChild(QLabel, f"compval_{count}").setText(f"{key_item_val} = {result['values'][item]['deps'][key_item]}")
            count += 1
        if count % 2 == 0:
            count += 1
        equation_values = "λ = "
        for item in result["values"]:
            if equation_values != "λ = ":
                equation_values += " * "
            equation_values += f"{result['values'][item]['value']}"
        self.findChild(QLabel, f"compval_{count}").setText(equation_values)
        count += 1
        if count % 2 == 0:
            count += 1
        lambda_val = 0
        try:
            lambda_val = eval(equation_values.split('λ = ')[-1].strip())
            self.findChild(QLabel, f"compval_{count}").setText(f"λ = {lambda_val} * 10\u207B\u2079")
        except:
            self.resultValue.setText(f" Please verify all options are selected correctly")
        duration_hr = result['duration']
        count += 1
        if count%2 ==0:
            count += 1
        self.findChild(QLabel, f"compval_{count}").setText("Reliability R(t) =  e^{-λt} ")
        count += 2
        self.findChild(QLabel, f"compval_{count}").setText(f"= e^{{-{lambda_val* (10 ** -9):.12f}*{duration_hr}}}")
        reliability = math.exp(-(lambda_val* (10 ** -9)) * float(duration_hr))
        count += 2
        self.findChild(QLabel, f"compval_{count}").setText(f" R(t) =  {reliability:.12f}")
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

    def export_result_to_pdf(self):
        print("Exporting result to file")
        utils.export_pdf(self.result, created_data=self.row["CreatedDate"], updated=self.row["LastModified"])
        utils.download_pdf(self)
    def export_result_to_word(self):
        utils.export_to_word(self.result, created_data=self.row["CreatedDate"], updated=self.row["LastModified"])
        utils.download_word(self)
    def export_result_to_excel(self):
        utils.export_excel(self.result, created_data=self.row["CreatedDate"], updated=self.row["LastModified"])
        utils.download_excel(self)

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
