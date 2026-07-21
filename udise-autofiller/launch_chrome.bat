@echo off
echo Starting Google Chrome with Remote Debugging Enabled...
start chrome --remote-debugging-port=9222 --user-data-dir="%temp%\chrome_debug_profile"
echo Chrome is now running.
echo Please log in to UDISE+, navigate to the Student Progression page, and start the UDISE Auto Filler application.
pause
