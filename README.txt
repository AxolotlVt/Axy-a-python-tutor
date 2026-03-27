AXY
Local Python Mentor

Axy is a local Streamlit app that acts like a Python mentor and learning
assistant. It keeps chat history on your machine, tracks learning progress,
and can optionally connect to Spotify.

The app is designed to run locally and talk to a local Ollama server for AI
responses.

======================================================================
WHAT AXY DOES
======================================================================

- Chat-based Python help and mentoring
- Local conversation history and user data
- Mastery / progress system for learning
- Optional Spotify playback integration
- Windows-friendly launcher with automatic browser opening

======================================================================
RUNTIME REQUIREMENTS
======================================================================

You need:

- Python
- Ollama installed locally
- The Python packages from requirements.txt

Current runtime packages:

- requests
- cryptography
- spotipy
- streamlit
- psutil

Install them with:

    pip install -r requirements.txt

======================================================================
OLLAMA SETUP
======================================================================

Axy expects a local Ollama server.

Start Ollama with:

    ollama serve

The app currently uses the "phi3" model by default, so make sure that model
is available:

    ollama pull phi3

If Ollama is not running, Axy may show connection errors or tell you to run
"ollama serve" in another terminal.

======================================================================
HOW TO RUN AXY
======================================================================

Option 1: Run the Streamlit app directly

    streamlit run main.py

Option 2: Run the launcher

    python launch_axy.py

The launcher is the friendlier option. It prepares the runtime environment
and tries to open the browser automatically.

======================================================================
OPTIONAL SPOTIFY SETUP
======================================================================

Spotify support is optional.

You can provide the Spotify client secret with an environment variable:

    SPOTIPY_CLIENT_SECRET=your_client_secret

Or create encrypted local files with:

    python scripts/create_spotify_secret.py --secret YOUR_CLIENT_SECRET

This writes encrypted Spotify files into the data folder. Keep those files
private.

======================================================================
DATA AND FILES
======================================================================

Important project files:

- main.py
  Main Streamlit app

- launch_axy.py
  Launcher for local app startup

- Axy/
  Core app package

- data/
  Local runtime data such as chat history and user data

- requirements.txt
  Runtime Python dependencies

- Axy.spec
  PyInstaller spec file for building an executable

Notes:

- In source mode, runtime data stays under the local data folder.
- In a frozen executable build, runtime data may move to a per-user app folder.
- Launcher logs are written to launcher.log in the active runtime location.

======================================================================
TROUBLESHOOTING
======================================================================

If the app opens but responses fail:

- Make sure Ollama is running
- Make sure the phi3 model is installed
- Check launcher.log for startup details

If the browser does not open automatically:

- Run python launch_axy.py again
- Or open the local Streamlit URL manually if it is shown in the terminal or
  launcher message

If Spotify features do not work:

- Make sure your Spotify secret is configured
- Make sure the encrypted Spotify files exist if you use file-based setup
- Make sure Spotify has an active device ready for playback

======================================================================
TESTS AND BUILDING
======================================================================

requirements.txt is runtime-only.

If you want to run tests, install pytest separately:

    pip install pytest
    pytest -q

If you want to build the executable, install PyInstaller separately:

    pip install pyinstaller

======================================================================
SUMMARY
======================================================================

Axy is a local Python mentor app powered by Streamlit and Ollama, with chat,
learning progress, and optional Spotify support. Install the runtime
requirements, start Ollama, and launch the app.
