import copy

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QComboBox, QLineEdit

import constants
from database.db_connection import get_connection
from utils import utils
from models.component.view_component import ComponentViewWindow


class ComponentCreateWindow(QWidget):
    def __init__(self, prev_window, row=None):
        super().__init__()
        uic.loadUi("gui/component/create_component_page.ui", self)  # Load the .ui file for the GUI
        self.prev_window = prev_window
        self.row = row
        self.config = utils.get_comp_config()
        self.component_config = {}
        # Find GUI elements defined in the .ui file
        self.goBackButton = self.findChild(QPushButton, "backBtn")  # "Back" button
        self.nextButton = self.findChild(QPushButton, "nextBtm")

        if self.goBackButton:
            self.goBackButton.clicked.connect(self.goBack)  # Connect go back button to close action

        if self.nextButton:
            self.nextButton.clicked.connect(self.handle_submit)
        self.label_2.setVisible(False)
        self.equation.setVisible(False)
        deps_list = self.get_depends_values()
        for i in range(1,9):
            self.findChild(QLabel, f"vaiable_label_{i}").setVisible(False)
            self.findChild(QLabel, f"deps_label_{i}").setVisible(False)
            self.findChild(QLineEdit, f"const_value_{i}").setVisible(False)
            self.findChild(QLabel, f"vaiable_label_{i}").setText("")

            comb_box = self.findChild(QComboBox, f"select_val_{i}")
            comb_box.setVisible(False)
            comb_box.setProperty("id", f"{i}")
            comb_box.currentIndexChanged.connect(self.update_deps_values)
            for j in range(1, 4):
                new_comboBox = self.findChild(QComboBox, f"select_option_val_{i}_{j}")
                new_comboBox.setVisible(False)
                new_comboBox.clear()
                new_comboBox.addItem("Select Option")
                for item_v in deps_list:
                    new_comboBox.addItem(item_v)
        self.update_row = False
        if self.row:
            print(row)
            self.compName.setText(row['name'])
            self.component_config = copy.deepcopy(self.config.get(row['name'].strip().lower()))
            self.handle_submit()
            self.handle_submit()
            i = 1
            formula = self.component_config['formula']
            for item in formula.split('*'):
                key = item.strip()
                main_value = ""
                if "deps" in self.component_config['values'][key]:
                    main_value = "depends"
                else:
                    main_value = "constant"
                main_comboBox = self.findChild(QComboBox, f"select_val_{i}")
                idx = main_comboBox.findText(main_value)
                if idx != -1:
                    main_comboBox.setCurrentIndex(idx)
                if "deps" in self.component_config['values'][key]:
                    j = 1
                    for dep_item in self.component_config['values'][key]["deps"]:
                        dep_value = constants.key_map.get(dep_item, dep_item)
                        new_comboBox = self.findChild(QComboBox, f"select_option_val_{i}_{j}")
                        idx = new_comboBox.findText(dep_value)
                        if idx != -1:
                            new_comboBox.setCurrentIndex(idx)
                        j+=1
                else:
                    text_box = self.findChild(QLineEdit, f'const_value_{i}')
                    text_box.setText(str(self.component_config['values'][key]["value"]))
                i+=1

            # self.compType.setText(row['type'])
            # self.reference.setText(row['reference'])
            # self.refFailure.setText(str(row['λref']))
            # self.refTempe.setText(str(row['theetta1']))
            # self.submitButton.setText("Update Component")

    def goBack(self):
        self.prev_window.refresh_components()  # Refresh the ProjectsWindow data
        self.close()  # Close the Create Project window
        self.prev_window.show()  # Show the ProjectsWindow

    def update_deps_values(self, id):
        sender = self.sender()
        value = sender.currentText()
        print(value)
        print(id)
        obj_name = self.sender().objectName()
        obj_id = obj_name.split("_")[-1]
        if value:
            if value.lower() == "constant":
                for i in range(1,4):
                    combo_box = self.findChild(QComboBox, f'select_option_val_{obj_id}_{i}')
                    combo_box.setVisible(False)
                label_it = self.findChild(QLabel, f"deps_label_{obj_id}")
                label_it.setVisible(False)
                text_box = self.findChild(QLineEdit, f"const_value_{obj_id}")
                text_box.setVisible(True)
            else:
                text_box = self.findChild(QLineEdit, f"const_value_{obj_id}")
                text_box.setVisible(False)
                label_it = self.findChild(QLabel, f"deps_label_{obj_id}")
                label_it.setVisible(True)
                for i in range(1,4):
                    combo_box = self.findChild(QComboBox, f'select_option_val_{obj_id}_{i}')
                    combo_box.setVisible(True)

    def handle_submit(self):
        component_name = self.compName.text()
        if not self.update_row:
            if component_name.lower() in self.config:
                self.component_config = copy.deepcopy(self.config[component_name.strip().lower()])
            elif f"{component_name.lower()}s" in self.config:
                self.component_config = copy.deepcopy(self.config[f"{component_name.lower()}s"])
            if self.component_config:
                self.label_2.setVisible(True)
                self.equation.setVisible(True)
                self.equation.setText(self.component_config["formula"])
                self.update_row = True
            else:
                self.equation.setVisible(True)
                self.update_row = True
        else:
            if self.equation.text().strip():
                equation = self.equation.text()
                i = 1
                for item in equation.split("*"):
                    value = item.strip()
                    self.findChild(QLabel, f"vaiable_label_{i}").setVisible(True)
                    self.findChild(QLabel, f"vaiable_label_{i}").setText(value)

                    self.findChild(QComboBox, f"select_val_{i}").setVisible(True)
                    i += 1
        valid = True
        new_comp=None
        if self.equation.text().strip() and component_name.strip().lower():
            equation_str = self.equation.text().strip()
            new_comp = {
                "name": component_name.strip().lower(),
                "reliability": "",
                "duration": "",
                "formula": self.equation.text().strip(),
                "additional_data": [],
                "values": {
                }
            }
            i = 1
            for _item in equation_str.split('*'):
                t_label = self.findChild(QLabel, f"vaiable_label_{i}")
                lab_text = t_label.text().strip()
                select_val = self.findChild(QComboBox, f"select_val_{i}").currentText()
                if select_val.strip().lower() == "constant":
                    # "constant": true,
                    # "value": 1
                    val = self.findChild(QLineEdit, f"const_value_{i}").text()
                    new_comp["values"][lab_text] = {
                        "constant": True,
                        "value": val
                    }
                    if not val:
                        valid = False
                else:
                    new_comp["values"][lab_text] = {
                        "value": ""
                    }
                    temp_deps = {}
                    options_got = []
                    for j in range(1,4):
                        tmp_comp_item = self.findChild(QComboBox, f"select_option_val_{i}_{j}").currentText().strip()
                        if tmp_comp_item and tmp_comp_item.strip() not in constants.exclude_options:
                            options_got.append(constants.equ_map.get(tmp_comp_item, tmp_comp_item))
                    if len(options_got) == 0:
                        valid = False
                    for item in options_got:
                        temp_deps[item] = ""
                    new_comp["values"][lab_text]["deps"] = temp_deps
                i += 1

            print(new_comp)
        if valid:
            # "value": "",
            # "deps": {
            #     "type": "",
            #     "U/Umax": ""
            # }
            # row = {"name": component_name}
            self.second_window = ComponentViewWindow(self, self.prev_window, row=new_comp)
            self.second_window.show()
            self.hide()

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

    def get_depends_values(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM env_values")
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Map rows to dictionaries
        result_list = [dict(zip(column_names, comp)) for comp in results]
        conn.close()
        items = []
        for item in result_list:
            if item["value"] is not None and item["value"] not in items:
                items.append(item["value"])
        return items
