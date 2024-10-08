# Use the official Python image from the Docker Hub
FROM python:3.10-alpine

# Set environment variables to ensure Python runs in unbuffered and maximally compatible mode
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory to /backend
WORKDIR /backend

# Copy the requirements.txt file into the container at /backend
COPY requirements.txt /backend/

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /backend
COPY . /backend/

# Create the uploads/images directory
RUN mkdir -p /backend/uploads/images

# Expose the port on which the Flask app will run (replace 5000 with your desired port)
EXPOSE 5000

# Run the Flask application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]