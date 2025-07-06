# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Expose port
EXPOSE 8080

# Run the server
CMD ["python3", "server.py"]
