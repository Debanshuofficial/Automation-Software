import PyInstaller.__main__
import os
import sys

def build():
    # Base path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_script = os.path.join(base_dir, 'UDISE_Suite', 'main.py')
    
    # We need to add the directories as data
    add_data_suite = f"{os.path.join(base_dir, 'UDISE_Suite')};UDISE_Suite"
    
    
    PyInstaller.__main__.run([
        launcher_script,
        '--name=UDISE_Automation_Suite',
        '--onefile',
        '--noconsole',
        f'--add-data={add_data_suite}',
        
        '--clean'
    ])

if __name__ == "__main__":
    build()
