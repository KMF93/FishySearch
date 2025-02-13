import os
import socket
from contextlib import closing

def kill_port_8000():
    try:
        # First method: UNIX-style kill command
        os.system("kill -9 $(lsof -t -i:8000) 2>/dev/null")
        
        # Verify port status
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            if s.connect_ex(('localhost', 8000)) != 0:
                print("Port 8000 freed successfully")
                return

        # Fallback method for Pythonista's environment
        print("UNIX kill failed, trying Python alternative...")
        os.system('''python3 -c "import os; os.system('kill -9 $(ps aux | grep [8]000 | awk \\'{print $2}\\')')"''')

    except Exception as e:
        print(f"Error occurred: {e}")

    # Final check with iOS-specific advice
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        if s.connect_ex(('localhost', 8000)) == 0:
            print("\nIf still occupied, force-quit Pythonista:")
            print("1. Double-click home button")
            print("2. Swipe up on Pythonista's preview")
            print("3. Relaunch the app")

if __name__ == "__main__":
    kill_port_8000()
