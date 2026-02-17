import tkinter as tk
from tkinter import ttk, messagebox

class ReliabilityCalculatorVariant12:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчёт коэффициента отсутствия дефектов (Вариант 12)")
        self.root.geometry("500x700")
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Вариант 12", font=("Arial", 14, "bold")).pack(pady=10)
        
        description = """В системе возможны три состояния:
1. Работа без дефектов (P0)
2. Работа с дефектом (P1)
3. Отказ (P2)

Вероятности состояний в установившемся режиме:
P0 = 0.85, P1 = 0.1, P2 = 0.05

Коэффициент отсутствия дефектов K_од = Σ P_k(t)
где K — подмножество состояний, в которых отсутствуют дефекты
(работа без дефектов + работа с дефектом)."""
        
        ttk.Label(main_frame, text=description, justify='left', wraplength=450).pack(pady=10)
        
        input_frame = ttk.LabelFrame(main_frame, text="Введите вероятности состояний", padding=15)
        input_frame.pack(fill='x', pady=15)
        
        self.p0_var = tk.StringVar(value="0.85")
        self.p1_var = tk.StringVar(value="0.10")
        self.p2_var = tk.StringVar(value="0.05")
        
        ttk.Label(input_frame, text="P0 (работа без дефектов):").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(input_frame, textvariable=self.p0_var, width=15).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(input_frame, text="P1 (работа с дефектом):").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(input_frame, textvariable=self.p1_var, width=15).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(input_frame, text="P2 (отказ):").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(input_frame, textvariable=self.p2_var, width=15).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Button(main_frame, text="Рассчитать K_од", command=self.calculate_k_od).pack(pady=10)
        
        self.result_frame = ttk.LabelFrame(main_frame, text="Результат", padding=15)
        self.result_frame.pack(fill='x', pady=15)
        
        self.result_label = ttk.Label(self.result_frame, text="", font=("Arial", 12))
        self.result_label.pack()
        
        ttk.Button(main_frame, text="Вернуть значения по умолчанию", 
                  command=self.set_default_values).pack(pady=5)
        
    def calculate_k_od(self):
        try:
            p0 = float(self.p0_var.get())
            p1 = float(self.p1_var.get())
            p2 = float(self.p2_var.get())
            
            total = p0 + p1 + p2
            
            if abs(total - 1.0) > 0.001:
                messagebox.showwarning("Проверка", 
                    f"Сумма вероятностей должна быть равна 1.0\n"
                    f"Текущая сумма: {total:.3f}\n"
                    f"Автоматическая нормализация...")
                
                p0 = p0 / total
                p1 = p1 / total
                p2 = p2 / total
                
                self.p0_var.set(f"{p0:.3f}")
                self.p1_var.set(f"{p1:.3f}")
                self.p2_var.set(f"{p2:.3f}")
            
            k_od = p0 + p1
            
            self.result_label.config(
                text=f"Коэффициент отсутствия дефектов K_од = {k_od:.4f}\n"
                     f"P0 + P1 = {p0:.3f} + {p1:.3f} = {k_od:.3f}\n"
                     f"P2 (отказ) = {p2:.3f}"
            )
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
            
    def set_default_values(self):
        self.p0_var.set("0.85")
        self.p1_var.set("0.10")
        self.p2_var.set("0.05")
        self.result_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReliabilityCalculatorVariant12(root)
    root.mainloop()