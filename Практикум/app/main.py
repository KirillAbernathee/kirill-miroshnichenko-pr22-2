import requests
import tkinter as tk
from tkinter import ttk, messagebox

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("400x600")
        
        self.currencies = ["RUB", "USD", "EUR", "CNY", "KRW"]
        
        self.exchange_rates = {}
        
        self.setup_ui()
        
        self.fetch_exchange_rates()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        title_label = tk.Label(self.root, text="Конвертер валют", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Из валюты:").grid(row=0, column=0, padx=5, pady=5)
        self.from_currency = ttk.Combobox(input_frame, values=self.currencies, 
                                          state="readonly", width=10)
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        self.from_currency.set("USD")
        
        tk.Label(input_frame, text="В валюту:").grid(row=1, column=0, padx=5, pady=5)
        self.to_currency = ttk.Combobox(input_frame, values=self.currencies, 
                                        state="readonly", width=10)
        self.to_currency.grid(row=1, column=1, padx=5, pady=5)
        self.to_currency.set("RUB")
        
        swap_button = tk.Button(input_frame, text="↔", 
                                command=self.swap_currencies, 
                                font=("Arial", 10, "bold"),
                                width=3, height=1)
        swap_button.grid(row=0, column=2, rowspan=2, padx=10)
        
        tk.Label(input_frame, text="Сумма:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        convert_button = tk.Button(input_frame, text="Конвертировать", 
                                   command=self.convert_currency, bg="#4CAF50", fg="white")
        convert_button.grid(row=3, column=0, columnspan=2, pady=15)
        
        result_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=2)
        result_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=False)
        
        tk.Label(result_frame, text="Результат:", font=("Arial", 12)).pack(pady=5)
        
        self.result_label = tk.Label(result_frame, text="0.00", 
                                     font=("Arial", 14, "bold"), fg="#2196F3")
        self.result_label.pack(pady=10)
        
        rates_frame = tk.LabelFrame(self.root, text="Курсы валют (1 USD =)", 
                                   font=("Arial", 10, "bold"), relief=tk.RIDGE)
        rates_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.rates_text = tk.Text(rates_frame, height=6, font=("Arial", 10))
        self.rates_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.status_label = tk.Label(self.root, text="Курсы загружаются...", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def swap_currencies(self):
        """Поменять валюты местами"""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        self.from_currency.set(to_curr)
        self.to_currency.set(from_curr)
        
        if self.amount_var.get():
            self.convert_currency()

    def fetch_exchange_rates(self):
        """Получение актуальных курсов валют через API"""
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for currency in self.currencies:
                    if currency in data['rates']:
                        self.exchange_rates[currency] = data['rates'][currency]
                    elif currency == "USD":
                        self.exchange_rates[currency] = 1.0
                
                self.status_label.config(text=f"Курсы обновлены: {data['date']}")
                self.update_rates_display()
                print("Курсы валют загружены успешно:")
                for curr, rate in self.exchange_rates.items():
                    print(f"1 USD = {rate} {curr}")
                    
            else:
                messagebox.showerror("Ошибка", "Не удалось получить курсы валют")
                self.status_label.config(text="Ошибка загрузки курсов")
                self.set_fallback_rates()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")
            self.status_label.config(text="Нет подключения к интернету")
            self.set_fallback_rates()

    def set_fallback_rates(self):
        """Резервные курсы валют на случай отсутствия интернета"""
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "RUB": 90.0,
            "CNY": 7.2,
            "KRW": 1300.0
        }
        self.status_label.config(text="Используются резервные курсы")
        self.update_rates_display()

    def update_rates_display(self):
        """Обновление отображения курсов валют"""
        self.rates_text.delete(1.0, tk.END)
        
        if not self.exchange_rates:
            self.rates_text.insert(tk.END, "Курсы валют не загружены")
            return
        
        for currency in self.currencies:
            if currency != "USD":
                rate = self.exchange_rates[currency]
                formatted_rate = f"{rate:.4f}"
                self.rates_text.insert(tk.END, f"1 USD = {formatted_rate} {currency}\n")

    def convert_currency(self):
        """Конвертация валюты"""
        try:
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()
            amount = float(self.amount_var.get())
            
            if not self.exchange_rates:
                messagebox.showwarning("Предупреждение", "Курсы валют не загружены")
                return
            
            if amount <= 0:
                messagebox.showwarning("Предупреждение", "Введите положительную сумму")
                return
            
            if from_curr == "USD":
                amount_in_usd = amount
            else:
                amount_in_usd = amount / self.exchange_rates[from_curr]
            
            if to_curr == "USD":
                result = amount_in_usd
            else:
                result = amount_in_usd * self.exchange_rates[to_curr]
            
            self.result_label.config(text=f"{result:.2f} {to_curr}")
            
            print(f"\nКонвертация: {amount:.2f} {from_curr} → {result:.2f} {to_curr}")
            print(f"Курс: 1 {from_curr} = {result/amount:.4f} {to_curr}")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
        except KeyError as e:
            messagebox.showerror("Ошибка", f"Валюта {e} не найдена в базе")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

def main():
    """Основная функция"""
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()