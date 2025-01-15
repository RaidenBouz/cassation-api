# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set the working directory in the container
WORKDIR /app

# Copy only the necessary files for installation first
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Set up the SQLite database path
ENV FLASK_APP=src
ENV FLASK_ENV=production
ENV SQLALCHEMY_DB_URI='sqlite:////app/instance/decisions.db'


# Expose the port Flask runs on
EXPOSE 8080

# Run the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "src.runner:app"]
