import json
import copy

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtGui import QIcon

import constants
from models.calculation.calculate_fr import *
from database.db_connection import get_connection
from models.projects.project_create import ProjectCreateWindow
from models.projects.view_project import ProjectViewWindow
from utils import utils
from session import Session


class CalculationsWindow(QWidget):
    def __init__(self, main_window, home_window, project_id=None, results=None):
        super().__init__()
        uic.loadUi("gui/calculation_engine.ui", self)  # Load the .ui file for the GUI
        self.main_window = main_window
        self.home_window = home_window
        self.config = utils.get_comp_config()
        self.component_config = {}
        self.alert = True
        self.prev_key = {}
        self.component = None
        self.user = Session().get_user()
        self.results = results
        if results:
            self.component_config = results

        self.theetta_1 = None
        self.project_id = project_id

        # Find GUI elements defined in the .ui file
        self.tableView = self.findChild(QWidget, "tableView")  # The QTableView
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.createButton = self.findChild(QPushButton, "createComponent")  # "Create" button
        self.calculateButton = self.findChild(QPushButton, "calculateBtm")  # "Create" button

        self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action
        self.calculateButton.clicked.connect(self.calculate)

        # self.export_result.clicked.connect(self.export_result_to_file)
        self.exportPdf.setIcon(QIcon("static/icons/pdf.png"))
        self.exportDoc.setIcon(QIcon("static/icons/word.png"))
        self.exportXls.setIcon(QIcon("static/icons/excel.png"))
        self.exportPdf.clicked.connect(self.export_result_to_pdf)
        self.exportDoc.clicked.connect(self.export_result_to_word)
        self.exportXls.clicked.connect(self.export_result_to_excel)

        self.comp_comboBox = self.findChild(QComboBox, "componentBox")
        self.type_comboBox = self.findChild(QComboBox, "typeComboBox")
        self.ref_comboBox = self.findChild(QComboBox, "refComboBox")
        self.tmp_comboBox = self.findChild(QComboBox, "tempComboBox")
        self.ref_comboBox = self.findChild(QComboBox, "refComboBox")
        self.homeButton = self.findChild(QPushButton, "homeBtn")
        if self.homeButton:
            self.homeBtn.setIcon(QIcon("static/icons/home.png"))
            self.homeButton.clicked.connect(self.handle_home)
        self.clear_items()

        self.comp_comboBox.clear()
        self.type_comboBox.clear()
        self.ref_comboBox.clear()
        self.tmp_comboBox.clear()
        self.comp_comboBox.addItem("Select Component")
        self.type_comboBox.addItem("Select Option")
        self.ref_comboBox.addItem("Select Option")
        self.tmp_comboBox.addItem("Select Option")

        self.components_list = self.get_all_components()
        self.comp_comboBox.currentIndexChanged.connect(self.update_components)
        self.type_comboBox.currentIndexChanged.connect(self.update_references)
        self.ref_comboBox.currentIndexChanged.connect(self.update_ref_values)
        self.tempComboBox.currentIndexChanged.connect(self.update_values)


        self.save_project.clicked.connect(self.save_project_data)
        if project_id:
            self.save_project.setText("Save")

        if self.results:
            com_index = self.comp_comboBox.findText(results['name'])
            if com_index != -1:
                self.comp_comboBox.setCurrentIndex(com_index)
            for item in results['additional_data']:
                for key in item:
                    if key == "type":
                        idx = self.type_comboBox.findText(item[key])
                        if idx != -1:
                            self.type_comboBox.setCurrentIndex(idx)
                    elif key == "reference":
                        idx = self.ref_comboBox.findText(item[key])
                        if idx != -1:
                            self.ref_comboBox.setCurrentIndex(idx)
                    else:
                        continue
            for key, item in results['values'].items():
                if "deps" in item:
                    if "theetta2" in item['deps']:
                        idx = self.tempComboBox.findText(item['deps']['theetta2'])
                        if idx != -1:
                            self.tempComboBox.setCurrentIndex(idx)
            self.calculate()
            self.results = None

    def goBack(self):
        self.close()  # Close the Components window
        self.main_window.show()  # Show the main window

    def handle_home(self):
        self.close()
        self.home_window.show()

    def update_project(self, result):
        project_id = self.project_id
        if type(project_id) == dict:
            project_id = self.project_id['ProjectID']
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Project SET Results = ? WHERE UserID = ? and ProjectID = ?",
            (json.dumps(result), self.user["UserID"], project_id))

        cursor.execute("SELECT * FROM Project WHERE ProjectID = ?", (project_id,))

        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.commit()
        conn.close()
        return projects[0]

    def save_project_data(self):
        if self.validate_comp():
            if self.project_id:
                row = self.update_project(self.component_config)
                self.second_window = ProjectViewWindow(self, self.home_window, row=row)
                self.second_window.show()
                self.hide()
            else:
                print("valid")
                self.second_window = ProjectCreateWindow(self, self.home_window, result=self.component_config)
                self.second_window.show()
                self.hide()

    def update_values(self):
        if self.component_config and not self.results:
            if "Pi_T" in self.component_config["values"] and "deps" in self.component_config["values"]["Pi_T"]:
                value = self.get_pi_value()
                if value:
                    self.component_config["values"]["Pi_T"]["value"] = value
            self.update_items()
    def validate_comp(self):
        valid = True
        if self.component and self.component not in constants.exclude_options:
            for _, component_item in self.component_config["values"].items():
                if not component_item["value"]:
                    valid = False
        else:
            valid = False
        return  valid

    def calculate(self):
        comp = self.comp_comboBox.currentText()
        self.component = comp
        if self.validate_comp():
            self.component_config["name"] = comp.strip()
            formula = self.component_config["formula"]
            items = formula.split("*")
            for item in items:
                key = item.strip()
                if self.component_config["values"][key]["value"]:
                    continue
                deps = self.component_config["values"][key].get("deps")
                if deps and not self.results:
                    val = self.get_value(deps=deps)
                    self.component_config["values"][key]["value"] = val

            self.resultLab.setText("Failure Rate")
            equation_values = "λ = "
            for item in self.component_config["values"]:
                if equation_values != "λ = ":
                    equation_values += " * "
                equation_values += f"{self.component_config['values'][item]['value']}"
            self.equation_2.setText(equation_values)
            try:
                self.resultValue.setText(f"λ = {eval(equation_values.split('λ = ')[-1].strip())}")
            except:
                self.resultValue.setText(f" Please verify all options are selected correctly")
            self.save_project.setEnabled(True)
            # self.export_result.setEnabled(True)
            self.exportPdf.setEnabled(True)
            self.exportDoc.setEnabled(True)
            self.exportXls.setEnabled(True)
        else:
            utils.confirm_delete(self, "Warning", f"Select all values for calculation", self.ref_comboBox)
            return

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
        self.equation.setText(f"λ = {self.component_config.get('formula')}")
        types = []
        for comp in self.components_list:
            if comp['type'] not in types and compn == comp["name"]:
                types.append(comp['type'])
                self.type_comboBox.addItem(comp['type'])
                self.refTemp.setText("")
                self.refFail.setText("")
        if len(types) == 1:
            self.type_comboBox.setCurrentIndex(1)
        self.clear_items()
        self.update_temp_select()
        self.update_items()
    def update_temp_select(self):
        temp_values = self.get_temp_values()

        self.tmp_comboBox.clear()
        self.tmp_comboBox.addItem("Select Option")
        if len(temp_values) > 0:
            for item in temp_values:
                self.tmp_comboBox.addItem(f"{item}")
        if not temp_values:
            self.tmp_comboBox.addItem("nil")
            self.tmp_comboBox.setCurrentIndex(1)

    def update_references(self):
        self.ref_comboBox.clear()
        self.ref_comboBox.addItem("Select Option")
        refs = []
        compn = self.comp_comboBox.currentText()
        if compn == "Select Component":
            return
        if compn.strip().lower() not in self.config and self.alert:
            self.alert = False
            self.comp_comboBox.setCurrentIndex(0)
            utils.confirm_delete(self, "Error", f"Component {compn} not configured", self.ref_comboBox)
            return
        else:
            self.alert = True
            type = self.type_comboBox.currentText()
            for comp in self.components_list:
                if comp['reference'] not in refs and comp["name"] == compn and comp["type"] == type:
                    ref = comp['reference'] if comp['reference'] else "nil"
                    refs.append(comp['reference'])
                    self.ref_comboBox.addItem(ref)
                    self.refTemp.setText("")
                    self.refFail.setText("")
        if len(refs) == 1:
            self.ref_comboBox.setCurrentIndex(1)
        self.update_temp_select()
        self.update_items()

    def update_ref_values(self):
        compn = self.comp_comboBox.currentText()
        type = self.type_comboBox.currentText() if self.type_comboBox.currentText() else None
        ref = self.ref_comboBox.currentText() if  self.ref_comboBox.currentText() else None
        if compn.strip().lower() in self.config:
            if not self.results:
                self.component_config = copy.deepcopy(self.config.get(compn.strip().lower()))
                if {"name": compn} not in self.component_config["additional_data"]:
                    self.component_config["additional_data"].append({"name": compn})
            for comp in self.components_list:
                if ref == 'nil' and not comp["reference"]:
                    ref = None
                if comp["name"] == compn and comp["type"] == type and ref == comp["reference"]:
                    if not self.results:
                        if {"type": type} not in self.component_config["additional_data"]:
                            self.component_config["additional_data"].append({"type": type})
                        if {"reference": ref} not in self.component_config["additional_data"]:
                            self.component_config["additional_data"].append({"reference": ref})
                    self.refTemp.setText(f"{comp['theetta1']} °C")
                    self.refFail.setText(f"{comp['λref']}")
                    if not self.results:
                        for key, item in self.component_config["values"].items():
                            if 'deps' in item and "theetta1" in item["deps"]:
                                item["deps"]["theetta1"] = comp['theetta1']
                            elif 'deps' in item and "type" in item["deps"]:
                                item["deps"]["type"] = type

                        self.component_config["values"]["λref"]["value"] = float(comp["λref"]) if comp.get("λref") else 1
        self.update_temp_select()
        self.update_items()


    def get_pi_value(self):
        if not self.results:
            if "deps" in self.component_config["values"]["Pi_T"]:
                if "theetta1" in self.component_config["values"]["Pi_T"]["deps"]:
                    compn = self.comp_comboBox.currentText()
                    theetta2 = self.tempComboBox.currentText()
                    theetta_1 = self.component_config["values"]["Pi_T"]["deps"]["theetta1"]
                    self.component_config["values"]["Pi_T"]["deps"]["theetta2"] = theetta2
                    conn = get_connection()
                    cursor = conn.cursor()
                    query = "SELECT * FROM env_factors WHERE component = ? AND theetta1 = ? AND theetta2 = ?"
                    cursor.execute(query, (compn, theetta_1, theetta2))
                    results = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]

                    # Map rows to dictionaries
                    result_list = [dict(zip(column_names, comp)) for comp in results]
                    conn.close()
                    for item in result_list:
                        if item["Pi_T"] is not None:
                            return item["Pi_T"]
                else:
                    return None
        return None

    def get_extra_values(self, key, value, item_key, com_type=None):
        compn = self.comp_comboBox.currentText()
        conn = get_connection()
        cursor = conn.cursor()
        if key== "type":
            query = "SELECT * FROM env_factors WHERE component = ? AND type = ?"
            cursor.execute(query, (compn, value))
        elif com_type:
            query = f"SELECT * FROM env_factors WHERE component = ? AND env_varibale = ? AND env_value = ? AND type = ?"
            cursor.execute(query, (compn, key, value, com_type))
        else:
            query = f"SELECT * FROM env_factors WHERE component = ? AND env_varibale = ? AND env_value = ?"
            cursor.execute(query, (compn, key, value))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Map rows to dictionaries
        result_list = [dict(zip(column_names, comp)) for comp in results]
        conn.close()
        items = []
        for item in result_list:
            if item_key in item and item[item_key] not in items:
                return item[item_key]
        return None

    def get_value(self, deps={}, key="", comp_type=""):
        if deps:
            if "theetta1" in key and  "theetta2" in key:
                return self.get_pi_value()
        elif key:
            compn = self.comp_comboBox.currentText()
            conn = get_connection()
            cursor = conn.cursor()
            if comp_type:
                query = "SELECT * FROM env_factors WHERE component = ? AND env_varibale = ? AND type = ?"
                cursor.execute(query, (compn, key, comp_type))
            else:
                query = "SELECT * FROM env_factors WHERE component = ? AND env_varibale = ?"
                cursor.execute(query, (compn, key))
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            # Map rows to dictionaries
            result_list = [dict(zip(column_names, comp)) for comp in results]
            conn.close()
            items = []
            for item in result_list:
                if "env_value" in item and item["env_value"] not in items:
                    items.append(item["env_value"])
            return items

    def get_temp_values(self):
        compn = self.comp_comboBox.currentText()
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM env_factors WHERE component = ?"
        cursor.execute(query, (compn,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Map rows to dictionaries
        result_list = [dict(zip(column_names, comp)) for comp in results]
        conn.close()
        items = []
        for item in result_list:
            if item["theetta2"] is not None and item["theetta2"] not in items:
                items.append(item["theetta2"])
        return items

    def export_result_to_pdf(self):
        print("Exporting result to file")
        utils.export_pdf(self.component_config)
        utils.download_pdf(self)
    def export_result_to_word(self):
        utils.export_to_word(self.component_config)
        utils.download_word(self)
    def export_result_to_excel(self):
        utils.export_excel(self.component_config)
        utils.download_excel(self)

    def clear_items(self):
        self.save_project.setEnabled(False)
        # self.export_result.setEnabled(False)
        self.exportPdf.setEnabled(True)
        self.exportDoc.setEnabled(True)
        self.exportXls.setEnabled(True)
        self.calculateButton.setEnabled(False)

        self.val_combo_1.clear()
        self.val_combo_2.clear()
        self.val_combo_3.clear()
        self.val_combo_4.clear()
        self.val_combo_5.clear()
        self.val_combo_6.clear()
        self.val_combo_7.clear()
        self.val_combo_8.clear()

        self.val_combo_1.setVisible(False)
        self.val_combo_2.setVisible(False)
        self.val_combo_3.setVisible(False)
        self.val_combo_4.setVisible(False)
        self.val_combo_5.setVisible(False)
        self.val_combo_6.setVisible(False)
        self.val_combo_7.setVisible(False)
        self.val_combo_8.setVisible(False)

        for i in range(1, 9):
            try:
                self.findChild(QLabel, f"val_label_res_{i}").setText("")
                self.findChild(QLabel, f"val_label{i}").setText("")
            except:
                continue

        self.resultLab.setText("")
        self.equation_2.setText("")
        self.resultValue.setText("")
        self.prev_key = {}
        self.component = None

    def update_items(self):
        self.clear_items()
        if not self.component_config:
            return
        index = 0
        valid = True
        for key, item in self.component_config["values"].items():
            index += 1
            if not item["value"]:
                valid = False
            if 'deps' in item:
                if "theetta1" in item["deps"] and "theetta2" in item["deps"]:
                    label = self.findChild(QLabel, f"val_label{index}")
                    label.setText(f"{key} : {item['value']}")
                elif "theetta1" in item["deps"]:
                    label = self.findChild(QLabel, f"val_label{index}")
                    label.setText(f"{key} : {item['value']}")
                elif key in ["λref"]:
                    label = self.findChild(QLabel, f"val_label{index}")
                    label.setText(f"{key} : {item['value']}")
                elif "type" in item["deps"]:
                    dep_keys = list(item["deps"].keys())
                    type_val = self.type_comboBox.currentText().strip()
                    if  len(dep_keys)==1:
                        label = self.findChild(QLabel, f"val_label{index}")
                        if type_val and type_val not in constants.exclude_options:
                            if not self.results:
                                value = self.get_extra_values("type", type_val, key)
                                item["value"] = value
                            label.setText(f"{key} : {item['value']}")
                    else:
                        for dep_key in dep_keys:
                            if dep_key == "type":
                                continue
                            label = self.findChild(QLabel, f"val_label{index}")
                            label.setText(f"{key}  {dep_key} :")

                            comb_box = self.findChild(QComboBox, f"val_combo_{index}")
                            comb_box.setVisible(True)
                            comb_box.addItem("Select Option")
                            val_items = self.get_value(key=dep_key)
                            temp_items = []
                            if val_items:
                                for val_item in val_items:
                                    comb_box.addItem(f"{val_item}")
                                    if val_items not in temp_items:
                                        temp_items.append(val_items)
                                    comb_box.setProperty("id", f"{key}|||{dep_key}|||{index}")
                                    comb_box.currentIndexChanged.connect(self.update_env_values)
                                    if len(temp_items) == 1:
                                        comb_box.setCurrentIndex(1)
                                    if self.results:
                                        val = self.results["values"][key]['deps'][dep_key]
                                        idx = comb_box.findText(val)
                                        if idx != -1:
                                            comb_box.setCurrentIndex(idx)


                elif "reference" in item["deps"]:
                    label = self.findChild(QLabel, f"val_label{index}")
                    ref = self.ref_comboBox.currentText().strip()
                    if not self.results:
                        value = self.get_extra_values("reference", ref, key)
                        item["value"] = value
                    label.setText(f"{key} : {item['value']}")
                else:
                    for val in item["deps"]:
                        label = self.findChild(QLabel, f"val_label{index}")
                        label.setText(f"{val} :")

                        comb_box = self.findChild(QComboBox, f"val_combo_{index}")
                        comb_box.setVisible(True)
                        comb_box.addItem("Select Option")
                        val_items = self.get_value(key=val)
                        temp_items = []
                        if val_items:
                            for val_item in val_items:
                                comb_box.addItem(f"{val_item}")
                                if val_items not in temp_items:
                                    temp_items.append(val_items)
                                comb_box.setProperty("id", f"{key}|||{val}|||{index}")
                                comb_box.currentIndexChanged.connect(self.update_env_values)
                                if len(temp_items) == 1:
                                    comb_box.setCurrentIndex(1)
                                if self.results:
                                    it_value = self.results["values"][key]['deps'][val]
                                    idx = comb_box.findText(it_value)
                                    if idx != -1:
                                        comb_box.setCurrentIndex(idx)

            elif "constant" in item:
                label = self.findChild(QLabel, f"val_label{index}")
                label.setText(f"{key} : {item['value']}")
        if valid:
            self.calculateButton.setEnabled(True)

    def update_env_values(self, value):
        sender = self.sender()
        value = sender.currentText()
        valid = True
        if value not in constants.exclude_options:
            combo_id = sender.property("id")
            item_key = combo_id.split("|||")[0]
            key = combo_id.split("|||")[1]
            index = combo_id.split("|||")[2]
            print(key, value, item_key)
            if item_key not in self.prev_key or self.prev_key[item_key] != combo_id+value:
                self.prev_key[item_key] = combo_id+value
                if "type" in self.component_config["values"][item_key]["deps"] and key != "type":
                    type_val = self.type_comboBox.currentText().strip()
                    comp_value = self.get_extra_values(key, value, item_key, type_val)
                    if not self.results:
                        self.component_config["values"][item_key]["deps"]["type"] = type_val
                else:
                    comp_value = self.get_extra_values(key, value, item_key)
                if comp_value:
                    if not self.results:
                        self.component_config["values"][item_key]["value"] = comp_value
                        self.component_config["values"][item_key]["deps"][key] = value

                    # text = self.findChild(QLabel, f"val_label{index}").text()
                    # self.findChild(QLabel, f"val_label{index}").setText(text+" "+comp_value)
                    for inx in range(1,5):
                        text_value = self.findChild(QLabel, f"val_label_res_{inx}").text().strip()
                        if text_value != "" and item_key not  in text_value:
                            continue
                        self.findChild(QLabel, f"val_label_res_{inx}").setText(item_key + " :" + str(comp_value))
                        break
                        # "val_label_res_4"
                else:
                    valid = False
        if valid:
            self.calculateButton.setEnabled(True)


