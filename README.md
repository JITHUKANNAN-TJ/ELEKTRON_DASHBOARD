# HydraMetric: Environmental Monitoring Dashboard

This project is an AI-powered environmental monitoring platform that tracks air quality and detects river waste using YOLOv26.

## Prerequisites

- **Python 3.8+**
- **Git**
- **Web Browser** (Chrome/Edge/Firefox)

## Setup on a New Laptop

### 1. Clone the Repository
Open a terminal (Command Prompt or PowerShell) and run:
```bash
git clone https://github.com/JITHUKANNAN-TJ/ELEKTRON_DASHBOARD.git
cd ELEKTRON_DASHBOARD
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to keep dependencies isolated.
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python libraries using the `requirements.txt` file:
```powershell
pip install -r requirements.txt
```

### 4. Run the Dashboard
You can use the provided batch file to start both the backend and the frontend:
```powershell
.\start_dashboard.bat
```

- **Start Backend**: `python backend\app.py`
- **Open Dashboard**: Go to [http://localhost:5000/](http://localhost:5000/) in your browser.

## Project Structure
- `backend/app.py`: FastAPI server handling AI detection and API requests.
- `index.html`: Main dashboard entry point.
- `map.html`: Interactive river monitoring map.
- `air_quality.html`: Real-time AQI tracking page.
- `yolo26n.pt`: YOLOv26 AI model weights.

## Troubleshooting
- **Camera Issues**: Ensure your laptop has a webcam or provide a URL to a stream in the UI.
- **Model Loading**: The first time you run the backend, it will download the YOLOv26 weights (if not already present). This may take a few minutes.
