import tkinter as tk
from tkinter import ttk, messagebox
from models import Proposal, Category, Status

class MainForm(tk.Frame):
    """Главная форма - список предложений"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.setup_ui()
        self.load_proposals()
    
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(
            self,
            text="📋 Предложения по расширению информационной системы",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Панель кнопок
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        
        tk.Button(
            button_frame,
            text="➕ Добавить предложение",
            command=self.controller.show_add_form,
            bg="green",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📊 Сформировать отчет",
            command=self.controller.show_report_form,
            bg="blue",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🔄 Обновить",
            command=self.load_proposals,
            bg="gray",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Фильтры
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=5, fill=tk.X, padx=20)
        
        tk.Label(filter_frame, text="Фильтр по статусу:").pack(side=tk.LEFT, padx=5)
        self.status_filter = ttk.Combobox(
            filter_frame,
            values=["Все"] + [status.value for status in Status],
            state="readonly",
            width=15
        )
        self.status_filter.pack(side=tk.LEFT, padx=5)
        self.status_filter.set("Все")
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.load_proposals())
        
        tk.Label(filter_frame, text="Фильтр по категории:").pack(side=tk.LEFT, padx=5)
        self.category_filter = ttk.Combobox(
            filter_frame,
            values=["Все"] + [category.value for category in Category],
            state="readonly",
            width=25
        )
        self.category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter.set("Все")
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.load_proposals())
        
        # Таблица предложений
        table_frame = tk.Frame(self)
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Создаем Treeview
        columns = ("id", "title", "category", "status", "author", "priority", "cost", "date")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Настройка колонок
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("category", text="Категория")
        self.tree.heading("status", text="Статус")
        self.tree.heading("author", text="Автор")
        self.tree.heading("priority", text="Приоритет")
        self.tree.heading("cost", text="Стоимость")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=250)
        self.tree.column("category", width=150)
        self.tree.column("status", width=100)
        self.tree.column("author", width=120)
        self.tree.column("priority", width=80)
        self.tree.column("cost", width=100)
        self.tree.column("date", width=120)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка двойного клика
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # Кнопки действий
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)
        
        tk.Button(
            action_frame,
            text="👁️ Просмотр",
            command=self.view_proposal,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="✏️ Редактировать",
            command=self.edit_proposal,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🗑️ Удалить",
            command=self.delete_proposal,
            bg="#f44336",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Статистика
        self.stats_label = tk.Label(
            self,
            text="",
            font=("Arial", 9),
            fg="gray"
        )
        self.stats_label.pack(pady=5)
    
    def load_proposals(self):
        """Загрузка предложений в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем все предложения
        proposals = self.db.get_all_proposals()
        
        # Применяем фильтры
        filtered_proposals = proposals
        if self.status_filter.get() != "Все":
            filtered_proposals = [p for p in filtered_proposals if p.status.value == self.status_filter.get()]
        if self.category_filter.get() != "Все":
            filtered_proposals = [p for p in filtered_proposals if p.category.value == self.category_filter.get()]
        
        # Добавляем в таблицу
        for proposal in filtered_proposals:
            priority_text = {1: "Высокий", 2: "Средний", 3: "Низкий"}.get(proposal.priority, "Не указан")
            self.tree.insert("", tk.END, values=(
                proposal.id,
                proposal.title,
                proposal.category.value,
                proposal.status.value,
                proposal.author,
                priority_text,
                f"{proposal.estimated_cost:,.0f} руб." if proposal.estimated_cost else "Не указана",
                proposal.created_date.strftime("%d.%m.%Y")
            ))
        
        # Обновляем статистику
        stats = self.db.get_statistics()
        self.stats_label.config(
            text=f"Всего предложений: {stats['total']} | Общая стоимость: {stats['total_cost']:,.0f} руб."
        )
    
    def get_selected_proposal_id(self):
        """Получение ID выбранного предложения"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item['values'][0]  # ID находится в первом столбце
        return None
    
    def view_proposal(self):
        """Просмотр выбранного предложения"""
        proposal_id = self.get_selected_proposal_id()
        if proposal_id:
            self.controller.show_details_form(proposal_id)
        else:
            messagebox.showwarning("Внимание", "Выберите предложение для просмотра")
    
    def edit_proposal(self):
        """Редактирование выбранного предложения"""
        proposal_id = self.get_selected_proposal_id()
        if proposal_id:
            self.controller.show_add_form(proposal_id, edit=True)
        else:
            messagebox.showwarning("Внимание", "Выберите предложение для редактирования")
    
    def delete_proposal(self):
        """Удаление выбранного предложения"""
        proposal_id = self.get_selected_proposal_id()
        if proposal_id:
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это предложение?"):
                self.db.delete_proposal(proposal_id)
                self.load_proposals()
                messagebox.showinfo("Успех", "Предложение успешно удалено")
        else:
            messagebox.showwarning("Внимание", "Выберите предложение для удаления")
    
    def on_item_double_click(self, event):
        """Обработка двойного клика по предложению"""
        self.view_proposal()

class AddProposalForm(tk.Toplevel):
    """Форма добавления/редактирования предложения"""
    def __init__(self, parent, controller, proposal_id=None, edit=False):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.proposal_id = proposal_id
        self.edit_mode = edit
        self.proposal = None
        
        if edit and proposal_id:
            self.proposal = self.db.get_proposal_by_id(proposal_id)
            title = "Редактирование предложения"
        else:
            title = "Добавление нового предложения"
        
        self.title(title)
        self.geometry("600x700")
        self.resizable(False, False)
        self.setup_ui()
        
        if self.proposal:
            self.load_proposal_data()
    
    def setup_ui(self):
        # Основной фрейм с прокруткой
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Поля формы
        row = 0
        
        # Название
        tk.Label(self.scrollable_frame, text="Название предложения*:").grid(row=row, column=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(self.scrollable_frame, width=50)
        self.title_entry.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Категория
        tk.Label(self.scrollable_frame, text="Категория*:").grid(row=row, column=0, sticky="w", pady=5)
        self.category_combo = ttk.Combobox(
            self.scrollable_frame,
            values=[category.value for category in Category],
            state="readonly",
            width=47
        )
        self.category_combo.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Описание
        tk.Label(self.scrollable_frame, text="Описание*:").grid(row=row, column=0, sticky="nw", pady=5)
        self.description_text = tk.Text(self.scrollable_frame, width=50, height=5)
        self.description_text.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Ожидаемая польза
        tk.Label(self.scrollable_frame, text="Ожидаемая польза:").grid(row=row, column=0, sticky="nw", pady=5)
        self.benefit_text = tk.Text(self.scrollable_frame, width=50, height=3)
        self.benefit_text.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Автор
        tk.Label(self.scrollable_frame, text="Автор*:").grid(row=row, column=0, sticky="w", pady=5)
        self.author_entry = tk.Entry(self.scrollable_frame, width=50)
        self.author_entry.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Отдел
        tk.Label(self.scrollable_frame, text="Отдел*:").grid(row=row, column=0, sticky="w", pady=5)
        self.department_entry = tk.Entry(self.scrollable_frame, width=50)
        self.department_entry.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Приоритет
        tk.Label(self.scrollable_frame, text="Приоритет*:").grid(row=row, column=0, sticky="w", pady=5)
        self.priority_var = tk.IntVar(value=3)
        priority_frame = tk.Frame(self.scrollable_frame)
        priority_frame.grid(row=row, column=1, pady=5, padx=5, sticky="w")
        
        tk.Radiobutton(priority_frame, text="Высокий (1)", variable=self.priority_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(priority_frame, text="Средний (2)", variable=self.priority_var, value=2).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(priority_frame, text="Низкий (3)", variable=self.priority_var, value=3).pack(side=tk.LEFT)
        row += 1
        
        # Статус
        tk.Label(self.scrollable_frame, text="Статус*:").grid(row=row, column=0, sticky="w", pady=5)
        self.status_combo = ttk.Combobox(
            self.scrollable_frame,
            values=[status.value for status in Status],
            state="readonly",
            width=47
        )
        self.status_combo.grid(row=row, column=1, pady=5, padx=5)
        self.status_combo.set(Status.NEW.value)
        row += 1
        
        # Стоимость
        tk.Label(self.scrollable_frame, text="Ориентировочная стоимость (руб.):").grid(row=row, column=0, sticky="w", pady=5)
        self.cost_entry = tk.Entry(self.scrollable_frame, width=50)
        self.cost_entry.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Время реализации
        tk.Label(self.scrollable_frame, text="Срок реализации:").grid(row=row, column=0, sticky="w", pady=5)
        self.time_entry = tk.Entry(self.scrollable_frame, width=50)
        self.time_entry.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Риски
        tk.Label(self.scrollable_frame, text="Потенциальные риски:").grid(row=row, column=0, sticky="nw", pady=5)
        self.risks_text = tk.Text(self.scrollable_frame, width=50, height=3)
        self.risks_text.grid(row=row, column=1, pady=5, padx=5)
        row += 1
        
        # Кнопки
        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(
            button_frame,
            text="💾 Сохранить",
            command=self.save_proposal,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="❌ Отмена",
            command=self.destroy,
            bg="gray",
            fg="white",
            font=("Arial", 10),
            width=15
        ).pack(side=tk.LEFT, padx=10)
    
    def load_proposal_data(self):
        """Загрузка данных предложения в форму"""
        if self.proposal:
            self.title_entry.insert(0, self.proposal.title)
            self.category_combo.set(self.proposal.category.value)
            self.description_text.insert("1.0", self.proposal.description)
            self.benefit_text.insert("1.0", self.proposal.expected_benefit)
            self.author_entry.insert(0, self.proposal.author)
            self.department_entry.insert(0, self.proposal.department)
            self.priority_var.set(self.proposal.priority)
            self.status_combo.set(self.proposal.status.value)
            self.cost_entry.insert(0, str(self.proposal.estimated_cost))
            self.time_entry.insert(0, self.proposal.implementation_time)
            self.risks_text.insert("1.0", self.proposal.risks)
    
    def save_proposal(self):
        """Сохранение предложения"""
        try:
            # Проверка обязательных полей
            if not self.title_entry.get().strip():
                messagebox.showerror("Ошибка", "Введите название предложения")
                return
            
            if not self.category_combo.get():
                messagebox.showerror("Ошибка", "Выберите категорию")
                return
            
            if not self.description_text.get("1.0", tk.END).strip():
                messagebox.showerror("Ошибка", "Введите описание")
                return
            
            if not self.author_entry.get().strip():
                messagebox.showerror("Ошибка", "Введите автора")
                return
            
            if not self.department_entry.get().strip():
                messagebox.showerror("Ошибка", "Введите отдел")
                return
            
            # Создание объекта предложения
            proposal = Proposal(
                title=self.title_entry.get().strip(),
                description=self.description_text.get("1.0", tk.END).strip(),
                category=Category(self.category_combo.get()),
                status=Status(self.status_combo.get()),
                author=self.author_entry.get().strip(),
                department=self.department_entry.get().strip(),
                priority=self.priority_var.get(),
                expected_benefit=self.benefit_text.get("1.0", tk.END).strip(),
                implementation_time=self.time_entry.get().strip(),
                risks=self.risks_text.get("1.0", tk.END).strip()
            )
            
            # Обработка стоимости
            try:
                cost = float(self.cost_entry.get().strip() or 0)
                proposal.estimated_cost = cost
            except ValueError:
                proposal.estimated_cost = 0.0
            
            # Сохранение в БД
            if self.edit_mode and self.proposal_id:
                proposal.id = self.proposal_id
                proposal.created_date = self.proposal.created_date
                self.db.update_proposal(proposal)
                messagebox.showinfo("Успех", "Предложение успешно обновлено")
            else:
                self.db.add_proposal(proposal)
                messagebox.showinfo("Успех", "Предложение успешно добавлено")
            
            # Обновление главной формы и закрытие
            self.controller.main_form.load_proposals()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить предложение: {str(e)}")

class DetailsForm(tk.Toplevel):
    """Форма просмотра деталей предложения"""
    def __init__(self, parent, controller, proposal_id):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.proposal_id = proposal_id
        self.proposal = self.db.get_proposal_by_id(proposal_id)
        
        if not self.proposal:
            messagebox.showerror("Ошибка", "Предложение не найдено")
            self.destroy()
            return
        
        self.title(f"Просмотр предложения #{proposal_id}")
        self.geometry("600x600")
        self.resizable(False, False)
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(
            main_frame,
            text=f"📄 {self.proposal.title}",
            font=("Arial", 12, "bold"),
            wraplength=550,
            justify="left"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Информационная таблица
        info_frame = tk.LabelFrame(main_frame, text="Основная информация", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_data = [
            ("ID:", str(self.proposal.id)),
            ("Категория:", self.proposal.category.value),
            ("Статус:", self.proposal.status.value),
            ("Автор:", self.proposal.author),
            ("Отдел:", self.proposal.department),
            ("Приоритет:", {1: "Высокий", 2: "Средний", 3: "Низкий"}.get(self.proposal.priority, "Не указан")),
            ("Дата создания:", self.proposal.created_date.strftime("%d.%m.%Y %H:%M")),
            ("Срок реализации:", self.proposal.implementation_time or "Не указан"),
            ("Стоимость:", f"{self.proposal.estimated_cost:,.0f} руб." if self.proposal.estimated_cost else "Не указана")
        ]
        
        for i, (label, value) in enumerate(info_data):
            tk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(info_frame, text=value, font=("Arial", 9)).grid(row=i, column=1, sticky="w", pady=2, padx=10)
        
        # Описание
        desc_frame = tk.LabelFrame(main_frame, text="Описание", padx=10, pady=10)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, font=("Arial", 9))
        desc_text.insert("1.0", self.proposal.description)
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X)
        
        # Ожидаемая польза
        if self.proposal.expected_benefit:
            benefit_frame = tk.LabelFrame(main_frame, text="Ожидаемая польза", padx=10, pady=10)
            benefit_frame.pack(fill=tk.X, pady=(0, 15))
            
            benefit_text = tk.Text(benefit_frame, height=2, wrap=tk.WORD, font=("Arial", 9))
            benefit_text.insert("1.0", self.proposal.expected_benefit)
            benefit_text.config(state=tk.DISABLED)
            benefit_text.pack(fill=tk.X)
        
        # Риски
        if self.proposal.risks:
            risks_frame = tk.LabelFrame(main_frame, text="Потенциальные риски", padx=10, pady=10)
            risks_frame.pack(fill=tk.X, pady=(0, 15))
            
            risks_text = tk.Text(risks_frame, height=2, wrap=tk.WORD, font=("Arial", 9))
            risks_text.insert("1.0", self.proposal.risks)
            risks_text.config(state=tk.DISABLED)
            risks_text.pack(fill=tk.X)
        
        # Кнопки
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="✏️ Редактировать",
            command=self.edit_proposal,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🖨️ Печать",
            command=self.print_proposal,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="❌ Закрыть",
            command=self.destroy,
            bg="gray",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
    
    def edit_proposal(self):
        """Переход к редактированию предложения"""
        self.controller.show_add_form(self.proposal_id, edit=True)
        self.destroy()
    
    def print_proposal(self):
        """Печать предложения"""
        try:
            from report_generator import ReportGenerator
            generator = ReportGenerator(self.db)
            
            # Пробуем PDF, если не получится - TXT
            try:
                pdf_path = generator.generate_proposal_pdf(self.proposal)
                messagebox.showinfo("Успех", f"PDF отчет сохранен:\n{pdf_path}")
            except Exception as pdf_error:
                print(f"PDF не создан: {pdf_error}")
                txt_path = generator.generate_proposal_report(self.proposal)
                messagebox.showinfo("Успех", f"Текстовый отчет сохранен:\n{txt_path}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчет: {str(e)}")

class ReportForm(tk.Toplevel):
    """Форма формирования отчетов"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        self.title("📊 Формирование отчетов")
        self.geometry("500x600")
        self.resizable(False, False)
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="Формирование отчетов",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Статистика
        stats = self.db.get_statistics()
        
        stats_frame = tk.LabelFrame(main_frame, text="Текущая статистика", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            stats_frame,
            text=f"Всего предложений: {stats['total']}",
            font=("Arial", 10)
        ).pack(anchor="w", pady=2)
        
        tk.Label(
            stats_frame,
            text=f"Общая стоимость: {stats['total_cost']:,.0f} руб.",
            font=("Arial", 10)
        ).pack(anchor="w", pady=2)
        
        # Варианты отчетов
        report_frame = tk.LabelFrame(main_frame, text="Тип отчета", padx=10, pady=10)
        report_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.report_type = tk.StringVar(value="full")
        
        tk.Radiobutton(
            report_frame,
            text="Полный отчет (все предложения)",
            variable=self.report_type,
            value="full",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            report_frame,
            text="Отчет по статусам",
            variable=self.report_type,
            value="status",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            report_frame,
            text="Отчет по категориям",
            variable=self.report_type,
            value="category",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            report_frame,
            text="Финансовый отчет",
            variable=self.report_type,
            value="financial",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        # Формат отчета
        format_frame = tk.LabelFrame(main_frame, text="Формат отчета", padx=10, pady=10)
        format_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.format_type = tk.StringVar(value="pdf")
        
        tk.Radiobutton(
            format_frame,
            text="PDF документ",
            variable=self.format_type,
            value="pdf",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            format_frame,
            text="Текстовый файл",
            variable=self.format_type,
            value="txt",
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        # Кнопки
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="🖨️ Сформировать отчет",
            command=self.generate_report,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="❌ Закрыть",
            command=self.destroy,
            bg="gray",
            fg="white",
            font=("Arial", 10),
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def generate_report(self):
        """Генерация отчета"""
        try:
            from report_generator import ReportGenerator
            generator = ReportGenerator(self.db)
            
            report_type = self.report_type.get()
            format_type = self.format_type.get()
            
            if report_type == "full":
                file_path = generator.generate_full_report(format_type)
            elif report_type == "status":
                file_path = generator.generate_status_report(format_type)
            elif report_type == "category":
                file_path = generator.generate_category_report(format_type)
            elif report_type == "financial":
                file_path = generator.generate_financial_report(format_type)
            else:
                file_path = generator.generate_full_report(format_type)
            
            messagebox.showinfo("Успех", f"Отчет сохранен:\n{file_path}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать отчет: {str(e)}")