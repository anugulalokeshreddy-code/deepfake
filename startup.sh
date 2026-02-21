#!/bin/bash
# ViT Deepfake Detector - Startup Script for Linux/Mac

echo ""
echo "===================================="
echo "ViT Deepfake Detector - Startup"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
pip show transformers > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Check if database exists
if [ ! -f "backend/users.db" ]; then
    echo ""
    echo "Creating database..."
    python backend/init_db.py
    echo ""
fi

# Start the application
echo ""
echo "===================================="
echo "Starting ViT Deepfake Detector"
echo "===================================="
echo ""
echo "Application running at: http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python backend/app.py
