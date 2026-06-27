
import subprocess
import sys

cmd = [
    sys.executable, "-m", "streamlit", "run",
    "ui/app.py",
    "--server.port", "8501",
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--theme.base", "dark",
    "--theme.primaryColor", "#FF4B4B",
    "--theme.backgroundColor", "#0E1117",
]

print("🔥 Dashboard launching...")
print("📍 Open: http://localhost:8501")
process = subprocess.Popen(cmd)
print(f"✅ Dashboard PID: {process.pid}")
process.wait()
