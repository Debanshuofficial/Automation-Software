import customtkinter as ctk
from gui.progression_tab import ProgressionTab
from gui.new_student_tab import NewStudentTab

class UnifiedApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("UDISE+ AutoFiller Suite")
        self.geometry("900x900")
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("Student Progression")
        self.tabview.add("New Student Entry")
        
        self.progression_tab = ProgressionTab(master=self.tabview.tab("Student Progression"))
        self.progression_tab.pack(fill="both", expand=True)
        
        self.new_student_tab = NewStudentTab(master=self.tabview.tab("New Student Entry"))
        self.new_student_tab.pack(fill="both", expand=True)
        
    def on_closing(self):
        self.progression_tab.on_closing()
        self.new_student_tab.on_closing()
        self.destroy()
