from PyQt5.QtWidgets import QMessageBox

from database.db_connection import get_connection


def confirm_delete(self, row):
    # Get the user ID or identifier of the selected row
    user_data = self.data[row]
    user_id = user_data.get("id")  # Assuming "id" is the unique identifier for the user

    # Show a confirmation dialog
    confirm_box = QMessageBox()
    confirm_box.setIcon(QMessageBox.Warning)
    confirm_box.setWindowTitle("Confirm Delete")
    confirm_box.setText("Are you sure you want to delete this user?")
    confirm_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = confirm_box.exec()

    if result == QMessageBox.Yes:
        # Perform deletion in the database
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM User WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()

            # Remove the user from the table
            self.data.pop(row)
            self.refresh_users()

            # Show success message
            success_box = QMessageBox()
            success_box.setIcon(QMessageBox.Information)
            success_box.setWindowTitle("User Deleted")
            success_box.setText(f"User with ID {user_id} has been successfully deleted.")
            success_box.exec()
        except Exception as e:
            conn.close()

            # Show error message
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText(f"An error occurred: {str(e)}")
            error_box.exec()
