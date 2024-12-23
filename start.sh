# start.sh
#!/bin/bash
# Start the Python backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the frontend server
cd ../frontend
python -m http.server 3000