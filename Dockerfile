# Dockerfile for the FastAPI application
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn requests

# Install python-dotenv to handle .env files
RUN pip install python-dotenv

# Expose the port the app runs on
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["uvicorn", "api-call:app", "--host", "0.0.0.0", "--port", "8000"]