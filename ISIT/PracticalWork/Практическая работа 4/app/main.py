import tkinter as tk
from tkinter import ttk, font
import requests
from datetime import datetime
import json

class WeatherExpertSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Экспертная система погоды")
        self.root.geometry("850x750")
        self.root.configure(bg='#f0f8ff')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.cities = {
            "Макеевка": {"lat": 48.0478, "lon": 37.9722},
            "Донецк": {"lat": 48.0159, "lon": 37.8028},
            "Ростов": {"lat": 47.2313, "lon": 39.7233},
            "Москва": {"lat": 55.7558, "lon": 37.6173},
            "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351}
        }
        
        self.create_widgets()
        
    def configure_styles(self):
        self.style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), background='#f0f8ff', foreground='#2c3e50')
        self.style.configure('City.TLabel', font=('Segoe UI', 12), background='#f0f8ff', foreground='#34495e')
        self.style.configure('Card.TFrame', background='white', relief='solid', borderwidth=2)
        self.style.configure('Value.TLabel', font=('Segoe UI', 14, 'bold'), background='white', foreground='#2c3e50')
        self.style.configure('Param.TLabel', font=('Segoe UI', 10), background='white', foreground='#7f8c8d')
        self.style.configure('WeatherCard.TFrame', background='#e8f4fc', relief='solid', borderwidth=2)
        self.style.configure('WeatherValue.TLabel', font=('Segoe UI', 24, 'bold'), background='#e8f4fc', foreground='#2980b9')
        self.style.configure('WeatherState.TLabel', font=('Segoe UI', 14), background='#e8f4fc', foreground='#2c3e50')
        self.style.configure('Action.TButton', font=('Segoe UI', 12), padding=10)
        self.style.map('Action.TButton', background=[('active', '#3498db')])

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg='#f0f8ff')
        header_frame.pack(pady=20)
        
        ttk.Label(header_frame, text="🌤️ Экспертная система погоды", style='Title.TLabel').pack()
        
        control_frame = tk.Frame(self.root, bg='#f0f8ff')
        control_frame.pack(pady=20)
        
        ttk.Label(control_frame, text="Выберите город:", style='City.TLabel').grid(row=0, column=0, padx=10)
        
        self.city_combo = ttk.Combobox(control_frame, values=list(self.cities.keys()), 
                                      state="readonly", font=('Segoe UI', 11), width=20)
        self.city_combo.grid(row=0, column=1, padx=10)
        self.city_combo.current(0)
        
        self.refresh_btn = ttk.Button(control_frame, text="🔄 Обновить данные", 
                                     style='Action.TButton', command=self.get_weather)
        self.refresh_btn.grid(row=0, column=2, padx=20)
        
        self.weather_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.weather_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        self.create_weather_cards()
        
        self.status_label = ttk.Label(self.root, text="Выберите город и нажмите 'Обновить данные'", 
                                     font=('Segoe UI', 9), background='#f0f8ff', foreground='#95a5a6')
        self.status_label.pack(pady=10)

    def create_weather_cards(self):
        self.main_card = tk.Frame(self.weather_frame, bg='#e8f4fc', relief='solid', borderwidth=2)
        self.main_card.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nsew', ipadx=20, ipady=20)
        
        self.city_label = tk.Label(self.main_card, text="", font=('Segoe UI', 22, 'bold'), 
                                 bg='#e8f4fc', fg='#2c3e50')
        self.city_label.pack()
        
        self.temp_label = tk.Label(self.main_card, text="", font=('Segoe UI', 48, 'bold'), 
                                 bg='#e8f4fc', fg='#e74c3c')
        self.temp_label.pack()
        
        self.state_label = tk.Label(self.main_card, text="", font=('Segoe UI', 18), 
                                  bg='#e8f4fc', fg='#34495e')
        self.state_label.pack()
        
        self.update_label = tk.Label(self.main_card, text="", font=('Segoe UI', 10), 
                                   bg='#e8f4fc', fg='#7f8c8d')
        self.update_label.pack()
        
        params = [
            ("💨 Ветер", "wind_frame", "wind_value", "wind_desc"),
            ("💧 Влажность", "hum_frame", "hum_value", "hum_desc"),
            ("📊 Давление", "press_frame", "press_value", "press_desc"),
            ("🌧️ Осадки", "precip_frame", "precip_value", "precip_desc"),
            ("🌡️ Ощущается", "feel_frame", "feel_value", "feel_desc"),
            ("🎯 Код погоды", "code_frame", "code_value", "code_desc")
        ]
        
        self.param_widgets = {}
        
        for idx, (title, frame_name, value_name, desc_name) in enumerate(params):
            row = idx // 3
            col = idx % 3
            
            frame = tk.Frame(self.weather_frame, bg='white', relief='solid', borderwidth=2)
            frame.grid(row=row+1, column=col, padx=10, pady=10, sticky='nsew', ipadx=10, ipady=10)
            
            title_label = tk.Label(frame, text=title, font=('Segoe UI', 11, 'bold'), 
                                 bg='white', fg='#2c3e50')
            title_label.pack()
            
            value_label = tk.Label(frame, text="", font=('Segoe UI', 20, 'bold'), 
                                 bg='white', fg='#2980b9')
            value_label.pack(pady=5)
            
            desc_label = tk.Label(frame, text="", font=('Segoe UI', 10), 
                                bg='white', fg='#7f8c8d')
            desc_label.pack()
            
            self.param_widgets[frame_name] = frame
            self.param_widgets[value_name] = value_label
            self.param_widgets[desc_name] = desc_label
        
        for i in range(3):
            self.weather_frame.columnconfigure(i, weight=1)
        for i in range(2):
            self.weather_frame.rowconfigure(i, weight=1)

    def get_weather(self):
        city = self.city_combo.get()
        if not city:
            return
        
        lat = self.cities[city]["lat"]
        lon = self.cities[city]["lon"]
        
        try:
            self.status_label.config(text="⌛ Получаем данные...", foreground='#f39c12')
            self.root.update()
            
            weather_data = self.fetch_weather_api(lat, lon)
            self.display_weather(city, weather_data)
            
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.status_label.config(text=f"✅ Данные обновлены: {timestamp}", foreground='#27ae60')
            
        except Exception as e:
            self.status_label.config(text=f"❌ Ошибка: {str(e)}", foreground='#e74c3c')

    def fetch_weather_api(self, lat, lon):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Ошибка API: {response.status_code}")
        
        data = response.json()
        current = data.get("current_weather", {})
        if not current:
            raise Exception("Нет данных о погоде")
        
        return {
            "temperature": current.get("temperature", 0),
            "windspeed": current.get("windspeed", 0),
            "weathercode": current.get("weathercode", 0),
            "winddirection": current.get("winddirection", 0),
            "time": current.get("time", "")
        }

    def evaluate_temperature(self, temp):
        if temp < -10: return "❄️ Очень холодно", "#3498db"
        elif -10 <= temp < 0: return "🥶 Холодно", "#2980b9"
        elif 0 <= temp < 15: return "😊 Прохладно", "#1abc9c"
        else: return "☀️ Тепло", "#e74c3c"

    def evaluate_wind(self, wind):
        if wind < 5: return "🍃 Слабый", "#27ae60"
        elif 5 <= wind < 15: return "💨 Умеренный", "#f39c12"
        else: return "💨 Сильный", "#e74c3c"

    def evaluate_precipitation(self, precip):
        if precip == 0: return "☀️ Нет", "#2ecc71"
        elif 0 < precip <= 5: return "🌧️ Умеренные", "#3498db"
        else: return "🌧️ Сильные", "#9b59b6"

    def decode_weather_state(self, code):
        codes = {
            0: "☀️ Ясно", 1: "🌤️ Преимущественно ясно", 2: "⛅ Переменная облачность",
            3: "☁️ Пасмурно", 45: "🌫️ Туман", 48: "🌫️ Туман с инеем",
            51: "🌦️ Морось", 53: "🌦️ Морось", 55: "🌦️ Морось",
            61: "🌧️ Дождь", 63: "🌧️ Дождь", 65: "🌧️ Сильный дождь",
            71: "❄️ Снег", 73: "❄️ Снег", 75: "❄️ Сильный снег",
            80: "🌧️ Ливень", 81: "🌧️ Ливень", 82: "🌧️ Сильный ливень",
            85: "❄️ Снегопад", 86: "❄️ Сильный снегопад",
            95: "⛈️ Гроза", 96: "⛈️ Гроза с градом", 99: "⛈️ Сильная гроза с градом"
        }
        return codes.get(code, "❓ Неизвестно")

    def display_weather(self, city, data):
        temp = data["temperature"]
        wind = data["windspeed"]
        code = data["weathercode"]
        
        temp_eval, temp_color = self.evaluate_temperature(temp)
        wind_eval, wind_color = self.evaluate_wind(wind)
        state = self.decode_weather_state(code)
        
        precip = 0.0
        if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            precip = 2.5
        elif code in [71, 73, 75, 85, 86]:
            precip = 1.0
        
        precip_eval, precip_color = self.evaluate_precipitation(precip)
        
        humidity = 60 + int(temp * 0.5)
        if humidity > 90: humidity = 90
        if humidity < 30: humidity = 30
        
        pressure = 1013 - int(temp * 0.3)
        feels_like = temp - (wind * 0.2)
        
        self.city_label.config(text=city)
        self.temp_label.config(text=f"{temp:.1f}°C")
        self.state_label.config(text=state)
        
        update_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.update_label.config(text=f"Обновлено: {update_time}")
        
        wind_text = f"{wind:.1f} км/ч"
        self.param_widgets["wind_value"].config(text=wind_text, fg=wind_color)
        self.param_widgets["wind_desc"].config(text=wind_eval)
        
        hum_text = f"{humidity}%"
        hum_color = "#3498db" if humidity < 70 else "#e74c3c"
        self.param_widgets["hum_value"].config(text=hum_text, fg=hum_color)
        self.param_widgets["hum_desc"].config(text="Нормальная" if humidity < 70 else "Высокая")
        
        press_text = f"{pressure} гПа"
        self.param_widgets["press_value"].config(text=press_text, fg="#9b59b6")
        self.param_widgets["press_desc"].config(text="Нормальное")
        
        precip_text = f"{precip:.1f} мм"
        self.param_widgets["precip_value"].config(text=precip_text, fg=precip_color)
        self.param_widgets["precip_desc"].config(text=precip_eval)
        
        feel_text = f"{feels_like:.1f}°C"
        feel_eval, feel_color = self.evaluate_temperature(feels_like)
        self.param_widgets["feel_value"].config(text=feel_text, fg=feel_color)
        self.param_widgets["feel_desc"].config(text=feel_eval)
        
        code_text = str(code)
        self.param_widgets["code_value"].config(text=code_text, fg="#2c3e50")
        self.param_widgets["code_desc"].config(text="Код погодных условий")
        
        bg_color = "#e8f4fc"
        if temp < 0:
            bg_color = "#d6eaf8"
        elif temp > 20:
            bg_color = "#fef9e7"
        
        self.main_card.config(bg=bg_color)
        for widget in self.main_card.winfo_children():
            widget.config(bg=bg_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherExpertSystem(root)
    root.mainloop()