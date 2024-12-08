# Work Pass Extension API

This project implements a Flask-based API for managing work pass extensions and Short-Term Visit Passes (STVPs) in Singapore.

## Project Structure

- `app.py`: Main application file that initializes the Flask app and sets up configurations.
- `check_db.py`: Script to check database connectivity and display sample data.
- `config.py`: Configuration settings for the application.
- `models.py`: Database models using SQLAlchemy.
- `routes.py`: API route definitions and handlers.
- `utils.py`: Utility functions, including API key authentication.
- `with_amendments.py`: Script to generate sample data for testing.
- `with_amendments.db`: SQLite database file.

## Setup and Installation

1. Clone the repository.
2. Install the required dependencies:
    pip install -r requirements.txt
- Flask
- Flask-SQLAlchemy
- Flask-Swagger-UI
- python-dotenv
- Faker
3. Set up environment variables:
- `API_KEY`: Your chosen API key
- `REQUIRE_API_KEY`: Set to 'True' to enable API key authentication

## Running the Application

1. Start the Flask server:
    python app.py

2. The API will be available at `http://localhost:5000`

## API Documentation

API documentation is available via Swagger UI at `/api/docs` when the server is running.

## Available Endpoints

- `GET /api/applications/search`: Search for applications by FIN
- `PUT /api/applications/<application_id>/update-expiry`: Update the expiry date of an application
- `POST /api/applications/<application_id>/create-stvp`: Create or extend an STVP
- `GET /api/applications`: List all applications (paginated)
- `GET /api/applications/<application_id>/amendments`: Get amendment history for an application

## Database

The project uses SQLite with SQLAlchemy ORM. The database file is `with_amendments.db`.

To generate sample data, run:
    python with_amendments.py

To check database connectivity and view sample data:
    python check_db.py

## Security

API key authentication is implemented. Set the `X-API-Key` header in your requests when `REQUIRE_API_KEY` is set to 'True'.

## Logging

Application logs are written to `api.log` and also output to the console.

## Development

For development purposes, the Flask debug mode is enabled. Ensure to disable this in a production environment.
