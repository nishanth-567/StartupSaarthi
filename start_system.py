
import os
import sys
import subprocess
import time
import socket
import webbrowser
import signal

# Configuration
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BACKEND_DIR, "startupsaarthi-ui")
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"

def kill_port(port):
    """Find and kill process on port for Windows."""
    try:
        # Find PID
        cmd = f"netstat -ano | findstr :{port}"
        output = subprocess.check_output(cmd, shell=True).decode()
        lines = output.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) > 4:
                pid = parts[-1]
                if pid != "0":
                    print(f"🔪 Killing PID {pid} on port {port}...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass # No process found
    except Exception as e:
        print(f"Warning cleaning port {port}: {e}")

def check_backend_health():
    """Poll backend health endpoint."""
    import urllib.request
    try:
        with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=1) as response:
            return response.status == 200
    except:
        return False

def main():
    print("🚀 STARTUPSAARTHI SYSTEM LAUNCHER")
    print("==================================")
    
    # 1. Cleanup
    print("\n[1/5] Cleaning up ports 8000 & 5173...")
    kill_port(8000)
    kill_port(5173)
    # subprocess.run("taskkill /F /IM python.exe /T", ...) # Removed to prevent self-kill
    # subprocess.run("taskkill /F /IM node.exe /T", ...)   # Removed to prevent killing other dev tools
    time.sleep(2)
    
    # 2. Check Environment
    print("\n[2/5] Checking Environment...")
    if not os.path.exists(".env"):
        print("❌ Error: .env file missing!")
        sys.exit(1)
    
    # 3. Start Backend
    print("\n[3/5] Starting Backend (127.0.0.1:8000)...")
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    # Use the same python interpreter that is running this script
    python_exe = sys.executable
    
    backend_cmd = f'start "StartupSaarthi Backend" cmd /k "cd /d {BACKEND_DIR} && "{python_exe}" -m backend.main"'
    subprocess.run(backend_cmd, shell=True)
    
    print("   Waiting for Backend to maximize...")
    retries = 30
    ready = False
    for i in range(retries):
        if check_backend_health():
            ready = True
            break
        print(f"   ...waiting ({i+1}/{retries})")
        time.sleep(1)
        
    if not ready:
        print("❌ Backend failed to start! Check the Backend terminal window for errors.")
        sys.exit(1)
    print("✅ Backend is Ready!")
    
    # 4. Start Frontend
    print("\n[4/5] Starting Frontend...")
    # Inject Node.js into PATH so both 'npm' and 'node' (used by vite) are found
    node_dir = r"C:\Program Files\nodejs"
    frontend_cmd = f'start "StartupSaarthi Frontend" cmd /k "set "PATH={node_dir};%PATH%" && cd /d {FRONTEND_DIR} && npm run dev"'
    subprocess.run(frontend_cmd, shell=True)
    
    # 5. Launch
    print("\n[5/5] Launching Browser...")
    time.sleep(3) # Give Vite a moment
    webbrowser.open(FRONTEND_URL)
    
    print("\n✅ SYSTEM LAUNCHED SUCCESSFULLY!")
    print("   Backend: http://127.0.0.1:8000")
    print("   Frontend: http://localhost:5173")
    print("\n   Press Enter to exit this launcher (Servers will keep running)...")
    input()

if __name__ == "__main__":
    main()
