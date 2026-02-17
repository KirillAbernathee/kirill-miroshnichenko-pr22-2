from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Category(Enum):
    """Категории предложений"""
    FUNCTIONALITY = "Расширение функциональности"
    PERFORMANCE = "Повышение производительности"
    SECURITY = "Безопасность"
    INTEGRATION = "Интеграция"
    UI_UX = "Улучшение интерфейса"
    OTHER = "Другое"

class Status(Enum):
    """Статусы предложений"""
    NEW = "Новое"
    IN_PROGRESS = "В работе"
    APPROVED = "Утверждено"
    REJECTED = "Отклонено"
    COMPLETED = "Завершено"

@dataclass
class Proposal:
    """Модель предложения"""
    id: int = None
    title: str = ""
    description: str = ""
    category: Category = Category.OTHER
    status: Status = Status.NEW
    author: str = ""
    department: str = ""
    priority: int = 3  # 1-высокий, 2-средний, 3-низкий
    created_date: datetime = None
    expected_benefit: str = ""
    estimated_cost: float = 0.0
    implementation_time: str = ""
    risks: str = ""
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'status': self.status.value,
            'author': self.author,
            'department': self.department,
            'priority': self.priority,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'expected_benefit': self.expected_benefit,
            'estimated_cost': self.estimated_cost,
            'implementation_time': self.implementation_time,
            'risks': self.risks
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание из словаря"""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            category=Category(data['category']),
            status=Status(data['status']),
            author=data['author'],
            department=data['department'],
            priority=data['priority'],
            created_date=datetime.strptime(data['created_date'], '%Y-%m-%d %H:%M:%S'),
            expected_benefit=data['expected_benefit'],
            estimated_cost=data['estimated_cost'],
            implementation_time=data['implementation_time'],
            risks=data['risks']
        )