from app import create_app
from models import db, Application

def check_database(app):
    with app.app_context():
        try:
            # Check if we can query the database
            applications = Application.query.limit(5).all()
            print(f"Successfully connected to the database. Found {len(applications)} applications.")
            for application in applications:
                print(f"Application ID: {application.id}, FIN: {application.fin}, Name: {application.name}")
        except Exception as e:
            print(f"An error occurred while checking the database: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    print("app:", app)
    print("db:", db)
    check_database(app)
