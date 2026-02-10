import tkinter as tk
from tkinter import ttk, messagebox
import math

def calculate():
    try:
        P = float(p_entry.get())
        t = float(t_entry.get())
        
        if P <= 0 or P > 1:
            messagebox.showerror("Ошибка", "Вероятность P(t) должна быть в интервале (0, 1]")
            return
        
        if t <= 0:
            messagebox.showerror("Ошибка", "Время t должно быть > 0")
            return
        
        # Экспоненциальный закон: P(t) = exp(-λ*t)
        # λ = -ln(P(t)) / t
        lambda_val = -math.log(P) / t
        
        # Среднее время безотказной работы: T_cp = 1 / λ
        T_cp = 1 / lambda_val
        
        # Частота отказов a(t) = λ * exp(-λ*t) = λ * P(t)
        a_t = lambda_val * P
        
        # Вывод результатов
        result_text = (
            f"Результаты расчёта:\n"
            f"Вероятность безотказной работы P(t) = {P:.4f}\n"
            f"Время работы t = {t:.2f} час.\n"
            f"Интенсивность отказов λ = {lambda_val:.6f} 1/час\n"
            f"Среднее время безотказной работы T_cp = {T_cp:.2f} час.\n"
            f"Частота отказов a(t) = {a_t:.6f} 1/час\n"
        )
        
        result_label.config(text=result_text)
        
    except ValueError:
        messagebox.showerror("Ошибка", "Введите числовые значения")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Создание основного окна
root = tk.Tk()
root.title("Расчёт показателей долговечности (Вариант 12)")
root.geometry("500x400")

# Заголовок
title_label = tk.Label(root, text="Вариант 12: Экспоненциальный закон надёжности", font=("Arial", 12, "bold"))
title_label.pack(pady=10)

# Описание
desc_text = (
    "Дано:\n"
    "Вероятность безотказной работы P(t) = 0,95\n"
    "Время работы t = 120 час.\n"
    "Экспоненциальный закон надёжности\n\n"
    "Найти:\n"
    "• Интенсивность отказов λ\n"
    "• Среднее время безотказной работы T_cp\n"
    "• Частоту отказов a(t)"
)
desc_label = tk.Label(root, text=desc_text, justify="left")
desc_label.pack(pady=10)

# Поля ввода
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="P(t) (вероятность безотказной работы):").grid(row=0, column=0, sticky="e", padx=5)
p_entry = tk.Entry(frame_input, width=15)
p_entry.insert(0, "0.95")
p_entry.grid(row=0, column=1, padx=5)

tk.Label(frame_input, text="t (время работы, час.):").grid(row=1, column=0, sticky="e", padx=5)
t_entry = tk.Entry(frame_input, width=15)
t_entry.insert(0, "120")
t_entry.grid(row=1, column=1, padx=5)

# Кнопка расчёта
calc_button = tk.Button(root, text="Вычислить", command=calculate, bg="lightblue", font=("Arial", 10))
calc_button.pack(pady=10)

# Поле вывода результатов
result_label = tk.Label(root, text="Результаты будут здесь...", justify="left", bg="white", relief="solid", padx=10, pady=10)
result_label.pack(pady=10, padx=20, fill="both", expand=True)

# Запуск приложения
root.mainloop()