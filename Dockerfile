# Start from an official lightweight Python image
FROM python:3.12-slim

# Work inside /app in the container
WORKDIR /app

# Install dependencies first (cached between builds)
RUN pip install boto3

# Copy the code and notes in
COPY auditor.py .
COPY notes/ notes/

# What runs when the container starts
CMD ["python3", "auditor.py"]
