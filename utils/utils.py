
import json
import shutil

import pandas as pd
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from PyQt5.QtWidgets import QMessageBox
from docx import Document
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QFileDialog

import constants


def get_comp_config():
    with open("component_configuration.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["components"]

def get_details_values(details):
    equation_values = "λ = "
    for item in details["values"]:
        if equation_values != "λ = ":
            equation_values += " * "
        equation_values += f"{details['values'][item]['value']}"
    try:
        result = f"λ = {eval(equation_values.split('λ = ')[-1].strip())}"
    except:
        result = ""
    return result, equation_values

def export_pdf(details):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/pdf_export.html')
    result, equation_val = get_details_values(details)
    html_content = template.render(details=details, result=result, equation=equation_val)

    # Save HTML file (optional)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    # Convert HTML to PDF
    HTML(string=html_content).write_pdf("output.pdf")


def export_html(details):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/pdf_export.html')
    result, equation_val = get_details_values(details)
    html_content = template.render(details=details, result=result, equation=equation_val)

    # Save HTML file (optional)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    # Convert HTML to PDF
    HTML(string=html_content).write_pdf("output.pdf")
    export_to_word(details)
    export_excel(details)

def export_to_word(details):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/pdf_export.html')
    result, equation_val = get_details_values(details)
    html_content = template.render(details=details, result=result, equation=equation_val)

    # Save HTML file (optional)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    # Create a new Word Document
    document = Document()

    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Simple conversion: paragraph by paragraph
    for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = element.get_text(strip=True)
        if not text:
            continue
        if element.name == "h1":
            document.add_heading(text, level=1)
        elif element.name == "h2":
            document.add_heading(text, level=2)
        elif element.name == "h3":
            document.add_heading(text, level=3)
        elif element.name == "li":
            document.add_paragraph(text, style='ListBullet')
        else:
            document.add_paragraph(text)

    # Save Word file
    document.save("output.docx")

def export_excel(details, filename="output.xlsx"):
    data = []
    keys = []
    for key in details:
        if type(details[key]) == str:
            if key not in keys:
                data.append([key.capitalize(), details[key],"","","","","","","","","",""])
                keys.append(key)
        elif type(details[key]) == list:
            for item in details[key]:
                for it_key, it_val in item.items():
                    if it_key not in keys:
                        data.append([it_key.capitalize(), it_val,"","","","","","","","","",""])
                        keys.append(it_key)
        elif type(details[key]) == dict:
            for key_item, key_data in details[key].items():
                temp = []
                # temp.append(key_item)
                temp.append(f"{key_item} = {key_data['value']}")
                if "deps" in key_data:
                    for sub_key in key_data['deps']:
                        key_value = sub_key
                        if sub_key in constants.key_map:
                            key_value = constants.key_map[sub_key]
                        temp.append(f"{key_value} = {key_data['deps'][sub_key]}")
                temp.extend(["","","","","","","",""])
                data.append(temp)
    result = ""

    for key, item in details['values'].items():
        result += f" {item['value']} *"
    result = eval(result[:-1])
    data.append([f"Result = {result}"])

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


def confirm_delete(current_comp, title, message, comp_box=None):
    """ Show confirmation dialog before deleting a row """
    msg = QMessageBox(current_comp)  # Ensure it has a parent
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(f"{title}")
    msg.setText(f"{message}")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDefaultButton(QMessageBox.Ok)

    result = msg.exec_()  # Show dialog

    if result == QMessageBox.Ok:
        msg.close()  # This is redundant as QMessageBox closes automatically


def load_stylesheet(path):
    with open(path, "r") as f:
        return f.read()

# def handle_home_btn(main_window):
#     main_window.home_window = MainWindow(main_window)
#     main_window.home_window.show()
#     main_window.close()  # Close the login window

def download_pdf(window):
    # Source file to be "downloaded"
    source_path = "output.pdf"

    # Ask user where to save it
    save_path, _ = QFileDialog.getSaveFileName(window, "Save File", "pdf_report.pdf", "PDF Files (*.pdf);;All Files (*)")

    if save_path:
        try:
            shutil.copy(source_path, save_path)
            print(f"File saved to: {save_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

def download_excel(window):
    # Sample data (replace with your actual data)
    source_path = "output.xlsx"

    # Ask user where to save it
    save_path, _ = QFileDialog.getSaveFileName(window, "Save Excel File", "excel_report.xlsx", "Excel Files (*.xlsx);;All Files (*)")

    if save_path:
        try:
            shutil.copy(source_path, save_path)
            print(f"File saved to: {save_path}")
        except Exception as e:
            print(f"Error saving file: {e}")


def download_word(window):
    # Sample data (replace with your actual data)
    source_path = "output.docx"

    # Ask user where to save it
    save_path, _ = QFileDialog.getSaveFileName(window, "Save Excel File", "excel_report.docx", "Word Files (*.docx);;All Files (*)")

    if save_path:
        try:
            shutil.copy(source_path, save_path)
            print(f"File saved to: {save_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
