#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Initialize the database
python -c "
from app.database import init_db
init_db()
"

# Start the server
uvicorn enhanced_server:app --host 0.0.0.0 --port $PORT 