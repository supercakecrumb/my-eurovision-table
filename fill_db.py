"""
Database initialization script for Eurovision Table application.
This script can be run directly to populate the database with Eurovision data.

Environment variables:
- USE_REAL_EUROVISION_DATA: Set to '1' to use real Eurovision 2023 data
"""
from app import app
from app.db_init import initialize_database

if __name__ == '__main__':
    print("\n🎵 Eurovision Table Database Setup Script 🎵")
    print("===========================================")
    print("This script will initialize the database with Eurovision data.")
    print("You can also set AUTO_INIT_DB=1 in your environment to auto-initialize when the app starts.")
    
    with app.app_context():
        initialize_database()
        
    print("\nYou can now run the application and start voting!")
