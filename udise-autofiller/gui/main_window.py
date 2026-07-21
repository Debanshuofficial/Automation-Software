import customtkinter as ctk
from tkinter import filedialog
from tkinter import ttk
import threading

from models.student_manager import StudentManager
from storage.json_loader import JsonLoader
from utils.logger import AppLogger
from utils.validator import Validator
from browser.browser_controller import BrowserController
from browser.udise_automation import UdiseAutomation

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("UDISE Student Progression Auto Filler")
        self.geometry("800x850")
        
        # Managers
        self.logger = AppLogger()
        self.student_manager = StudentManager()
        self.browser_ctrl = BrowserController(self.logger)
        self.automation = None
        
        self.web_students = [] # (row_index, pen_id)
        
        self._setup_ui()
        self.logger.set_ui_callback(self._log_to_ui)
        
        self.logger.info("Application Started")

    def _setup_ui(self):
        # Configuration
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # JSON Section
        json_frame = ctk.CTkFrame(self)
        json_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(json_frame, text="JSON Data", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        json_inner = ctk.CTkFrame(json_frame, fg_color="transparent")
        json_inner.pack(fill="x", padx=10, pady=5)
        
        self.json_path_var = ctk.StringVar(value="No file selected")
        ctk.CTkLabel(json_inner, textvariable=self.json_path_var).pack(side="left")
        ctk.CTkButton(json_inner, text="Browse", command=self._browse_json, width=100).pack(side="right")
        
        # Browser Status Section
        browser_frame = ctk.CTkFrame(self)
        browser_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(browser_frame, text="Browser Controls", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        browser_inner = ctk.CTkFrame(browser_frame, fg_color="transparent")
        browser_inner.pack(fill="x", padx=10, pady=5)
        
        self.browser_status_lbl = ctk.CTkLabel(browser_inner, text="🔴 Not Connected")
        self.browser_status_lbl.pack(side="left")
        
        ctk.CTkButton(browser_inner, text="Connect", command=self._check_connection, width=100).pack(side="right", padx=5)
        ctk.CTkButton(browser_inner, text="Launch Chrome", command=self._launch_chrome, width=120, fg_color="#28a745", hover_color="#218838").pack(side="right", padx=5)

        
        # Stats Section
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_found = ctk.CTkLabel(stats_frame, text="Students Found: 0")
        self.lbl_found.pack(side="left", padx=20, pady=10)
        
        self.lbl_matched = ctk.CTkLabel(stats_frame, text="Matched: 0")
        self.lbl_matched.pack(side="left", padx=20, pady=10)
        
        self.lbl_missing = ctk.CTkLabel(stats_frame, text="Missing: 0")
        self.lbl_missing.pack(side="left", padx=20, pady=10)
        
        # Preview Table
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(pady=10, padx=20, fill="both", expand=True)
        ctk.CTkLabel(preview_frame, text="Preview Table", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        columns = ('website_row', 'pen_id', 'json_status', 'status')
        self.tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=6)
        self.tree.heading('website_row', text='Website Row')
        self.tree.heading('pen_id', text='PEN ID')
        self.tree.heading('json_status', text='JSON Found')
        self.tree.heading('status', text='Status')
        
        self.tree.column('website_row', width=100, anchor='center')
        self.tree.column('pen_id', width=200, anchor='center')
        self.tree.column('json_status', width=100, anchor='center')
        self.tree.column('status', width=150, anchor='center')
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Control Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        self.btn_start = ctk.CTkButton(btn_frame, text="Start Filling", command=self._start_filling, state="disabled")
        self.btn_start.pack(side="left", padx=10)
        
        self.btn_stop = ctk.CTkButton(btn_frame, text="Stop", command=self._stop_filling, state="disabled", fg_color="#dc3545", hover_color="#c82333")
        self.btn_stop.pack(side="left", padx=10)
        
        # Progress
        self.progress_lbl = ctk.CTkLabel(btn_frame, text="Filled 0 / 0")
        self.progress_lbl.pack(side="right", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        self.progress_bar.set(0)
        
        # Logs
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        ctk.CTkLabel(log_frame, text="Logs", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.log_box = ctk.CTkTextbox(log_frame)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_box.configure(state="disabled")

    def _log_to_ui(self, msg: str):
        def append():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, append)

    def _browse_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            self.json_path_var.set(filepath)
            students, errors = JsonLoader.load(filepath)
            if errors:
                for err in errors:
                    self.logger.error(err)
            
            if students:
                is_valid, val_msgs = Validator.validate_students_business_rules(students)
                for msg in val_msgs:
                    self.logger.warning(msg)
                    
                self.student_manager.load_students(students)
                self.logger.info(f"Loaded {self.student_manager.count()} students from JSON. 🟢 Loaded")
                self._update_preview()
            else:
                self.student_manager.students.clear()
                self.logger.error("No valid students loaded. 🔴")
                self._update_preview()

    def _launch_chrome(self):
        import subprocess
        import os
        self.logger.info("Launching Chrome with remote debugging...")
        try:
            temp_dir = os.environ.get('TEMP', 'C:\\Temp')
            profile_dir = os.path.join(temp_dir, 'chrome_debug_profile')
            # Use shell=True to allow 'start chrome'
            subprocess.Popen(f'start chrome --remote-debugging-port=9222 --user-data-dir="{profile_dir}"', shell=True)
            self.logger.info("Chrome launched. Please log in and navigate to Student Progression page.")
        except Exception as e:
            self.logger.error(f"Failed to launch Chrome: {e}")

    def _check_connection(self):
        def task():
            self.logger.info("Checking connection...")
            success, msg = self.browser_ctrl.connect()
            if success:
                self.browser_status_lbl.configure(text="🟢 Connected")
                page = self.browser_ctrl.get_page()
                if page:
                    self.automation = UdiseAutomation(page, self.logger)
                    if self.automation.is_student_progression_page():
                        self.logger.info("🟢 Student Progression Page")
                        self._scan_webpage()
                    else:
                        self.logger.error("🔴 Student Progression Page NOT detected")
                        self.browser_status_lbl.configure(text="🔴 Connected, but wrong page")
            else:
                self.browser_status_lbl.configure(text="🔴 Not Connected")
                
        # Run directly on main thread since Playwright sync API requires it
        task()

    def _scan_webpage(self):
        if not self.automation:
            return
            
        self.web_students = self.automation.scan_page()
        self.after(0, self._update_preview)

    def _update_preview(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        found_count = len(self.web_students)
        matched_count = 0
        missing_count = 0
        
        for row_index, pen_id in self.web_students:
            in_json = self.student_manager.has_student(pen_id)
            if in_json:
                matched_count += 1
                json_status = "Yes"
                status = "Ready"
            else:
                missing_count += 1
                json_status = "No"
                status = "Missing"
                
            self.tree.insert('', 'end', values=(row_index + 1, pen_id, json_status, status))
            
        self.lbl_found.configure(text=f"Students Found: {found_count}")
        self.lbl_matched.configure(text=f"Matched: {matched_count}")
        self.lbl_missing.configure(text=f"Missing: {missing_count}")
        
        if found_count > 0 and missing_count == 0 and self.student_manager.count() > 0:
            self.btn_start.configure(state="normal")
            self.logger.info("All visible students found in JSON. Ready to start. 🟢")
        else:
            self.btn_start.configure(state="disabled")
            if found_count > 0 and missing_count > 0:
                self.logger.error(f"{missing_count} students missing from JSON. Cannot start. 🔴")

    def _start_filling(self):
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress_bar.set(0)
        self.progress_lbl.configure(text=f"Filled 0 / {len(self.web_students)}")
        
        if self.automation:
            self.automation._should_stop = False
            
        def fill_task():
            total = len(self.web_students)
            filled = 0
            for row_index, pen_id in self.web_students:
                if self.automation and self.automation._should_stop:
                    self.logger.info("Filling stopped by user.")
                    break
                    
                student = self.student_manager.get_student(pen_id)
                if student:
                    success = self.automation.fill_student(row_index, pen_id, student)
                    if success:
                        filled += 1
                        self._update_progress(filled, total)
                
                # Keep UI responsive during the loop
                self.update()
            
            self.logger.info("Completed Current Page")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            
        # Run directly on main thread
        fill_task()

    def _update_progress(self, filled: int, total: int):
        self.progress_lbl.configure(text=f"Filled {filled} / {total}")
        if total > 0:
            self.progress_bar.set(filled / total)

    def _stop_filling(self):
        if self.automation:
            self.automation.stop()
        self.btn_stop.configure(state="disabled")

    def on_closing(self):
        self.browser_ctrl.disconnect()
        self.destroy()
