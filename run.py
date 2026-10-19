"""One-click launcher for the AI Students Success Dashboard.

Starts the Flask web server and automatically opens localhost:5000 in your default browser.
Uses only the Python standard library (no additional dependencies or JavaScript).
"""
import threading
import time
import webbrowser
from app import app


def open_browser():
    """Wait for the Flask server to initialize, then launch the browser."""
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Launching AI Students Success & Performance Dashboard...")
    print("📍 URL: http://127.0.0.1:5000")
    print("📖 Docs & Team: http://127.0.0.1:5000/about")
    print("=" * 60)
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=True)
