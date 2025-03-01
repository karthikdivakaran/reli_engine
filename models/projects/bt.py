from database.db_connection import get_connection

def create_project(project_name, description, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS Project (
           ID INTEGER PRIMARY KEY AUTOINCREMENT,
           ProjectName TEXT NOT NULL,
           Description TEXT,
           CreatedDate DATETIME,
           LastModified DATETIME,
           UserID INTEGER
       )
       """)

    cursor.execute(
        "INSERT INTO Project (ProjectName, Description, CreatedDate, LastModified , UserID) VALUES (?, ?, datetime('now'), datetime('now'), ?)",
        (project_name, description, user_id))
    conn.commit()
    conn.close()


create_project("Project2", "Capacitor Reliab", 1)