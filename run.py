from database.db_connection import initialize_database

def setup():
    print("Setting up the database...")
    initialize_database()
    print("Setup complete!")

if __name__ == "__main__":
    setup()
