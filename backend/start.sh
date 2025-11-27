#!/bin/bash

# Set environment variables
export DATABASE_URL="sqlite:///./questions.db"
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000"
export LOG_LEVEL="INFO"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
