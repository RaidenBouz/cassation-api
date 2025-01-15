# Cassation-API

## Overview

This project collects data from a specified base URL and exposes it via a REST API. The API is designed to allow users to interact with the collected data in a structured and secure manner.

---

## How to Run

### 1. Setup Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
pip install -e .
```

### 3. Configure Environment Variables

Create a `.env` file at the root level of the project and specify the following variables:

```
JWT_SECRET_KEY=<your-jwt-secret-key>
SQLALCHEMY_DB_URI=sqlite:///decisions.db
SECRET_KEY=<your-secret-key>
```

- `JWT_SECRET_KEY`: A secure and random string used for signing JSON Web Tokens.
- `SQLALCHEMY_DB_URI`: The database URI for connecting to SQLite.
- `SECRET_KEY`: A secure and random string used for Flask sessions.

### 4. Initialize the Database

Run the following script to initialize an SQLite3 database:

```bash
python scripts/init_db.py
```

### 5. Fetch Data

Extract data from the base URL and store it into the database:

```bash
python scripts/fetch_data.py
```

---

## Using the API : [OpenAPI documentation](https://cassation-api-1092005627376.europe-west9.run.app/)

### 1. Start the Server

Run the following command to start the Flask development server:

```bash
flask run
```

The server will start locally, and the API can be accessed and tested via tools like Postman.

### 2. Authentication

To interact with the API, you need an access token. Follow these steps:

1. **Register**: Use the `/register` endpoint to create an account.
2. **Login**: Use the `/login` endpoint to obtain an access token and a refresh token.

- **Access Token**: Valid for 30 minutes.
- **Refresh Token**: Use the `/refresh` endpoint to renew your access token when it expires.

---

## API Features

### 1. Retrieve All Decisions

Get a list of all decisions:

```
GET /api/v1/decisions/
```

### 2. Filter Decisions

Filter decisions by a specific query parameter (e.g., chamber):

```
GET /api/v1/decisions/?formation="example"
```

### 3. Get Decision Content

Retrieve the content of a specific decision by providing its ID:

```
GET /api/v1/decisions/<decision_id>
Example: GET /api/v1/decisions/JURITEXT000048430356
```

### 4. Search Decisions

Search for decisions by a query string. The API searches both the title and content fields and sorts the results based on a basic score ranking:

```
GET /api/v1/decisions/search?q=<query_string>
Example: GET /api/v1/decisions/search?q=janvier
```

---

## OpenAPI Documentation

For more details on the available endpoints and request/response formats, refer to the [OpenAPI documentation](https://cassation-api-1092005627376.europe-west9.run.app/).

---

## Docker

You can build and run the project using Docker:

1. Build the Docker image:
   ```bash
   docker build -t cassation-api .
   ```
2. Run the Docker container:
   ```bash
   docker run -p 5000:5000 -e JWT_SECRET_KEY=<your-jwt-secret-key> -e SECRET_KEY=<your-secret-key> cassation-api
   ```

Ensure you set the `JWT_SECRET_KEY` and `SECRET_KEY` as environment variables during runtime.

---

## Deployment

The API is deployed on Google Cloud and is accessible online. Use the [live API link](https://cassation-api-1092005627376.europe-west9.run.app/) to interact with it.

---

## Additional Notes

- Make sure to replace placeholder values in the `.env` file and API calls with your actual credentials.
- Use Postman or similar tools to test the endpoints and confirm the expected behavior.
- Keep your secret keys secure and do not share them publicly.

---

## Self-Critique

This project is designed to be reliable and functional; however, it requires more comprehensive testing, particularly for edge cases, to ensure robustness. Prior to deploying this application in a production environment, it is essential to:

1. Conduct extensive tests for various edge cases to identify and address potential issues.
2. Perform thorough reviews and refinements to guarantee optimal performance and security.

Have a nice day!

