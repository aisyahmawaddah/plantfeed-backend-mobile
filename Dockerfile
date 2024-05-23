# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libpq-dev \ 
    && apt-get clean

# Copy the requirements file into the container
COPY requirements.txt /app/

# Print the contents of the requirements file for debugging
RUN cat /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Debug: Print the contents of the working directory for debugging
RUN ls -la /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV DJANGO_SETTINGS_MODULE=plantfeed.settings

# Run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "plantfeed.wsgi:application"]
