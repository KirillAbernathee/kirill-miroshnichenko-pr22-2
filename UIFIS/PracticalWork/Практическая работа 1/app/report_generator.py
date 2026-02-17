from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from models import Status, Category

class ReportGenerator:
    def __init__(self, database):
        self.db = database
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Регистрируем шрифты с поддержкой кириллицы
        self._register_fonts()
    
    def _register_fonts(self):
        """Регистрация шрифтов с поддержкой кириллицы"""
        try:
            # Сначала попробуем зарегистрировать Arial с разными вариантами
            fonts_registered = False
            
            # Проверяем локальную папку fonts
            fonts_dir = "fonts"
            if os.path.exists(fonts_dir):
                arial_path = os.path.join(fonts_dir, "arial.ttf")
                arialbd_path = os.path.join(fonts_dir, "arialbd.ttf")
                
                if os.path.exists(arial_path):
                    pdfmetrics.registerFont(TTFont('Arial', arial_path))
                    if os.path.exists(arialbd_path):
                        pdfmetrics.registerFont(TTFont('Arial-Bold', arialbd_path))
                    else:
                        # Если нет жирного, используем обычный для обоих
                        pdfmetrics.registerFont(TTFont('Arial-Bold', arial_path))
                    self.default_font = 'Arial'
                    fonts_registered = True
                    print("Шрифты зарегистрированы из локальной папки 'fonts'")
            
            # Стандартные пути Windows
            if not fonts_registered:
                windows_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/arialbd.ttf",
                    "C:/Windows/Fonts/times.ttf",
                    "C:/Windows/Fonts/timesbd.ttf"
                ]
                
                for font_path in windows_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Arial', font_path))
                        # Для жирного используем тот же файл если нет отдельного
                        pdfmetrics.registerFont(TTFont('Arial-Bold', font_path))
                        self.default_font = 'Arial'
                        fonts_registered = True
                        print("Шрифты зарегистрированы из системной папки Windows")
                        break
            
            # Если ничего не нашли, используем Helvetica
            if not fonts_registered:
                self.default_font = 'Helvetica'
                print("Внимание: Используется стандартный шрифт Helvetica (возможны проблемы с кириллицей)")
            
        except Exception as e:
            print(f"Ошибка регистрации шрифтов: {e}")
            self.default_font = 'Helvetica'
    
    def _get_paragraph_style(self, style_name, parent_style, **kwargs):
        """Создание стиля параграфа с нужным шрифтом"""
        # Для жирного шрифта используем правильное имя
        font_name = kwargs.get('fontName', self.default_font)
        if 'bold' in style_name.lower() or ('fontName' in kwargs and 'bold' in kwargs['fontName'].lower()):
            font_name = f"{self.default_font}-Bold"
        
        style = ParagraphStyle(
            style_name,
            parent=parent_style,
            fontName=font_name,
            **{k: v for k, v in kwargs.items() if k != 'fontName'}
        )
        return style
    
    def _get_filepath(self, report_name, format_type):
        """Получение пути к файлу отчета"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Убираем русские символы из имени файла для избежания проблем
        safe_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in report_name)
        filename = f"{safe_name}_{timestamp}.{format_type}"
        return os.path.join(self.reports_dir, filename)
    
    def generate_proposal_pdf(self, proposal):
        """Генерация PDF для конкретного предложения"""
        filename = self._get_filepath(f"proposal_{proposal.id}", "pdf")
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Настраиваем стили с русскими шрифтами
        title_style = self._get_paragraph_style(
            'CustomTitle',
            styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        
        normal_style = self._get_paragraph_style(
            'Normal',
            styles['Normal'],
            fontSize=10
        )
        
        bold_style = self._get_paragraph_style(
            'Bold',
            styles['Normal'],
            fontSize=10
        )
        
        # Заголовок
        story.append(Paragraph(f"Предложение по расширению ИС №{proposal.id}", title_style))
        
        # Основная информация
        data = [
            ["Название:", proposal.title],
            ["Категория:", proposal.category.value],
            ["Статус:", proposal.status.value],
            ["Автор:", proposal.author],
            ["Отдел:", proposal.department],
            ["Приоритет:", {1: "Высокий", 2: "Средний", 3: "Низкий"}.get(proposal.priority, "Не указан")],
            ["Дата создания:", proposal.created_date.strftime("%d.%m.%Y %H:%M")],
            ["Срок реализации:", proposal.implementation_time or "Не указан"],
            ["Стоимость:", f"{proposal.estimated_cost:,.0f} руб." if proposal.estimated_cost else "Не указана"]
        ]
        
        table = Table(data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.default_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Описание
        story.append(Paragraph("<b>Описание:</b>", bold_style))
        story.append(Paragraph(proposal.description, normal_style))
        
        # Ожидаемая польза
        if proposal.expected_benefit:
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Ожидаемая польза:</b>", bold_style))
            story.append(Paragraph(proposal.expected_benefit, normal_style))
        
        # Риски
        if proposal.risks:
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Потенциальные риски:</b>", bold_style))
            story.append(Paragraph(proposal.risks, normal_style))
        
        # Подпись
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Сформировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", normal_style))
        
        doc.build(story)
        return filename
    
    def generate_full_report(self, format_type='pdf'):
        """Полный отчет по всем предложениям"""
        proposals = self.db.get_all_proposals()
        stats = self.db.get_statistics()
        
        if format_type == 'pdf':
            return self._generate_full_pdf_report(proposals, stats, "full_report")
        else:
            return self._generate_full_text_report(proposals, stats, "full_report")
    
    def _generate_full_pdf_report(self, proposals, stats, report_name):
        """Генерация полного PDF отчета"""
        filename = self._get_filepath(report_name, "pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Создаем стили с русскими шрифтами
        title_style = self._get_paragraph_style(
            'TitleStyle',
            styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1
        )
        
        heading2_style = self._get_paragraph_style(
            'Heading2',
            styles['Heading2'],
            fontSize=12,
            spaceAfter=10
        )
        
        heading3_style = self._get_paragraph_style(
            'Heading3',
            styles['Heading3'],
            fontSize=11,
            spaceAfter=5
        )
        
        normal_style = self._get_paragraph_style(
            'Normal',
            styles['Normal'],
            fontSize=10
        )
        
        # Заголовок
        story.append(Paragraph("ПОЛНЫЙ ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ РАСШИРЕНИЯ ИС", title_style))
        story.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Статистика
        story.append(Paragraph("СТАТИСТИКА:", heading2_style))
        
        stats_data = [
            ["Всего предложений:", str(stats['total'])],
            ["Общая стоимость:", f"{stats['total_cost']:,.0f} руб."],
            ["Предложений в работе:", str(stats['status_stats'].get(Status.IN_PROGRESS.value, 0))],
            ["Утверждено предложений:", str(stats['status_stats'].get(Status.APPROVED.value, 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[200, 200])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, -1), self.default_font),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Распределение по статусам
        if stats['status_stats']:
            story.append(Paragraph("Распределение по статусам:", heading3_style))
            
            status_data = [["Статус", "Количество", "Доля, %"]]
            total = stats['total']
            for status, count in stats['status_stats'].items():
                percentage = (count / total * 100) if total > 0 else 0
                status_data.append([status, str(count), f"{percentage:.1f}%"])
            
            status_table = Table(status_data, colWidths=[150, 100, 100])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), f"{self.default_font}"),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(status_table)
            story.append(Spacer(1, 20))
        
        # Распределение по категориям
        if stats['category_stats']:
            story.append(Paragraph("Распределение по категориям:", heading3_style))
            
            category_data = [["Категория", "Количество"]]
            for category, count in stats['category_stats'].items():
                category_data.append([category, str(count)])
            
            category_table = Table(category_data, colWidths=[300, 100])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(category_table)
            story.append(Spacer(1, 20))
        
        # Таблица предложений
        story.append(PageBreak())
        story.append(Paragraph("СПИСОК ВСЕХ ПРЕДЛОЖЕНИЙ:", heading2_style))
        story.append(Spacer(1, 10))
        
        if proposals:
            headers = ["ID", "Название", "Категория", "Статус", "Автор", "Стоимость", "Дата"]
            data = [headers]
            
            for proposal in proposals:
                data.append([
                    str(proposal.id),
                    proposal.title[:30] + "..." if len(proposal.title) > 30 else proposal.title,
                    proposal.category.value[:20],
                    proposal.status.value[:15],
                    proposal.author[:15],
                    f"{proposal.estimated_cost:,.0f} руб." if proposal.estimated_cost else "-",
                    proposal.created_date.strftime("%d.%m.%Y")
                ])
            
            table = Table(data, colWidths=[30, 180, 90, 80, 70, 80, 60])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
                ('ALIGN', (6, 1), (6, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("Нет данных для отображения", normal_style))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Отчет сформирован автоматически системой управления предложениями", 
                              self._get_paragraph_style('Footer', normal_style, fontSize=8, alignment=1)))
        
        doc.build(story)
        return filename
    
    def _generate_full_text_report(self, proposals, stats, report_name):
        """Генерация полного текстового отчета"""
        filename = self._get_filepath(report_name, "txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("ПОЛНЫЙ ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ РАСШИРЕНИЯ ИС\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
            
            f.write("СТАТИСТИКА:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Всего предложений: {stats['total']}\n")
            f.write(f"Общая стоимость: {stats['total_cost']:,.0f} руб.\n\n")
            
            f.write("Распределение по статусам:\n")
            f.write("-" * 40 + "\n")
            total = stats['total']
            for status, count in stats['status_stats'].items():
                percentage = (count / total * 100) if total > 0 else 0
                f.write(f"  {status:<20} {count:>3} ({percentage:>5.1f}%)\n")
            
            f.write("\nРаспределение по категориям:\n")
            f.write("-" * 40 + "\n")
            for category, count in stats['category_stats'].items():
                f.write(f"  {category:<30} {count:>3}\n")
            
            f.write("\nРаспределение по приоритетам:\n")
            f.write("-" * 40 + "\n")
            for priority, count in stats.get('priority_stats', {}).items():
                priority_name = {1: "Высокий", 2: "Средний", 3: "Низкий"}.get(priority, f"Неизвестно ({priority})")
                f.write(f"  {priority_name:<10} {count:>3}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("СПИСОК ПРЕДЛОЖЕНИЙ:\n")
            f.write("=" * 70 + "\n\n")
            
            for i, proposal in enumerate(proposals, 1):
                f.write(f"[{i}] ID: {proposal.id}\n")
                f.write(f"    Название: {proposal.title}\n")
                f.write(f"    Категория: {proposal.category.value}\n")
                f.write(f"    Статус: {proposal.status.value}\n")
                f.write(f"    Автор: {proposal.author} | Отдел: {proposal.department}\n")
                f.write(f"    Приоритет: {proposal.priority} | Стоимость: {proposal.estimated_cost:,.0f} руб.\n")
                f.write(f"    Срок: {proposal.implementation_time or 'Не указан'} | Дата: {proposal.created_date.strftime('%d.%m.%Y')}\n")
                f.write(f"    Описание: {proposal.description[:150]}...\n")
                if proposal.expected_benefit:
                    f.write(f"    Ожидаемая польза: {proposal.expected_benefit[:100]}...\n")
                f.write("-" * 70 + "\n")
            
            f.write(f"\nВсего записей: {len(proposals)}\n")
            f.write(f"Отчет сохранен в: {filename}\n")
        
        return filename
    
    def generate_status_report(self, format_type='pdf'):
        """Отчет по статусам с детализацией"""
        proposals = self.db.get_all_proposals()
        stats = self.db.get_statistics()
        
        if format_type == 'pdf':
            return self._generate_status_pdf_report(proposals, stats, "status_report")
        else:
            return self._generate_status_text_report(proposals, stats, "status_report")
    
    def _generate_status_pdf_report(self, proposals, stats, report_name):
        """PDF отчет по статусам"""
        filename = self._get_filepath(report_name, "pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Создаем стили
        title_style = self._get_paragraph_style(
            'TitleStyle',
            styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1
        )
        
        heading2_style = self._get_paragraph_style(
            'Heading2',
            styles['Heading2'],
            fontSize=12,
            spaceAfter=10
        )
        
        normal_style = self._get_paragraph_style(
            'Normal',
            styles['Normal'],
            fontSize=10
        )
        
        # Заголовок
        story.append(Paragraph("ОТЧЕТ ПО СТАТУСАМ ПРЕДЛОЖЕНИЙ", title_style))
        story.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Группировка по статусам
        proposals_by_status = {}
        for proposal in proposals:
            status = proposal.status.value
            if status not in proposals_by_status:
                proposals_by_status[status] = []
            proposals_by_status[status].append(proposal)
        
        # Общая статистика
        story.append(Paragraph("ОБЩАЯ СТАТИСТИКА:", heading2_style))
        
        total = stats['total']
        status_data = [["Статус", "Количество", "Доля", "Сумма затрат"]]
        total_cost = 0
        
        for status in Status:
            status_value = status.value
            count = stats['status_stats'].get(status_value, 0)
            percentage = (count / total * 100) if total > 0 else 0
            
            # Подсчет стоимости для этого статуса
            status_cost = 0
            if status_value in proposals_by_status:
                for proposal in proposals_by_status[status_value]:
                    status_cost += proposal.estimated_cost
            
            total_cost += status_cost
            
            status_data.append([
                status_value,
                str(count),
                f"{percentage:.1f}%",
                f"{status_cost:,.0f} руб."
            ])
        
        status_data.append(["ВСЕГО:", str(total), "100.0%", f"{total_cost:,.0f} руб."])
        
        table = Table(status_data, colWidths=[150, 80, 80, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, 0), (-1, -1), self.default_font),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        doc.build(story)
        return filename
    
    def _generate_status_text_report(self, proposals, stats, report_name):
        """Текстовый отчет по статусам"""
        filename = self._get_filepath(report_name, "txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("ОТЧЕТ ПО СТАТУСАМ ПРЕДЛОЖЕНИЙ РАСШИРЕНИЯ ИС\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
            
            f.write("ОБЩАЯ СТАТИСТИКА ПО СТАТУСАМ:\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Статус':<25} {'Кол-во':>6} {'Доля,%':>8} {'Сумма затрат':>15}\n")
            f.write("-" * 70 + "\n")
            
            total = stats['total']
            total_cost = 0
            
            for status in Status:
                status_value = status.value
                count = stats['status_stats'].get(status_value, 0)
                percentage = (count / total * 100) if total > 0 else 0
                
                status_cost = sum(p.estimated_cost for p in proposals if p.status.value == status_value)
                total_cost += status_cost
                f.write(f"{status_value:<25} {count:>6} {percentage:>7.1f}% {status_cost:>12,.0f} руб.\n")
            
            f.write("-" * 70 + "\n")
            f.write(f"{'ВСЕГО:':<25} {total:>6} {'100.0%':>8} {total_cost:>12,.0f} руб.\n")
        
        return filename
    
    def generate_category_report(self, format_type='pdf'):
        """Отчет по категориям"""
        return self.generate_full_report(format_type)
    
    def generate_financial_report(self, format_type='pdf'):
        """Финансовый отчет"""
        proposals = self.db.get_all_proposals()
        
        if format_type == 'pdf':
            return self._generate_financial_pdf_report(proposals, "financial_report")
        else:
            return self._generate_financial_text_report(proposals, "financial_report")
    
    def _generate_financial_pdf_report(self, proposals, report_name):
        """PDF финансовый отчет"""
        filename = self._get_filepath(report_name, "pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Создаем стили
        title_style = self._get_paragraph_style(
            'TitleStyle',
            styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1
        )
        
        heading2_style = self._get_paragraph_style(
            'Heading2',
            styles['Heading2'],
            fontSize=12,
            spaceAfter=10
        )
        
        normal_style = self._get_paragraph_style(
            'Normal',
            styles['Normal'],
            fontSize=10
        )
        
        # Заголовок
        story.append(Paragraph("ФИНАНСОВЫЙ ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ", title_style))
        story.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Общая финансовая сводка
        total_cost = sum(p.estimated_cost for p in proposals)
        avg_cost = total_cost / len(proposals) if proposals else 0
        max_cost = max((p.estimated_cost for p in proposals), default=0)
        min_cost = min((p.estimated_cost for p in proposals if p.estimated_cost > 0), default=0)
        
        story.append(Paragraph("ФИНАНСОВАЯ СВОДКА:", heading2_style))
        
        summary_data = [
            ["Показатель", "Значение"],
            ["Общая стоимость всех предложений", f"{total_cost:,.0f} руб."],
            ["Средняя стоимость предложения", f"{avg_cost:,.0f} руб."],
            ["Максимальная стоимость", f"{max_cost:,.0f} руб."],
            ["Минимальная стоимость", f"{min_cost:,.0f} руб."],
            ["Количество предложений", str(len(proposals))]
        ]
        
        summary_table = Table(summary_data, colWidths=[250, 150])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, -1), self.default_font),
        ]))
        
        story.append(summary_table)
        
        doc.build(story)
        return filename
    
    def _generate_financial_text_report(self, proposals, report_name):
        """Текстовый финансовый отчет"""
        filename = self._get_filepath(report_name, "txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("ФИНАНСОВЫЙ ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ РАСШИРЕНИЯ ИС\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
            
            # Финансовая сводка
            total_cost = sum(p.estimated_cost for p in proposals)
            avg_cost = total_cost / len(proposals) if proposals else 0
            max_cost = max((p.estimated_cost for p in proposals), default=0)
            min_cost = min((p.estimated_cost for p in proposals if p.estimated_cost > 0), default=0)
            
            f.write("ФИНАНСОВАЯ СВОДКА:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Общая стоимость всех предложений: {total_cost:,.0f} руб.\n")
            f.write(f"Средняя стоимость предложения:    {avg_cost:,.0f} руб.\n")
            f.write(f"Максимальная стоимость:          {max_cost:,.0f} руб.\n")
            f.write(f"Минимальная стоимость:           {min_cost:,.0f} руб.\n")
            f.write(f"Количество предложений:          {len(proposals)}\n")
        
        return filename