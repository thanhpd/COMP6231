# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the Python app
COPY get_recommendation.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 80

# Command to run the application
CMD ["python3", "get_recommendation.py"]
