@echo off
REM Check if a virtual environment folder already exists
IF EXIST venv (
    echo Virtual environment already exists.
) ELSE (
    REM Create a new virtual environment named 'venv'
    python -m venv venv
    echo Virtual environment created.
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Install required libraries from requirements.txt
pip install -r requirements.txt

REM Deactivate the virtual environment after installation
deactivate

echo All required libraries have been installed.
