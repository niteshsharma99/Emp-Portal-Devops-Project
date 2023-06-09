# Use the official Python image as the base image
FROM python:3.8.0-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code to the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set the required environment variables
ENV DATABASE='emp_db.db'
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Create the database tables
CMD flask db upgrade

# Specify the command to run when the container starts
CMD flask run

