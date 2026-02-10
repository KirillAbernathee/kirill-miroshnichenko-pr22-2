import tkinter as tk
from tkinter import messagebox
from database import Database
from forms import MainForm, AddProposalForm, DetailsForm, ReportForm

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления предложениями по расширению ИС")
        self.root.geometry("1000x700")
        
        self.db = Database()
        
        self.main_form = MainForm(root, self)
        self.main_form.pack(fill=tk.BOTH, expand=True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_add_form(self, proposal_id=None, edit=False):
        """Показать форму добавления/редактирования предложения"""
        AddProposalForm(self.root, self, proposal_id, edit)
    
    def show_details_form(self, proposal_id):
        """Показать форму деталей предложения"""
        DetailsForm(self.root, self, proposal_id)
    
    def show_report_form(self):
        """Показать форму формирования отчетов"""
        ReportForm(self.root, self)
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()