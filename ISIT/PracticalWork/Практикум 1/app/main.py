import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
from dictionary_api import DictionaryAPI

class DictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Электронный словарь")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        self.api = DictionaryAPI()
        
        self.setup_styles()
        
        self.setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Настройка стилей для виджетов."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('TEntry', font=('Segoe UI', 11))

    def setup_ui(self):
        """Создание интерфейса."""
        title_label = ttk.Label(
            self.root,
            text="🔍 Электронный словарь",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(
            self.root,
            text="Введите слово на русском или английском языке",
            font=('Segoe UI', 10)
        )
        subtitle_label.pack(pady=(0, 10))
        
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(input_frame, text="Введите слово:").pack(anchor=tk.W)
        
        self.word_entry = ttk.Entry(input_frame, font=('Segoe UI', 12))
        self.word_entry.pack(pady=5, fill=tk.X)
        self.word_entry.bind('<Return>', lambda e: self.search_word())
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.search_button = ttk.Button(
            button_frame,
            text="Поиск",
            command=self.search_word,
            style='TButton'
        )
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(
            button_frame,
            text="Очистить",
            command=self.clear_results
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        examples_frame = ttk.Frame(self.root)
        examples_frame.pack(pady=5)
        
        examples_label = ttk.Label(
            examples_frame,
            text="Примеры: ",
            font=('Segoe UI', 9)
        )
        examples_label.pack(side=tk.LEFT)
        
        examples = ["hello", "computer", "привет", "компьютер", "красивый", "бежать"]
        for example in examples:
            example_btn = ttk.Button(
                examples_frame,
                text=example,
                command=lambda ex=example: self.set_word(ex),
                width=len(example)
            )
            example_btn.pack(side=tk.LEFT, padx=2)
        
        result_frame = ttk.Frame(self.root)
        result_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        ttk.Label(result_frame, text="Результат:").pack(anchor=tk.W)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=18,
            bg='#f5f5f5'
        )
        self.result_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.status_bar = ttk.Label(
            self.root,
            text="Готов к работе. Введите слово и нажмите Enter или кнопку 'Поиск'.",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_word(self, word):
        """Устанавливает слово из примеров."""
        self.word_entry.delete(0, tk.END)
        self.word_entry.insert(0, word)
        self.search_word()

    def search_word(self):
        """Запуск поиска в отдельном потоке."""
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showwarning("Внимание", "Пожалуйста, введите слово для поиска.")
            return
        
        self.search_button.config(state=tk.DISABLED)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "⏳ Идет поиск...\n")
        self.status_bar.config(text="Идет поиск...")
        
        threading.Thread(target=self.async_search, args=(word,), daemon=True).start()

    def async_search(self, word):
        """Асинхронный поиск слова."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(self.api.get_word_info(word))
            self.update_results(result)
        except Exception as e:
            self.show_error(f"Ошибка при поиске: {str(e)}")
        finally:
            loop.close()
            self.root.after(0, self.enable_search_button)

    def update_results(self, result):
        """Обновление поля с результатами."""
        self.root.after(0, lambda: self.result_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.result_text.insert(tk.END, result))
        self.root.after(0, lambda: self.status_bar.config(text="Поиск завершен."))

    def show_error(self, message):
        """Показ ошибки."""
        self.root.after(0, lambda: messagebox.showerror("Ошибка", message))
        self.root.after(0, lambda: self.status_bar.config(text="Ошибка при поиске."))

    def enable_search_button(self):
        """Разблокировка кнопки поиска."""
        self.search_button.config(state=tk.NORMAL)

    def clear_results(self):
        """Очистка поля результатов."""
        self.word_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.status_bar.config(text="Готов к работе.")

    def on_closing(self):
        """Обработка закрытия приложения."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.api.close())
        loop.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DictionaryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()