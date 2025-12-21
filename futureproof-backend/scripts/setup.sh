#!/bin/bash

echo "========================================"
echo "FutureProof Backend Setup (Linux/Mac)"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Please install Docker"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv venv

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/6] Copying environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "CREATED: .env file. Please update with your API keys!"
else
    echo ".env already exists"
fi

echo "[5/6] Setting up database..."
docker-compose up -d postgres redis

echo "Waiting for database to be ready..."
sleep 10

echo "[6/6] Running database migrations..."
alembic upgrade head

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: docker-compose up"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "To activate venv: source venv/bin/activate"
echo "========================================"
