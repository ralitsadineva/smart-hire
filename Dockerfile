# Use the official Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN apt-get update && apt-get install -y build-essential libffi-dev libpq-dev
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code to the working directory
COPY app.py .
COPY database.ini .
COPY templates ./templates
COPY static ./static

# Expose the port on which the Flask app runs
EXPOSE 5000

# Set the command to run the Flask app
CMD ["python", "app.py"]
