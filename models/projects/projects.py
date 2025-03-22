from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon
from database.db_connection import get_connection
from models.projects.project_create import ProjectCreateWindow


class ProjectsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi("gui/project/projects.ui", self)  # Load the .ui file for the GUI
        self.main_window = main_window
        self.data = []

        # Ensure table is a QTableWidget, not QTableView
        self.table = self.findChild(QTableWidget, "tableView")
        self.goBackButton = self.findChild(QPushButton, "backBtn")
        self.createButton = self.findChild(QPushButton, "createProject")

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)

        if self.createButton:
            self.createButton.clicked.connect(self.handle_create)

        # Load and display initial data
        self.refresh_projects()

    def refresh_projects(self):
        self.data = self.get_all_projects()
        headers = list(self.data[0].keys()) if self.data else []
        if headers:
            headers.append("")
            headers.append("")
        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Populate table
        for row, entry in enumerate(self.data):
            for col, key in enumerate(entry):
                self.table.setItem(row, col, QTableWidgetItem(str(entry[key])))

            # Edit button (✏️)
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("static/icons/icons-edit.png"))
            edit_button.clicked.connect(lambda _, r=row: self.on_edit_click(r))
            self.table.setCellWidget(row, len(entry), edit_button)

            # Delete button (🗑️)
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("static/icons/icons-delete.png"))
            delete_button.clicked.connect(lambda _, r=row: self.confirm_delete(r))  # FIXED LAMBDA ISSUE
            self.table.setCellWidget(row, len(entry) + 1, delete_button)

            # Configure headers for better appearance
            header = self.table.horizontalHeader()
            # header.setSectionResizeMode(0, header.ResizeToContents)
            header.setSectionResizeMode(1, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(2, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(3, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(4, header.Stretch)  # Stretch the last column
            header.setSectionResizeMode(6, header.Stretch)  # Stretch the last column

    def handle_create(self):
        self.second_window = ProjectCreateWindow(self)
        self.second_window.show()
        self.hide()

    def goBack(self):
        self.close()
        self.main_window.show()

    @staticmethod
    def get_all_projects():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Project")
        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return projects

    def on_edit_click(self, row):
        print(f"Edit button clicked on row {row}")

    def confirm_delete(self, row):
        """ Show confirmation dialog before deleting a row """
        msg = QMessageBox(self)  # Ensure it has a parent
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirm Delete")
        msg.setText(f"Are you sure you want to delete row {row + 1}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        result = msg.exec_()  # Properly show dialog

        if result == QMessageBox.Yes:
            self.on_delete_click(row)

    def on_delete_click(self, row):
        """ Remove the row from the table """
        try:
            self.delete_project(self.data[row]["ProjectID"])
            print(f"Row {row} deleted {self.data[row]['ProjectID']}")
            self.refresh_projects()
        except Exception as e:
            print(f"Error deleting row {row}: {e}")

    def delete_project(self, project_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Project WHERE ProjectID = ?", (project_id,))
        conn.commit()
        conn.close()

