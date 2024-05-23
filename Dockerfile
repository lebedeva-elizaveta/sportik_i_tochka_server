FROM python:3.11.1-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p app/uploads/activities app/static/achievements app/uploads/avatars

# Ensure /var/tmp is writable
RUN mkdir -p /var/tmp && chmod 777 /var/tmp

# Set the environment variable for Gunicorn temporary files
ENV TMPDIR=/var/tmp
