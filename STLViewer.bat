@echo off

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python from https://www.python.org/downloads/
    pause
    exit /b
)

REM Create a virtual environment in the current folder
echo Creating a virtual environment...
python -m venv venv

REM Check if the virtual environment was successfully created
IF NOT EXIST venv (
    echo Failed to create virtual environment. Ensure you have Python installed.
    pause
    exit /b
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate

REM Install the dependencies
echo Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt

REM Check if requirements.txt was successfully processed
IF ERRORLEVEL 1 (
    echo Failed to install dependencies. Please check your Python installation or requirements.txt.
    pause
    exit /b
)

REM Run the application
echo Running the application...
python main.py

REM Check if the Python script executed successfully
IF ERRORLEVEL 1 (
    echo An error occurred while running the application. Please check the Python code or requirements.
    pause
    exit /b
)

REM Keep the terminal open after the app closes
echo Application has closed. Press any key to exit.
pause

REM Deactivate the virtual environment after use
echo Deactivating the virtual environment...
deactivate

echo The application has been closed.
pause
exit /b