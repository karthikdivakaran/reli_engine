
from models.projects.projects import ProjectsWindow
from models.component.component import ComponentsWindow
from models.calculation.calculation import CalculationsWindow
from models.users.users import UserManagementWindow

def handle_project_btn(main_window):
    main_window.second_window = ProjectsWindow(main_window)
    main_window.second_window.show()
    main_window.hide()

def handle_component_btn(main_window):
    main_window.second_window = ComponentsWindow(main_window)
    main_window.second_window.show()
    main_window.hide()


def handle_calc_btn(main_window):
    main_window.second_window = CalculationsWindow(main_window)
    main_window.second_window.show()
    main_window.hide()


def handle_users_btn(main_window):
    main_window.second_window = UserManagementWindow(main_window)
    main_window.second_window.show()
    main_window.hide()
