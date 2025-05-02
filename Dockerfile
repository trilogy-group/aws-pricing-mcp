# Use Python 3.9 as the base image
FROM python:3.13-slim

# Set working directory in the container
WORKDIR /app

# Install curl for downloading files
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Fetch pricing data from public S3
RUN curl https://cloudfix-public-aws-pricing.s3.us-east-1.amazonaws.com/pricing/ec2_pricing.json.gz | gunzip > ec2_pricing.json

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server code
COPY src/server.py .

# Run the server when the container starts
CMD ["python", "server.py"]