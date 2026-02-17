import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class MotionAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор механического движения")
        self.root.geometry("900x700")
        
        self.v0_var = tk.DoubleVar(value=0.0)
        self.a_var = tk.DoubleVar(value=0.0)
        self.t_var = tk.DoubleVar(value=1.0)
        
        self.create_widgets()
        
    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Входные данные", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        result_frame = ttk.LabelFrame(self.root, text="Результаты", padding=10)
        result_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        graph_frame = ttk.LabelFrame(self.root, text="График зависимости пути от времени", padding=10)
        graph_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Начальная скорость v₀ (м/с):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.v0_var, width=15).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Ускорение a (м/с²):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.a_var, width=15).grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Время движения t (с):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.t_var, width=15).grid(row=2, column=1, pady=5, padx=5)
        
        explanation = ttk.Label(input_frame, text="Ускорение:\n• > 0 - разгон\n• < 0 - замедление\n• = 0 - равномерное движение", 
                                justify="left", foreground="blue")
        explanation.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Рассчитать", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear).pack(side="left", padx=5)
        
        self.result_text = tk.Text(result_frame, height=10, width=40, font=("Arial", 10))
        self.result_text.grid(row=0, column=0, pady=5)
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.equation_label = ttk.Label(graph_frame, text="Уравнение движения: S(t) = v₀t ± (at²)/2", 
                                         font=("Arial", 10, "bold"))
        self.equation_label.pack(pady=5)
        
    def calculate(self):
        try:
            v0 = self.v0_var.get()
            a = self.a_var.get()
            t = self.t_var.get()
            
            if t <= 0:
                messagebox.showwarning("Предупреждение", "Время должно быть больше 0!")
                return
            
            v_end = v0 + a * t
            s = v0 * t + (a * t**2) / 2
            
            motion_type, description = self.determine_motion_type(v0, a, t)
            
            self.display_results(v0, a, t, v_end, s, motion_type, description)
            
            self.plot_graph(v0, a, t)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числовые значения!")
            
    def determine_motion_type(self, v0, a, t):
        if a == 0:
            if v0 == 0:
                return "Покой", "Тело находится в состоянии покоя (не движется)."
            else:
                return "Равномерное движение", "Тело движется с постоянной скоростью без ускорения."
        elif a > 0:
            if v0 == 0:
                return "Равноускоренное из состояния покоя", "Тело начинает движение из состояния покоя с постоянным положительным ускорением."
            else:
                return "Равноускоренное движение", "Тело движется с постоянным положительным ускорением, скорость увеличивается."
        else:  # a < 0
            t_stop = abs(v0 / a) if a != 0 else float('inf')
            if t <= t_stop:
                return "Равнозамедленное движение", "Тело движется с постоянным отрицательным ускорением, скорость уменьшается."
            else:
                return "Движение с остановкой и обратным ходом", f"Тело останавливается через {t_stop:.2f} с, затем движется в обратном направлении."
    
    def display_results(self, v0, a, t, v_end, s, motion_type, description):
        self.result_text.delete(1.0, tk.END)
        
        results = f"===== РЕЗУЛЬТАТЫ РАСЧЕТА =====\n\n"
        results += f"Входные данные:\n"
        results += f"  Начальная скорость v₀ = {v0:.2f} м/с\n"
        results += f"  Ускорение a = {a:.2f} м/с²\n"
        results += f"  Время движения t = {t:.2f} с\n\n"
        
        results += f"Результаты:\n"
        results += f"  Тип движения: {motion_type}\n"
        results += f"  Пройденный путь S = {s:.2f} м\n"
        results += f"  Конечная скорость v = {v_end:.2f} м/с\n\n"
        
        results += f"Описание движения:\n{description}"
        
        self.result_text.insert(1.0, results)
        
        sign = "+" if a >= 0 else "-"
        abs_a = abs(a)
        equation = f"Уравнение движения: S(t) = {v0:.2f}t {sign} ({abs_a:.2f}t²)/2"
        self.equation_label.config(text=equation)
    
    def plot_graph(self, v0, a, t):
        self.ax.clear()
        
        time_points = np.linspace(0, t, 100)
        
        s_points = v0 * time_points + (a * time_points**2) / 2
        
        self.ax.plot(time_points, s_points, 'b-', linewidth=2, label='S(t)')
        self.ax.plot(t, v0 * t + (a * t**2) / 2, 'ro', markersize=8, label=f'Конечная точка (t={t:.1f})')
        
        self.ax.plot(0, 0, 'go', markersize=8, label='Начало (t=0)')
        
        if a < 0 and v0 > 0:
            t_stop = abs(v0 / a)
            if t_stop <= t:
                s_stop = v0 * t_stop + (a * t_stop**2) / 2
                self.ax.plot(t_stop, s_stop, 'mo', markersize=8, label=f'Остановка (t={t_stop:.2f})')
        
        self.ax.set_xlabel('Время t (с)', fontsize=10)
        self.ax.set_ylabel('Путь S (м)', fontsize=10)
        self.ax.set_title('Зависимость пути от времени S(t)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper left')
        
        self.ax.set_xlim(left=-0.1 * t, right=1.1 * t)
        s_max = max(s_points) if len(s_points) > 0 else 1
        s_min = min(s_points) if len(s_points) > 0 else 0
        margin = 0.1 * (s_max - s_min) if s_max != s_min else 1
        self.ax.set_ylim(bottom=min(0, s_min) - margin, top=s_max + margin)
        
        self.canvas.draw()
    
    def clear(self):
        self.v0_var.set(0.0)
        self.a_var.set(0.0)
        self.t_var.set(1.0)
        
        self.result_text.delete(1.0, tk.END)
        
        self.ax.clear()
        self.ax.set_xlabel('Время t (с)', fontsize=10)
        self.ax.set_ylabel('Путь S (м)', fontsize=10)
        self.ax.set_title('Зависимость пути от времени S(t)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        
        self.equation_label.config(text="Уравнение движения: S(t) = v₀t ± (at²)/2")
        
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = MotionAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()