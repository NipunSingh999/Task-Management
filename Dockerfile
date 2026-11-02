FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose API port
EXPOSE 8000

# Run migrations and start production server
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_demo_data && gunicorn taskflow.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
