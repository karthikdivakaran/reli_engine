
import json
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from PyQt5.QtWidgets import QMessageBox


def get_comp_config():
    with open("component_configuration.json", "r") as file:
        data = json.load(file)
    return data["components"]


def export_html(details):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/pdf_export.html')
    html_content = template.render(details=details)

    # Save HTML file (optional)
    with open("output.html", "w") as f:
        f.write(html_content)
    # Convert HTML to PDF
    HTML(string=html_content).write_pdf("output.pdf")


def confirm_delete(current_comp, title, message, comp_box):
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
