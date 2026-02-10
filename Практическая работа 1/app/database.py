import sqlite3
from datetime import datetime
from models import Proposal, Category, Status

class Database:
    def __init__(self, db_name='proposals.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создание таблицы предложений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                author TEXT NOT NULL,
                department TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_date TEXT NOT NULL,
                expected_benefit TEXT,
                estimated_cost REAL,
                implementation_time TEXT,
                risks TEXT
            )
        ''')
        
        # Добавление тестовых данных, если таблица пуста
        cursor.execute("SELECT COUNT(*) FROM proposals")
        if cursor.fetchone()[0] == 0:
            self.add_sample_data()
        
        conn.commit()
        conn.close()
    
    def add_sample_data(self):
        """Добавление тестовых данных"""
        sample_proposals = [
            Proposal(
                title="Добавление модуля аналитики",
                description="Разработка модуля для анализа данных пользователей с визуализацией",
                category=Category.FUNCTIONALITY,
                status=Status.IN_PROGRESS,
                author="Иванов А.И.",
                department="Отдел аналитики",
                priority=1,
                expected_benefit="Увеличение эффективности анализа на 40%",
                estimated_cost=150000.0,
                implementation_time="3 месяца",
                risks="Необходимость обучения сотрудников"
            ),
            Proposal(
                title="Миграция на облачную инфраструктуру",
                description="Перенос системы на облачную платформу для повышения масштабируемости",
                category=Category.PERFORMANCE,
                status=Status.APPROVED,
                author="Петров С.В.",
                department="ИТ-отдел",
                priority=1,
                expected_benefit="Снижение затрат на поддержку на 30%",
                estimated_cost=250000.0,
                implementation_time="6 месяцев",
                risks="Время простоя при миграции"
            ),
            Proposal(
                title="Интеграция с CRM системой",
                description="Настройка интеграции с CRM для автоматического обмена данными",
                category=Category.INTEGRATION,
                status=Status.NEW,
                author="Сидорова М.К.",
                department="Отдел продаж",
                priority=2,
                expected_benefit="Автоматизация процессов продаж",
                estimated_cost=80000.0,
                implementation_time="2 месяца",
                risks="Совместимость API"
            )
        ]
        
        for proposal in sample_proposals:
            self.add_proposal(proposal)
    
    def add_proposal(self, proposal):
        """Добавление нового предложения"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO proposals (
                title, description, category, status, author, department,
                priority, created_date, expected_benefit, estimated_cost,
                implementation_time, risks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            proposal.title, proposal.description, proposal.category.value,
            proposal.status.value, proposal.author, proposal.department,
            proposal.priority, proposal.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            proposal.expected_benefit, proposal.estimated_cost,
            proposal.implementation_time, proposal.risks
        ))
        
        proposal.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return proposal
    
    def update_proposal(self, proposal):
        """Обновление предложения"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE proposals SET
                title = ?, description = ?, category = ?, status = ?,
                author = ?, department = ?, priority = ?,
                expected_benefit = ?, estimated_cost = ?,
                implementation_time = ?, risks = ?
            WHERE id = ?
        ''', (
            proposal.title, proposal.description, proposal.category.value,
            proposal.status.value, proposal.author, proposal.department,
            proposal.priority, proposal.expected_benefit, proposal.estimated_cost,
            proposal.implementation_time, proposal.risks, proposal.id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_proposal(self, proposal_id):
        """Удаление предложения"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM proposals WHERE id = ?', (proposal_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_proposals(self):
        """Получение всех предложений"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proposals ORDER BY priority, created_date DESC')
        rows = cursor.fetchall()
        
        proposals = []
        for row in rows:
            proposal = Proposal.from_dict({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'status': row[4],
                'author': row[5],
                'department': row[6],
                'priority': row[7],
                'created_date': row[8],
                'expected_benefit': row[9],
                'estimated_cost': row[10],
                'implementation_time': row[11],
                'risks': row[12]
            })
            proposals.append(proposal)
        
        conn.close()
        return proposals
    
    def get_proposal_by_id(self, proposal_id):
        """Получение предложения по ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
        row = cursor.fetchone()
        
        if row:
            proposal = Proposal.from_dict({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'status': row[4],
                'author': row[5],
                'department': row[6],
                'priority': row[7],
                'created_date': row[8],
                'expected_benefit': row[9],
                'estimated_cost': row[10],
                'implementation_time': row[11],
                'risks': row[12]
            })
            conn.close()
            return proposal
        
        conn.close()
        return None
    
    def get_statistics(self):
        """Получение статистики по предложениям"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Общее количество
        cursor.execute('SELECT COUNT(*) FROM proposals')
        total = cursor.fetchone()[0]
        
        # По статусам
        cursor.execute('SELECT status, COUNT(*) FROM proposals GROUP BY status')
        status_stats = dict(cursor.fetchall())
        
        # По категориям
        cursor.execute('SELECT category, COUNT(*) FROM proposals GROUP BY category')
        category_stats = dict(cursor.fetchall())
        
        # По приоритетам
        cursor.execute('SELECT priority, COUNT(*) FROM proposals GROUP BY priority')
        priority_stats = dict(cursor.fetchall())
        
        # Общая стоимость
        cursor.execute('SELECT SUM(estimated_cost) FROM proposals WHERE status != ?', (Status.REJECTED.value,))
        total_cost = cursor.fetchone()[0] or 0
        
        # Стоимость по статусам
        cursor.execute('SELECT status, SUM(estimated_cost) FROM proposals GROUP BY status')
        cost_by_status = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total': total,
            'status_stats': status_stats,
            'category_stats': category_stats,
            'priority_stats': priority_stats,
            'total_cost': total_cost,
            'cost_by_status': cost_by_status
        }