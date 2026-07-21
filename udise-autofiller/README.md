# UDISE+ Student Progression Auto Filler

A professional Windows desktop application in Python that automatically fills student progression data into the UDISE+ Student Progression portal using Playwright and CustomTkinter.

## Features
- **Object-Oriented Architecture**: Modular design for maintainability.
- **Modern GUI**: Built with CustomTkinter.
- **Browser Automation**: Uses Playwright to connect to an existing Chrome session without bypassing captchas or storing passwords.
- **Safety First**: Only fills editable fields and **never** clicks the "Update" button automatically. Allows for manual verification.

## Prerequisites
- Python 3.12+
- Google Chrome installed

## Installation

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## Usage

1. **Start Chrome in Debug Mode**:
   Double-click the `launch_chrome.bat` script. This will open Chrome with a remote debugging port enabled (`--remote-debugging-port=9222`).
   *(Note: Playwright requires this port to connect to your existing session.)*

2. **Log in to UDISE+**:
   In the newly opened Chrome window, log in to the UDISE+ portal manually and navigate to the Student Progression page.
   *(For testing, you can just open the `udise_mock/index.html` file created earlier.)*

3. **Start the Application**:
   Run the Python app:
   ```bash
   python app.py
   ```

4. **Workflow in App**:
   - Click **Browse** and select `students.json`.
   - Click **Check Connection**. The app will verify if Chrome is accessible and if you are on the correct page.
   - Wait for the app to scan the webpage and match PEN IDs against your JSON file.
   - Click **Start Filling**. The app will rapidly fill the data for all matched students on the current page.
   - Manually verify the data and click **Update** on the website for each row.

## Packaging with PyInstaller

To create a standalone `.exe` file:
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "gui;gui" --add-data "browser;browser" --add-data "models;models" --add-data "storage;storage" --add-data "utils;utils" app.py
```
*(Note: You may need to tweak PyInstaller arguments depending on Playwright's specific binary requirements.)*
