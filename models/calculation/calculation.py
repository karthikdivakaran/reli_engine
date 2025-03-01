import json

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox

import constants
# from calculate_fr import *
from database.db_connection import get_connection



class CalculationsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi("gui/calculation_engine.ui", self)  # Load the .ui file for the GUI
        self.main_window = main_window

        self.theetta_1 = None
        self.ref_failure = None

        # Find GUI elements defined in the .ui file
        self.tableView = self.findChild(QWidget, "tableView")  # The QTableView
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.createButton = self.findChild(QPushButton, "createComponent")  # "Create" button
        self.calculateButton = self.findChild(QPushButton, "calculateBtm")  # "Create" button

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action
        if self.calculateButton:
            self.calculateButton.clicked.connect(self.calculate)

        self.comp_comboBox = self.findChild(QComboBox, "componentBox")
        self.type_comboBox = self.findChild(QComboBox, "typeComboBox")
        self.ref_comboBox = self.findChild(QComboBox, "refComboBox")
        self.tmp_comboBox = self.findChild(QComboBox, "tempComboBox")
        self.ref_comboBox = self.findChild(QComboBox, "refComboBox")
        self.comp_comboBox.clear()
        self.type_comboBox.clear()
        self.ref_comboBox.clear()
        self.tmp_comboBox.clear()
        self.comp_comboBox.addItem("Select Component")
        self.type_comboBox.addItem("Select Option")
        self.ref_comboBox.addItem("Select Option")
        self.tmp_comboBox.addItem("Select Option")
        self.tmp_comboBox.addItem("25")
        self.tmp_comboBox.addItem("30")
        self.tmp_comboBox.addItem("40")
        self.tmp_comboBox.addItem("50")
        self.tmp_comboBox.addItem("60")
        self.tmp_comboBox.addItem("70")
        self.tmp_comboBox.addItem("80")
        self.tmp_comboBox.addItem("90")
        self.tmp_comboBox.addItem("100")
        self.tmp_comboBox.addItem("110")
        self.tmp_comboBox.addItem("120")
        self.tmp_comboBox.addItem("125")

        self.components_list = self.get_all_components()
        self.comp_comboBox.currentIndexChanged.connect(self.update_components)
        self.type_comboBox.currentIndexChanged.connect(self.update_references)
        self.ref_comboBox.currentIndexChanged.connect(self.update_ref_values)

    def goBack(self):
        self.close()  # Close the Components window
        self.main_window.show()  # Show the main window

    def calculate(self):
        comp = self.comp_comboBox.currentText()
        type = self.type_comboBox.currentText()
        tmp = self.tempComboBox.currentText()
        if (comp not in constants.exclude_options and type not in constants.exclude_options and
                tmp not in constants.exclude_options):
            pi_value = self.get_pi_value()
            result = None
            if pi_value:
                result = calculate_fr_resistor_inductor(self.ref_failure, pi_value)
            self.resultLab.setText("Failure Rate")
            self.resultValue.setText(f"{result} × 10⁻⁹/hour")
        pass

    def get_all_components(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM components")
        components = cursor.fetchall()
        conn.close()
        # Fetch column names from the cursor
        column_names = [desc[0] for desc in cursor.description]

        # Map rows to dictionaries
        components_list = [dict(zip(column_names, comp)) for comp in components]
        components = []
        if components_list:
            for comp in components_list:
                if comp['name'] not in components:
                    components.append(comp['name'])
                    self.comp_comboBox.addItem(comp['name'])

        conn.close()  # Close the connection

        return components_list

    def update_components(self):
        self.type_comboBox.clear()
        self.type_comboBox.addItem("Select Option")
        compn = self.comp_comboBox.currentText()
        types = []
        for comp in self.components_list:
            if comp['type'] not in types and compn == comp["name"]:
                types.append(comp['type'])
                self.type_comboBox.addItem(comp['type'])
                self.refTemp.setText("")
                self.refFail.setText("")

    def update_references(self):
        self.ref_comboBox.clear()
        self.ref_comboBox.addItem("Select Option")
        refs = []
        compn = self.comp_comboBox.currentText()
        type = self.type_comboBox.currentText()
        for comp in self.components_list:
            if comp['reference'] not in refs and comp["name"] == compn and comp["type"] == type:
                ref = comp['reference'] if comp['reference'] else "nil"
                refs.append(comp['reference'])
                self.ref_comboBox.addItem(ref)
                self.refTemp.setText("")
                self.refFail.setText("")

    def update_ref_values(self):
        compn = self.comp_comboBox.currentText()
        type = self.type_comboBox.currentText()
        ref = self.ref_comboBox.currentText()
        for comp in self.components_list:
            if comp["name"] == compn and comp["type"] == type and ref == comp["reference"]:
                self.refTemp.setText(f"{comp['theetta1']} °C")
                self.refFail.setText(f"{comp['refFIT']}")
                self.theetta_1 = comp["theetta1"]
                self.ref_failure = comp["refFIT"]


    def get_pi_value(self):
        compn = self.comp_comboBox.currentText()
        theetta2 = self.tempComboBox.currentText()
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM temp_factor WHERE component = ? AND theetta1 = ? AND theetta2 = ?"
        cursor.execute(query, (compn, self.theetta_1, theetta2))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Map rows to dictionaries
        result_list = [dict(zip(column_names, comp)) for comp in results]
        conn.close()
        for item in result_list:
            if item["PiT"] is not None:
                return item["PiT"]
        return None
