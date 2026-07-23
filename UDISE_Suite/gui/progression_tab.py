import customtkinter as ctk
from tkinter import filedialog
from tkinter import ttk
import threading

from models.student_manager import StudentManager
from storage.json_loader import JsonLoader
from utils.logger import AppLogger
from utils.validator import Validator
from browser.browser_controller import BrowserController
from browser.progression_automation import UdiseAutomation

class ProgressionTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        
        
        
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
        ctk.set_appearance_mode("Dark") # Force dark mode for a sleeker look
        ctk.set_default_color_theme("blue")
        
        # Define Fonts
        title_font = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        heading_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        body_font = ctk.CTkFont(family="Segoe UI", size=13)
        
        # Main Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=25, fill="x")
        
        ctk.CTkLabel(header_frame, text="🎓 UDISE Auto Filler", font=title_font, text_color="#3a86ff").pack(side="left")
        ctk.CTkLabel(header_frame, text="by Debanshu Ghosh", font=body_font, text_color="gray").pack(side="right", anchor="s")

        # Main Content Container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Top Grid: JSON and Browser controls side by side
        top_grid = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_grid.pack(fill="x", pady=(0, 15))
        top_grid.columnconfigure(0, weight=1)
        top_grid.columnconfigure(1, weight=1)
        
        # JSON Section
        json_frame = ctk.CTkFrame(top_grid, corner_radius=12)
        json_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(json_frame, text="📁 Data Source", font=heading_font).pack(anchor="w", padx=15, pady=(15, 5))
        
        json_inner = ctk.CTkFrame(json_frame, fg_color="transparent")
        json_inner.pack(fill="x", padx=15, pady=(5, 15))
        
        self.json_path_var = ctk.StringVar(value="No file selected")
        path_lbl = ctk.CTkLabel(json_inner, textvariable=self.json_path_var, font=body_font, text_color="gray")
        path_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(json_inner, text="Browse", command=self._browse_json, width=80, font=body_font).pack(side="right")
        
        # Browser Status Section
        browser_frame = ctk.CTkFrame(top_grid, corner_radius=12)
        browser_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(browser_frame, text="🌐 Browser Connection", font=heading_font).pack(anchor="w", padx=15, pady=(15, 5))
        
        browser_inner = ctk.CTkFrame(browser_frame, fg_color="transparent")
        browser_inner.pack(fill="x", padx=15, pady=(5, 15))
        
        self.browser_status_lbl = ctk.CTkLabel(browser_inner, text="🔴 Not Connected", font=body_font)
        self.browser_status_lbl.pack(side="left")
        
        ctk.CTkButton(browser_inner, text="Launch Chrome", command=self._launch_chrome, width=110, fg_color="#28a745", hover_color="#218838", font=body_font).pack(side="right", padx=(5, 0))
        ctk.CTkButton(browser_inner, text="Connect", command=self._check_connection, width=80, font=body_font).pack(side="right", padx=5)
        
        # Stats Section
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#2b2b2b")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        stats_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_inner.pack(pady=15)
        
        self.lbl_found = ctk.CTkLabel(stats_inner, text="🔍 Found: 0", font=body_font)
        self.lbl_found.pack(side="left", padx=25)
        
        self.lbl_matched = ctk.CTkLabel(stats_inner, text="✅ Matched: 0", font=body_font, text_color="#28a745")
        self.lbl_matched.pack(side="left", padx=25)
        
        self.lbl_missing = ctk.CTkLabel(stats_inner, text="❌ Missing: 0", font=body_font, text_color="#dc3545")
        self.lbl_missing.pack(side="left", padx=25)
        
        # Style ttk Treeview for dark theme
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b",
                        rowheight=30,
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        borderwidth=0,
                        font=("Segoe UI", 11, "bold"))
        style.map('Treeview', background=[('selected', '#3a86ff')])
        
        # Preview Table
        preview_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        preview_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(preview_frame, text="📋 Student Preview", font=heading_font).pack(anchor="w", padx=15, pady=(15, 5))
        
        columns = ('website_row', 'pen_id', 'json_status', 'status')
        self.tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=6)
        self.tree.heading('website_row', text='Row')
        self.tree.heading('pen_id', text='PEN ID')
        self.tree.heading('json_status', text='In JSON?')
        self.tree.heading('status', text='Status')
        
        self.tree.column('website_row', width=80, anchor='center')
        self.tree.column('pen_id', width=200, anchor='center')
        self.tree.column('json_status', width=100, anchor='center')
        self.tree.column('status', width=150, anchor='center')
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Control Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))
        
        self.btn_start = ctk.CTkButton(btn_frame, text="▶ Start Filling", command=self._start_filling, state="disabled", font=heading_font, height=45)
        self.btn_start.pack(side="left")
        
        self.btn_stop = ctk.CTkButton(btn_frame, text="⏹ Stop", command=self._stop_filling, state="disabled", fg_color="#dc3545", hover_color="#c82333", font=heading_font, height=45)
        self.btn_stop.pack(side="left", padx=15)
        
        # Progress
        progress_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        progress_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        self.progress_lbl = ctk.CTkLabel(progress_frame, text="Filled 0 / 0", font=body_font)
        self.progress_lbl.pack(side="top", anchor="e")
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=12, progress_color="#3a86ff")
        self.progress_bar.pack(side="top", fill="x", pady=(5, 0))
        self.progress_bar.set(0)
        
        # Logs
        log_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        log_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(log_frame, text="📝 Execution Logs", font=heading_font).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.log_box = ctk.CTkTextbox(log_frame, font=("Consolas", 11), fg_color="#1e1e1e", text_color="#d4d4d4", corner_radius=8)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_box.configure(state="disabled")



    def _log_to_ui(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update()

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
        skipped_count = 0
        
        for row_index, pen_id, is_done in self.web_students:
            in_json = self.student_manager.has_student(pen_id)
            if is_done:
                status = "Skipped (Done)"
                json_status = "Yes" if in_json else "No"
                skipped_count += 1
            elif not in_json:
                missing_count += 1
                json_status = "No"
                status = "Skipped (Missing)"
                skipped_count += 1
            else:
                matched_count += 1
                json_status = "Yes"
                status = "Ready"
                
            self.tree.insert('', 'end', values=(row_index + 1, pen_id, json_status, status))
            
        self.lbl_found.configure(text=f"Students Found: {found_count}")
        self.lbl_matched.configure(text=f"Matched: {matched_count}")
        self.lbl_missing.configure(text=f"Missing: {missing_count}")
        
        if found_count > 0 and self.student_manager.count() > 0:
            if matched_count > 0:
                self.btn_start.configure(state="normal")
                self.logger.info(f"Ready to start. {matched_count} to fill, {skipped_count} skipped. 🟢")
            else:
                self.btn_start.configure(state="disabled")
                self.logger.warning("No students ready to fill (all skipped or missing). 🟡")
        else:
            self.btn_start.configure(state="disabled")

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
            for row_index, pen_id, is_done in self.web_students:
                if self.automation and self.automation._should_stop:
                    self.logger.info("Filling stopped by user.")
                    break
                    
                if is_done:
                    self.logger.info(f"Skipping PEN {pen_id}: already done.")
                    continue
                    
                student = self.student_manager.get_student(pen_id)
                if student:
                    success = self.automation.fill_student(row_index, pen_id, student)
                    if success:
                        filled += 1
                        self._update_progress(filled, total)
                else:
                    self.logger.info(f"Skipping PEN {pen_id}: not matched in JSON.")
                
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
        pass
