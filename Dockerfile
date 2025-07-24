# Use official lightweight Python image.
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app
WORKDIR /app

# Command to run the web service
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 web_app:application
