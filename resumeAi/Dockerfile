# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # For pdflatex
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    texlive-latex-recommended \
    ghostscript \
    # For MySQL client
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port that the app will run on
EXPOSE 8000

# Run gunicorn to start the app
CMD ["gunicorn", "resumeAi.wsgi:application", "--bind", "0.0.0.0:8000"]