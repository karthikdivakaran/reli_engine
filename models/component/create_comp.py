from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton
from database.db_connection import get_connection

class ComponentCreateWindow(QWidget):
    def __init__(self, prev_window, row=None):
        super().__init__()
        uic.loadUi("gui/component/create_component.ui", self)  # Load the .ui file for the GUI
        self.prev_window = prev_window
        self.row = row

        # Find GUI elements defined in the .ui file
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.submitButton = self.findChild(QPushButton, "createBtm")

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action

        if self.submitButton:
            self.submitButton.clicked.connect(self.handle_submit)
        if self.row:
            print(row)
            self.compName.setText(row['name'])
            self.compType.setText(row['type'])
            self.reference.setText(row['reference'])
            self.refFailure.setText(str(row['λref']))
            self.refTempe.setText(str(row['theetta1']))
            self.submitButton.setText("Update Component")

    def goBack(self):
        self.prev_window.refresh_components()  # Refresh the ProjectsWindow data
        self.close()  # Close the Create Project window
        self.prev_window.show()  # Show the ProjectsWindow

    def handle_submit(self):
        component_name = self.compName.text()
        type = self.compType.text()
        reference = self.reference.text()
        ref_failure = self.refFailure.text()
        ref_temp = self.refTempe.text()
        user_id = 1  # Example ID, replace with actual logic
        if component_name and type and ref_failure and ref_temp:
            reference = reference if reference else "nil"
            # Insert the project into the database
            if self.row:
                self.update_component(component_name, type, reference, ref_failure, ref_temp, self.row['componentid'])
            else:
                self.create_component(component_name, type, reference, ref_failure, ref_temp)

            # Refresh ProjectsWindow and go back
            self.goBack()

    @staticmethod
    def create_component(component_name, type, reference, ref_failure, ref_temp):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO components (name, type, reference, λref , theetta1) VALUES (?, ?, ?, ?, ?)",
            (component_name, type, reference, ref_failure, ref_temp))
        conn.commit()
        conn.close()

    def update_component(self, component_name, type, reference, ref_failure, ref_temp, comp_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE components SET name = ?, type = ?, reference = ?, λref = ?, theetta1 = ? WHERE componentid = ?",
            (component_name, type, reference, ref_failure, ref_temp, comp_id))
        conn.commit()
        conn.close()
