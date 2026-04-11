AXY — Local Python Mentor

Axy is a fully local AI-powered Python learning assistant built with Streamlit and Ollama. It is designed for structured programming education with mastery tracking, practice modes, and formative assessment.

1. Core Features
Chat-based Python tutoring with guided explanations
Mastery/progression system based on competencies
Practice, quiz, and challenge modes
Code evaluation with feedback loops
Fully local AI inference via Ollama
Persistent local user data

===============================================================================
2. System Architecture
Axy.exe → main application launcher (user entry point)
Streamlit app → UI and tutoring logic
Ollama runtime → local model inference
Local storage → user progress, sessions, and logs
install.bat → full automated setup system

===============================================================================
3. Installation
Distribution format

Axy is distributed as a .rar archive containing the full system.

Setup process
Extract the .rar file
Run:
install.bat
What the installer does

The installer automatically:

Checks Python installation
Installs required Python dependencies
Installs or configures Ollama
Downloads required model (qwen2.5-coder:1.5b)
Prepares runtime environment

No manual setup of dependencies or AI models is required.

===============================================================================
4. Running Axy
Main method (recommended)
Run Axy.exe

This:
starts the application
connects to local AI backend
opens the browser interface automatically
Developer mode (optional)
streamlit run main.py

===============================================================================
5. System Requirements

All runtime requirements are handled automatically by the installer.
Manual requirements only if running outside installer:

Python 3.10+
Windows OS
Local environment permissions for installs
at least 4 Gigabytes of free space
at least 4 Gigabytes of Ram
===============================================================================
6. Data Storage

All data is stored locally.

Structure
data/ → user accounts, mastery progress, session history
launcher.log → system logs

No cloud storage or external transmission is required for core functionality.

===============================================================================
7. Learning System

Axy is designed as a competency-based tutoring system.

Key components
Mastery tracking per topic
Competency-aligned progression model
Points system based on understanding and performance
Code evaluation with structured feedback
Retry-based learning loops
Modes
Chat mode → explanation and tutoring
Test mode → assessment
Challenge mode → micro coding tasks

===============================================================================
8. Troubleshooting
Axy does not start
Re-run install.bat
Ensure extracted folder is intact
AI not responding
Ensure Ollama is running (handled automatically by installer if needed)
Re-run installer if model is missing
System issues
Delete and reinstall via .rar package if corrupted
Ensure Windows permissions allow installation

===============================================================================
9. Summary

Axy is a fully local AI tutoring system for Python education, designed for classroom deployment.

It provides:

automated installation via batch script
local AI inference through Ollama
structured learning and assessment system
competency-based educational alignment
