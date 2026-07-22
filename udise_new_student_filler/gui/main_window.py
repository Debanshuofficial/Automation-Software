import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import sys
from models.new_student import NewStudent
from storage.json_loader import JsonLoader
from utils.logger import AppLogger
from browser.browser_controller import BrowserController
from browser.udise_automation import UdiseNewStudentAutomation

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("UDISE+ AutoFiller By Debanshu Ghosh")
        self.geometry("800x850")
        
        # Core components
        self.logger = AppLogger()
        self.browser_ctrl = BrowserController(self.logger)
        self.automation = None
        self.current_student: NewStudent = None
        
        self._setup_ui()
        self.logger.set_ui_callback(self._log_to_ui)
        
        self.logger.info("Application Started. Please select a JSON file.")

    def _setup_ui(self):
        # Configuration
        ctk.set_appearance_mode("Dark") # Force dark mode for a sleeker look
        ctk.set_default_color_theme("blue")
        
        # Define Fonts
        title_font = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        heading_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        sub_heading_font = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        body_font = ctk.CTkFont(family="Segoe UI", size=12)
        
        # Main Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=25, fill="x")
        
        ctk.CTkLabel(header_frame, text="🎓 UDISE+ AutoFiller", font=title_font, text_color="#3a86ff").pack(side="left")
        ctk.CTkLabel(header_frame, text="by Debanshu Ghosh", font=body_font, text_color="gray").pack(side="right", anchor="s")

        # Main Content Container
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#3a86ff", scrollbar_button_hover_color="#0056b3")
        main_frame.pack(fill="both", expand=True, padx=25, pady=10)
              # Top Grid: 3 columns layout
        top_grid = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_grid.pack(fill="x", pady=(0, 15))
        top_grid.columnconfigure(0, weight=1, uniform="col")
        top_grid.columnconfigure(1, weight=1, uniform="col")
        top_grid.columnconfigure(2, weight=1, uniform="col")
        
        # 1. File Selection (Column 0)
        file_frame = ctk.CTkFrame(top_grid, corner_radius=12)
        file_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ctk.CTkLabel(file_frame, text="📁 1. Load Student JSON", font=sub_heading_font, wraplength=200).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.json_path_var = ctk.StringVar(value="No file selected")
        path_lbl = ctk.CTkLabel(file_frame, textvariable=self.json_path_var, font=body_font, text_color="gray")
        path_lbl.pack(fill="x", padx=15, pady=(5, 10))
        
        btn_inner_file = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_inner_file.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(btn_inner_file, text="Browse", command=self._browse_json, font=body_font).pack(side="top", fill="x", expand=True, pady=(0, 5))
        ctk.CTkButton(btn_inner_file, text="Relaunch", command=self._relaunch, fg_color="#dc3545", hover_color="#c82333", font=body_font).pack(side="top", fill="x", expand=True)
        
        # 2. Browser Connection (Column 1)
        browser_frame = ctk.CTkFrame(top_grid, corner_radius=12)
        browser_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5))
        
        ctk.CTkLabel(browser_frame, text="🌐 2. Browser Connection", font=sub_heading_font, wraplength=200).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.browser_status_lbl = ctk.CTkLabel(browser_frame, text="🔴 Not Connected", font=body_font)
        self.browser_status_lbl.pack(fill="x", padx=15, pady=(5, 10))
        
        btn_inner_browser = ctk.CTkFrame(browser_frame, fg_color="transparent")
        btn_inner_browser.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(btn_inner_browser, text="Connect & Scan", command=self._check_connection, font=body_font).pack(side="top", fill="x", expand=True, pady=(0, 5))
        ctk.CTkButton(btn_inner_browser, text="Launch Chrome", command=self._launch_chrome, fg_color="#28a745", hover_color="#218838", font=body_font).pack(side="top", fill="x", expand=True)
        
        # 3. Actions (Column 2)
        action_frame = ctk.CTkFrame(top_grid, corner_radius=12, fg_color="transparent")
        action_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.btn_scan = ctk.CTkButton(
            action_frame, 
            text="SCAN", 
            command=self._scan_page,
            state="disabled",
            height=45,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color="#e67e22",
            hover_color="#d35400",
            text_color="white",
            text_color_disabled="#f3c6a5"
        )
        self.btn_scan.pack(side="top", fill="both", expand=True, pady=(0, 5))
        
        self.btn_write = ctk.CTkButton(
            action_frame, 
            text="WRITE", 
            command=self._write_data,
            state="disabled",
            height=45,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            text_color="white",
            text_color_disabled="#d2b4de"
        )
        self.btn_write.pack(side="bottom", fill="both", expand=True, pady=(5, 0))
        
        # LED Status Row
        led_container = ctk.CTkFrame(main_frame, fg_color="#151515", corner_radius=12, border_width=1, border_color="#333333")
        led_container.pack(fill="x", pady=(0, 15), ipady=8)
        
        led_inner = ctk.CTkFrame(led_container, fg_color="transparent")
        led_inner.pack(expand=True)
        
        self.led_json_ind = ctk.CTkLabel(led_inner, text="⬤", font=ctk.CTkFont(size=18), text_color="#444444")
        self.led_json_ind.pack(side="left", padx=(10, 2))
        ctk.CTkLabel(led_inner, text="JSON Loaded", font=body_font).pack(side="left", padx=(0, 25))
        
        self.led_browser_ind = ctk.CTkLabel(led_inner, text="⬤", font=ctk.CTkFont(size=18), text_color="#444444")
        self.led_browser_ind.pack(side="left", padx=(10, 2))
        ctk.CTkLabel(led_inner, text="Browser Connected", font=body_font).pack(side="left", padx=(0, 25))
        
        self.led_ready_ind = ctk.CTkLabel(led_inner, text="⬤", font=ctk.CTkFont(size=18), text_color="#444444")
        self.led_ready_ind.pack(side="left", padx=(10, 2))
        ctk.CTkLabel(led_inner, text="Ready", font=body_font).pack(side="left", padx=(0, 25))
        
        self.led_progress_ind = ctk.CTkLabel(led_inner, text="⬤", font=ctk.CTkFont(size=18), text_color="#444444")
        self.led_progress_ind.pack(side="left", padx=(10, 2))
        self.led_progress_lbl = ctk.CTkLabel(led_inner, text="Idle", font=body_font)
        self.led_progress_lbl.pack(side="left", padx=(0, 10))

        # Student Info Preview
        info_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#222222")
        info_frame.pack(fill="x", pady=(0, 15))
        
        self.student_name_lbl = ctk.CTkLabel(info_frame, text="👤 Student Name: -", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color="#3a86ff")
        self.student_name_lbl.pack(anchor="center", pady=15)
        
        # Style ttk Treeview for dark theme (Better colors)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#1e1e1e", 
                        foreground="#e0e0e0", 
                        fieldbackground="#1e1e1e",
                        rowheight=40,
                        borderwidth=0,
                        font=("Segoe UI", 13)) # Increased font size
        style.configure("Treeview.Heading", 
                        background="#0056b3", 
                        foreground="white", 
                        borderwidth=0,
                        font=("Segoe UI", 13, "bold"))
        style.map('Treeview', background=[('selected', '#007bff')])
        
        # Field Comparison Table
        table_frame = ctk.CTkFrame(main_frame, corner_radius=12, border_width=2, border_color="#0056b3")
        table_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(table_frame, text="📋 Current Page Field Mapping", font=heading_font).pack(anchor="w", padx=15, pady=(15, 5))
        
        columns = ('site_label', 'json_field', 'json_value', 'status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
        self.tree.heading('site_label', text='Website Field Label')
        self.tree.heading('json_field', text='JSON Field Name')
        self.tree.heading('json_value', text='JSON Value')
        self.tree.heading('status', text='Status')
        
        self.tree.column('site_label', width=200, anchor='w')
        self.tree.column('json_field', width=120, anchor='center')
        self.tree.column('json_value', width=150, anchor='center')
        self.tree.column('status', width=120, anchor='center')
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Logs
        log_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        log_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(log_frame, text="📝 Execution Logs", font=heading_font).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.log_box = ctk.CTkTextbox(log_frame, font=("Consolas", 11), fg_color="#1e1e1e", text_color="#d4d4d4", corner_radius=8)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_box.configure(state="disabled")
        
    def _update_leds(self, in_progress=False, has_error=False):
        # Colors
        COLOR_OFF = "#444444"
        COLOR_GREEN = "#28a745"
        COLOR_RED = "#dc3545"
        COLOR_YELLOW = "#ffc107"
        
        # JSON Loaded
        if self.current_student:
            self.led_json_ind.configure(text_color=COLOR_GREEN)
        else:
            self.led_json_ind.configure(text_color=COLOR_OFF)
            
        # Browser Connected
        if self.browser_ctrl.connected:
            self.led_browser_ind.configure(text_color=COLOR_GREEN)
        else:
            self.led_browser_ind.configure(text_color=COLOR_OFF)
            
        # Ready
        is_ready = bool(self.current_student and self.browser_ctrl.connected and self.automation)
        if is_ready and not in_progress and not has_error:
            self.led_ready_ind.configure(text_color=COLOR_GREEN)
        else:
            self.led_ready_ind.configure(text_color=COLOR_OFF)
            
        # Progress / Error
        if has_error:
            self.led_progress_ind.configure(text_color=COLOR_RED)
            self.led_progress_lbl.configure(text="Error")
        elif in_progress:
            self.led_progress_ind.configure(text_color=COLOR_YELLOW)
            self.led_progress_lbl.configure(text="In Progress")
        else:
            self.led_progress_ind.configure(text_color=COLOR_OFF)
            self.led_progress_lbl.configure(text="Idle")

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
            self.json_path_var.set(os.path.basename(filepath))
            student, errors = JsonLoader.load(filepath)
            
            if errors:
                for err in errors:
                    self.logger.error(err)
                self.current_student = None
                self.student_name_lbl.configure(text="Student Name: [Error loading]")
                self._update_write_btn_state()
                self._update_leds(has_error=True)
            else:
                self.current_student = student
                self.student_name_lbl.configure(text=f"Student Name: {student.student_name}")
                self.logger.info(f"Loaded data for {student.student_name} 🟢")
                self._update_write_btn_state()
                self._update_leds()

    def _launch_chrome(self):
        import subprocess
        self.logger.info("Launching Chrome with remote debugging...")
        try:
            temp_dir = os.environ.get('TEMP', 'C:\\Temp')
            profile_dir = os.path.join(temp_dir, 'chrome_debug_profile_new')
            subprocess.Popen(f'start chrome --remote-debugging-port=9222 --user-data-dir="{profile_dir}"', shell=True)
            self.logger.info("Chrome launched. Please log in and navigate to the Add New Student page.")
        except Exception as e:
            self.logger.error(f"Failed to launch Chrome: {e}")

    def _check_connection(self):
        self.logger.info("Checking connection...")
        success, msg = self.browser_ctrl.connect()
        if success:
            self.browser_status_lbl.configure(text="🟢 Connected")
            page = self.browser_ctrl.get_page()
            if page:
                self.automation = UdiseNewStudentAutomation(page, self.logger)
                self.logger.info(f"Attached to page: {page.title()}")
                found_fields = self.automation.scan_page_fields(self.current_student)
                self._update_comparison_table(found_fields)
        else:
            self.browser_status_lbl.configure(text="🔴 Not Connected")
            self.automation = None
            self._update_comparison_table([])
            
        self._update_write_btn_state()
        self._update_leds()

    def _update_comparison_table(self, found_fields: list):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.automation or not found_fields:
            return
            
        for display_name, field_name, value in found_fields:
            status = "Ready" if value else "Empty in JSON"
            self.tree.insert('', 'end', values=(display_name, field_name, value, status))
            
    def _update_write_btn_state(self):
        if self.browser_ctrl.connected:
            self.btn_scan.configure(state="normal")
            if self.current_student:
                self.btn_write.configure(state="normal")
            else:
                self.btn_write.configure(state="disabled")
        else:
            self.btn_scan.configure(state="disabled")
            self.btn_write.configure(state="disabled")
            
    def _scan_page(self):
        if not self.automation:
            return
        self.logger.info("Manual scan triggered...")
        self.btn_scan.configure(state="disabled")
        self._update_leds(in_progress=True)
        
        def task():
            found_fields = self.automation.scan_page_fields(self.current_student)
            self._update_comparison_table(found_fields)
            self.btn_scan.configure(state="normal")
            self._update_leds(in_progress=False)
            
        self.after(100, task)

    def _write_data(self):
        if not self.automation or not self.current_student:
            return
            
        self.logger.info("Starting write process for visible fields...")
        self.btn_write.configure(state="disabled")
        self._update_leds(in_progress=True)
        
        # Run in a small delay to allow UI to update
        def task():
            filled_fields = self.automation.fill_visible_fields(self.current_student)
            
            # Update table
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                field_name = values[1]
                if field_name in filled_fields:
                    # Update status to "Written Success"
                    self.tree.item(item, values=(values[0], values[1], values[2], "Written Success"))
                    
            if filled_fields:
                self.logger.info("Write process completed. Please review and save manually.")
                self.btn_write.configure(state="normal")
                self._update_leds(in_progress=False)
            else:
                self.logger.error("No fields were successfully written.")
                self.btn_write.configure(state="normal")
                self._update_leds(in_progress=False, has_error=True)
            
        self.after(100, task)

    def on_closing(self):
        self.browser_ctrl.disconnect()
        self.destroy()

    def _relaunch(self):
        self.logger.info("Relaunching application...")
        self.browser_ctrl.disconnect()
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)
