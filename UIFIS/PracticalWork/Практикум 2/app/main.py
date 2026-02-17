import tkinter as tk
from tkinter import messagebox
import random

class WordPuzzleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Поле чудес")
        self.root.geometry("600x600")
        self.root.configure(bg='#f0f8ff')
        
        self.original_word = ""
        self.shuffled_word = ""
        self.user_word = ""
        self.word_letters = []
        self.buttons = []
        self.user_buttons = []
        self.history = []
        
        self.COLORS = {
            'bg': '#f0f8ff',
            'button': '#4682b4',
            'button_text': 'white',
            'correct': '#90ee90',
            'incorrect': '#ffcccb',
            'neutral': 'white',
            'disabled': '#f5f5f5',
            'text': 'black'
        }
        
        self.create_widgets()
        self.reset_game()
    
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="ПОЛЕ ЧУДЕС", 
            font=('Arial', 24, 'bold'),
            bg=self.COLORS['bg'],
            fg='#2e8b57'
        )
        title_label.pack(pady=10)
        
        desc_label = tk.Label(
            self.root,
            text="Угадайте слово из перемешанных букв",
            font=('Arial', 12),
            bg=self.COLORS['bg']
        )
        desc_label.pack()
        
        self.original_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.original_frame.pack(pady=10)
        
        self.original_label = tk.Label(
            self.original_frame,
            text="Введите слово:",
            font=('Arial', 12),
            bg=self.COLORS['bg']
        )
        self.original_label.pack(side=tk.LEFT)
        
        self.input_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.input_frame.pack(pady=5)
        
        self.word_entry = tk.Entry(
            self.input_frame, 
            font=('Arial', 14),
            width=20,
            show=""
        )
        self.word_entry.pack(side=tk.LEFT, padx=5)

        self.hidden_word_label = tk.Label(
            self.input_frame,
            text="",
            font=('Arial', 14),
            bg=self.COLORS['bg'],
            fg='blue'
        )
        self.hidden_word_label.pack(side=tk.LEFT, padx=5)
        
        self.start_button = tk.Button(
            self.input_frame,
            text="Начать игру",
            command=self.start_game,
            bg=self.COLORS['button'],
            fg=self.COLORS['button_text'],
            font=('Arial', 11, 'bold'),
            padx=15,
            pady=5
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.shuffled_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.shuffled_frame.pack(pady=20)
        
        shuffled_label = tk.Label(
            self.shuffled_frame,
            text="Перемешанные буквы:",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg']
        )
        shuffled_label.pack()
        
        self.letters_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.letters_frame.pack(pady=10)
        
        self.user_word_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.user_word_frame.pack(pady=20)
        
        user_label = tk.Label(
            self.user_word_frame,
            text="Ваше слово:",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg']
        )
        user_label.pack()
        
        self.user_letters_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.user_letters_frame.pack(pady=10)
        
        self.control_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.control_frame.pack(pady=20)
        
        self.check_button = tk.Button(
            self.control_frame,
            text="Проверить",
            command=self.check_word,
            bg='#32cd32',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.check_button.pack(side=tk.LEFT, padx=10)
        
        self.undo_button = tk.Button(
            self.control_frame,
            text="Отменить",
            command=self.undo_action,
            bg=self.COLORS['button'],
            fg=self.COLORS['button_text'],
            font=('Arial', 11),
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.undo_button.pack(side=tk.LEFT, padx=10)
        
        self.new_game_button = tk.Button(
            self.control_frame,
            text="Новая игра",
            command=self.new_game,
            bg='#ffa500',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8
        )
        self.new_game_button.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(
            self.root,
            text="Введите слово и нажмите 'Начать игру'",
            font=('Arial', 11),
            bg=self.COLORS['bg'],
            fg='#696969'
        )
        self.status_label.pack(pady=10)
        
        self.hidden_word_label.pack_forget()
    
    def shuffle_word(self, word):
        """Перемешивает буквы в слове"""
        letters = list(word)
        random.shuffle(letters)
        return ''.join(letters)
    
    def start_game(self):
        """Начинает новую игру"""
        word = self.word_entry.get().strip().upper()
        
        if not word:
            messagebox.showwarning("Ошибка", "Пожалуйста, введите слово!")
            return
        
        if len(word) < 2:
            messagebox.showwarning("Ошибка", "Слово должно содержать минимум 2 буквы!")
            return
        
        self.original_word = word
        self.shuffled_word = self.shuffle_word(word)
        self.user_word = ""
        self.word_letters = list(self.shuffled_word)
        self.history = []
        
        for widget in self.letters_frame.winfo_children():
            widget.destroy()
        
        for widget in self.user_letters_frame.winfo_children():
            widget.destroy()
        
        self.buttons = []
        self.user_buttons = []
        
        for i, letter in enumerate(self.word_letters):
            button = tk.Button(
                self.letters_frame,
                text=letter,
                font=('Arial', 14, 'bold'),
                width=4,
                height=2,
                bg=self.COLORS['neutral'],
                fg=self.COLORS['text'],
                activebackground='#f0f0f0',
                activeforeground=self.COLORS['text']
            )
            button.grid(row=0, column=i, padx=3, pady=3)
            button.config(command=lambda l=letter, idx=i, btn=button: self.add_letter(l, idx, btn))
            self.buttons.append(button)
        
        self.word_entry.config(show="*")
        self.hidden_word_label.config(text="*" * len(word))
        self.hidden_word_label.pack(side=tk.LEFT, padx=5)
        
        self.original_label.config(text=f"Загаданное слово: {'_' * len(word)}")
        
        self.check_button.config(state=tk.NORMAL)
        self.undo_button.config(state=tk.NORMAL)
        
        self.status_label.config(text="Собирайте слово, нажимая на буквы!")
        self.word_entry.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
    
    def add_letter(self, letter, index, button):
        """Добавляет букву к слову пользователя"""
        if letter is None or button['state'] == tk.DISABLED:
            return
        
        button.config(state=tk.DISABLED, bg=self.COLORS['disabled'], fg='#a0a0a0')
        
        self.user_word += letter
        self.history.append(('add', letter, index, button))
        
        user_button = tk.Button(
            self.user_letters_frame,
            text=letter,
            font=('Arial', 14, 'bold'),
            width=4,
            height=2,
            bg=self.COLORS['neutral'],
            fg=self.COLORS['text']
        )
        user_button.grid(row=0, column=len(self.user_word)-1, padx=3, pady=3)
        self.user_buttons.append(user_button)
        
        self.status_label.config(text=f"Слово: {self.user_word}")
    
    def undo_action(self):
        """Отменяет последнее действие"""
        if not self.history:
            return
        
        action_type, letter, index, button = self.history.pop()
        
        if action_type == 'add':
            self.user_word = self.user_word[:-1]
            
            if self.user_buttons:
                last_button = self.user_buttons.pop()
                last_button.destroy()
            
            button.config(
                state=tk.NORMAL, 
                bg=self.COLORS['neutral'],
                fg=self.COLORS['text']
            )
        
        self.status_label.config(text=f"Слово: {self.user_word}")
    
    def check_word(self):
        """Проверяет собранное слово"""
        if self.user_word == self.original_word:
            for button in self.user_buttons:
                button.config(bg=self.COLORS['correct'])
            
            self.status_label.config(
                text=f"Правильно! Слово угадано!",
                fg='green'
            )
            
            self.word_entry.config(show="")
            self.hidden_word_label.config(text="✓" * len(self.original_word), fg='green')
            
            messagebox.showinfo("Поздравляем!", f"Вы правильно угадали слово!\n\nСлово: {self.original_word}")
        else:
            for button in self.user_buttons:
                button.config(bg=self.COLORS['incorrect'])
            
            self.status_label.config(
                text=f"Неправильно! Попробуйте еще раз",
                fg='red'
            )
            
            self.word_entry.config(show="")
            self.hidden_word_label.config(text=self.original_word, fg='red')
            
            messagebox.showwarning("Неверно", 
                                 f"Слово собрано неправильно!\n\n"
                                 f"Ваш вариант: {self.user_word}\n"
                                 f"Правильный ответ: {self.original_word}")
    
    def new_game(self):
        """Начинает новую игру"""
        self.reset_game()
        self.word_entry.config(state=tk.NORMAL, show="")
        self.start_button.config(state=tk.NORMAL)
        self.check_button.config(state=tk.DISABLED)
        self.undo_button.config(state=tk.DISABLED)
        
        self.word_entry.delete(0, tk.END)
        self.hidden_word_label.config(text="", fg='blue')
        self.hidden_word_label.pack_forget()
        
        self.original_label.config(text="Введите слово:")
        self.status_label.config(
            text="Введите слово и нажмите 'Начать игру'",
            fg='#696969'
        )
        
        for widget in self.letters_frame.winfo_children():
            widget.destroy()
        
        for widget in self.user_letters_frame.winfo_children():
            widget.destroy()
        
        self.buttons = []
        self.user_buttons = []
    
    def reset_game(self):
        """Сбрасывает состояние игры"""
        self.original_word = ""
        self.shuffled_word = ""
        self.user_word = ""
        self.word_letters = []
        self.history = []

def main():
    root = tk.Tk()
    game = WordPuzzleGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()