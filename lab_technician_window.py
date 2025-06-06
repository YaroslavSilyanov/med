from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QComboBox, QPushButton,
                               QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout,
                               QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
                               QScrollArea, QGridLayout, QGroupBox, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
import sys
import json
from datetime import datetime

from database_connection import db

# Единый стиль для всего приложения
GLOBAL_STYLESHEET = """
    /* Общие стили для всех виджетов */
    QWidget {
        font-family: 'Arial', sans-serif;
        color: #2c3e50;
    }

    /* Стили для QGroupBox */
    QGroupBox {
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #dfe6e9;
        border-radius: 5px;
        margin-top: 20px;
        background-color: #f8f9fa;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px 10px;
        background-color: #f8f9fa;
    }

    /* Стили для меток */
    QLabel {
        font-size: 12px;
        color: #2c3e50;
    }

    /* Стили для выпадающих списков */
    QComboBox {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 5px 10px;
        background-color: white;
        font-size: 12px;
    }

    QComboBox::drop-down {
        border-left: 1px solid #ced4da;
        padding: 0 5px;
    }

    QComboBox::down-arrow {
        width: 10px;
        height: 10px;
    }

    /* Стили для полей ввода */
    QLineEdit {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 12px;
        background-color: white;
    }

    /* Стили для таблицы */
    QTableWidget {
        border: 1px solid #ced4da;
        border-radius: 4px;
        background-color: white;
        font-size: 14px;
    }

    QTableWidget::item {
        padding: 5px;
    }

    QHeaderView::section {
        background-color: #e9ecef;
        padding: 5px;
        border: 1px solid #ced4da;
        font-weight: bold;
    }

    /* Общие стили для кнопок */
    QPushButton {
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: bold;
    }

    /* Основная кнопка (синяя) */
    QPushButton#primary {
        background-color: #007bff;
        color: white;
        border: none;
    }

    QPushButton#primary:hover {
        background-color: #0069d9;
    }

    /* Вторичная кнопка (серая) */
    QPushButton#secondary {
        background-color: #6c757d;
        color: white;
        border: none;
    }

    QPushButton#secondary:hover {
        background-color: #5a6268;
    }

    /* Кнопка успеха (зеленая) */
    QPushButton#success {
        background-color: #28a745;
        color: white;
        border: none;
    }

    QPushButton#success:hover {
        background-color: #218838;
    }

    /* Кнопка опасности (красная) */
    QPushButton#danger {
        background-color: #dc3545;
        color: white;
        border: none;
    }

    QPushButton#danger:hover {
        background-color: #c82333;
    }

    /* Кнопка информации (голубая) */
    QPushButton#info {
        background-color: #17a2b8;
        color: white;
        border: none;
    }

    QPushButton#info:hover {
        background-color: #138496;
    }

    /* Стили для QFrame */
    QFrame#infoFrame {
        background-color: #f8f9fa;
        border: 1px solid #dfe6e9;
        border-radius: 5px;
        padding: 10px;
    }
"""


class AnalysisEntryForm(QDialog):
    """Диалоговое окно для ввода результатов анализа"""

    def __init__(self, patient_name, analysis_type, parameters, parent=None):
        super().__init__(parent)
        self.patient_name = patient_name
        self.analysis_type = analysis_type
        self.parameters = parameters
        self.parameter_inputs = {}  # Словарь для хранения полей ввода

        self.setWindowTitle(f"Ввод результатов анализа: {analysis_type}")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса формы ввода"""
        layout = QVBoxLayout()

        # Заголовок с информацией
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout(info_frame)

        title_label = QLabel(f"Пациент: {self.patient_name}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(title_label)

        analysis_label = QLabel(f"Тип анализа: {self.analysis_type}")
        info_layout.addWidget(analysis_label)

        date_label = QLabel(f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
        info_layout.addWidget(date_label)

        layout.addWidget(info_frame)

        # Создание формы с полями для параметров анализа
        form_group = QGroupBox("Заполните значения параметров:")
        form_layout = QFormLayout()

        for param in self.parameters:
            param_input = QLineEdit()
            param_input.setPlaceholderText(f"Введите значение для {param}")
            form_layout.addRow(f"{param}:", param_input)
            self.parameter_inputs[param] = param_input

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Кнопки
        buttons_layout = QHBoxLayout()

        save_button = QPushButton("Сохранить")
        save_button.setObjectName("success")
        save_button.clicked.connect(self.save_analysis)

        cancel_button = QPushButton("Отмена")
        cancel_button.setObjectName("secondary")
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def save_analysis(self):
        """Сохранение результатов анализа"""
        # Проверка заполнения всех полей
        empty_fields = []
        for param, input_field in self.parameter_inputs.items():
            if not input_field.text().strip():
                empty_fields.append(param)

        if empty_fields:
            QMessageBox.warning(
                self,
                "Недостаточно данных",
                f"Пожалуйста, заполните все поля. Не заполнены: {', '.join(empty_fields)}"
            )
            return

        # Сбор данных из полей ввода
        result_data = {}
        for param, input_field in self.parameter_inputs.items():
            result_data[param] = input_field.text().strip()

        # Возвращаем результаты
        self.result_data = result_data
        self.accept()


class AnalysisResultDialog(QDialog):
    """Диалоговое окно для отображения результатов анализа в таблице"""

    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.result = result
        # Получаем детализированные данные результата анализа
        self.result_details = db.get_analysis_result_details(result['id'])
        self.setWindowTitle(f"Результаты анализа: {result['analysis_name']}")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса окна просмотра результатов"""
        layout = QVBoxLayout()

        # Информационная панель
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout(info_frame)

        title_label = QLabel(f"Пациент: {self.result['patient_name']}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(title_label)

        analysis_label = QLabel(f"Тип анализа: {self.result['analysis_name']}")
        info_layout.addWidget(analysis_label)

        # Корректная обработка даты
        result_date = self.result['result_date']
        if result_date:
            if isinstance(result_date, str):
                date_str = result_date
            else:
                date_str = result_date.strftime('%d.%m.%Y %H:%M')
        else:
            date_str = "Дата не указана"
        date_label = QLabel(f"Дата: {date_str}")
        info_layout.addWidget(date_label)

        layout.addWidget(info_frame)

        # Таблица результатов
        result_group = QGroupBox("Результаты анализа")
        result_layout = QVBoxLayout()

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)  # Столбцы: Параметр, Значение, Норма
        self.result_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Норма"])

        # Заполнение таблицы
        if self.result_details and 'parameters' in self.result_details:
            parameters = self.result_details['parameters']
            self.result_table.setRowCount(len(parameters))
            for row, param in enumerate(parameters):
                # Столбец "Параметр"
                self.result_table.setItem(row, 0, QTableWidgetItem(param['name']))

                # Столбец "Значение"
                value_item = QTableWidgetItem(str(param['value']))
                self.result_table.setItem(row, 1, value_item)

                # Столбец "Норма"
                if param['normal_min'] is not None and param['normal_max'] is not None:
                    norm_text = f"{param['normal_min']} - {param['normal_max']} {param['unit']}"
                else:
                    norm_text = "Не указано"
                norm_item = QTableWidgetItem(norm_text)
                self.result_table.setItem(row, 2, norm_item)

                # Проверка значения на соответствие норме и подсветка
                self.highlight_if_abnormal(param, value_item)
        else:
            self.result_table.setRowCount(1)
            self.result_table.setItem(0, 0, QTableWidgetItem("Данные"))
            self.result_table.setItem(0, 1, QTableWidgetItem(str(self.result['result_data'])))
            self.result_table.setItem(0, 2, QTableWidgetItem("Не указано"))

        # Настройка таблицы
        self.result_table.resizeColumnsToContents()
        self.result_table.setSortingEnabled(True)
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.setObjectName("secondary")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def highlight_if_abnormal(self, param, value_item):
        """Подсветка значения красным, если оно выходит за пределы нормы"""
        import re
        try:
            value_str = str(param['value']).replace(',', '.')
            match = re.search(r"\d+\.?\d*", value_str)
            value = float(match.group()) if match else None

            min_val = float(str(param['normal_min']).replace(',', '.')) if param['normal_min'] else None
            max_val = float(str(param['normal_max']).replace(',', '.')) if param['normal_max'] else None

            if value is not None:
                if min_val is not None and value < min_val:
                    value_item.setForeground(QBrush(QColor("red")))
                elif max_val is not None and value > max_val:
                    value_item.setForeground(QBrush(QColor("red")))

        except Exception as e:
            print(f"[!] Ошибка при анализе нормальности значения: {e}")


class LabTechnicianWindow(QMainWindow):
    """Главное окно интерфейса лаборанта"""
    logout_signal = Signal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data

        self.setWindowTitle(f"Медицинский центр - ДЦ А-Линия Чертаново")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("aliniya.png"))

        # Применяем глобальный стиль
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # Загрузка данных для работы
        self.patients = db.get_all_patients()
        self.analysis_types = db.get_all_analysis_types()

        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)

        # Верхняя панель с информацией о пользователе и кнопками
        top_panel = QHBoxLayout()

        user_info = QLabel(f"Лаборант: {self.user_data['full_name']}")
        user_info.setFont(QFont("Arial", 12, QFont.Bold))
        top_panel.addWidget(user_info)

        top_panel.addStretch()

        logout_button = QPushButton("Выйти")
        logout_button.setObjectName("danger")
        logout_button.clicked.connect(self.logout)
        top_panel.addWidget(logout_button)

        main_layout.addLayout(top_panel)

        # Добавление разделительной линии
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Панель выбора пациента и типа анализа
        selection_layout = QHBoxLayout()

        # Выбор пациента
        patient_group = QGroupBox("Выбор пациента")
        patient_layout = QVBoxLayout()

        self.patient_combo = QComboBox()
        for patient in self.patients:
            self.patient_combo.addItem(patient['full_name'], patient['id'])

        patient_layout.addWidget(self.patient_combo)

        # Добавляем фильтр для отображения пациентов без анализов
        filter_layout = QHBoxLayout()

        self.show_all_patients_button = QPushButton("Все пациенты")
        self.show_all_patients_button.setObjectName("secondary")
        self.show_all_patients_button.clicked.connect(self.show_all_patients)
        filter_layout.addWidget(self.show_all_patients_button)

        self.show_patients_without_analysis_button = QPushButton("Пациенты без анализов")
        self.show_patients_without_analysis_button.setObjectName("info")
        self.show_patients_without_analysis_button.clicked.connect(self.show_patients_without_analysis)
        filter_layout.addWidget(self.show_patients_without_analysis_button)

        patient_layout.addLayout(filter_layout)
        patient_group.setLayout(patient_layout)
        selection_layout.addWidget(patient_group)

        # Выбор типа анализа
        analysis_group = QGroupBox("Выбор типа анализа")
        analysis_layout = QVBoxLayout()

        self.analysis_combo = QComboBox()
        for analysis in self.analysis_types:
            self.analysis_combo.addItem(analysis['name'], analysis['id'])

        analysis_layout.addWidget(self.analysis_combo)
        analysis_group.setLayout(analysis_layout)
        selection_layout.addWidget(analysis_group)

        main_layout.addLayout(selection_layout)

        # Кнопка "Начать заполнение" в горизонтальном макете
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Растяжение слева

        start_button = QPushButton("Начать заполнение")
        start_button.setObjectName("primary")
        start_button.clicked.connect(self.start_analysis_entry)
        start_button.setFixedWidth(400)  # Фиксированная ширина кнопки
        button_layout.addWidget(start_button)

        button_layout.addStretch()  # Растяжение справа
        main_layout.addLayout(button_layout)

        # Таблица с ранее введенными анализами
        history_group = QGroupBox("История анализов")
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Дата", "Пациент", "Тип анализа", "Статус", "Действия"
        ])

        # Включаем сортировку
        self.history_table.setSortingEnabled(True)
        # Растягиваем таблицу на всю доступную ширину и высоту
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.verticalHeader().setStretchLastSection(False)
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group, 1)  # Добавляем stretch factor = 1 для растяжения

        # Загрузка истории анализов
        self.load_analysis_history()

    def load_analysis_history(self):
        """Загрузка истории анализов, выполненных текущим лаборантом"""
        analysis_results = db.fetch_all("""
            SELECT ar.*, p.full_name as patient_name, at.name as analysis_name 
            FROM analysis_results ar
            JOIN patients p ON ar.patient_id = p.id
            JOIN analysis_types at ON ar.analysis_type_id = at.id
            WHERE ar.lab_user_id = ?
            ORDER BY ar.result_date DESC
        """, (self.user_data['id'],))

        self.history_table.setRowCount(len(analysis_results))

        for row, result in enumerate(analysis_results):
            # Дата (столбец 0)
            result_date = result['result_date']
            if result_date:
                if isinstance(result_date, str):
                    date_str = result_date
                else:
                    date_str = result_date.strftime('%d.%m.%Y %H:%M')
            else:
                date_str = ""

            self.history_table.setItem(row, 0, QTableWidgetItem(date_str))

            # Пациент (столбец 1)
            self.history_table.setItem(row, 1, QTableWidgetItem(result['patient_name']))

            # Тип анализа (столбец 2)
            self.history_table.setItem(row, 2, QTableWidgetItem(result['analysis_name']))

            # Статус (столбец 3)
            status_text = {
                'pending': 'В обработке',
                'completed': 'Выполнен',
                'sent': 'Отправлен'
            }.get(result['status'], result['status'])

            status_item = QTableWidgetItem(status_text)
            self.history_table.setItem(row, 3, status_item)

            # Кнопка действий (столбец 4)
            view_button = QPushButton("Просмотр")
            view_button.setObjectName("primary")
            view_button.clicked.connect(lambda checked, r=result: self.view_analysis_result(r))
            self.history_table.setCellWidget(row, 4, view_button)

        # Установка высоты строк
        for row in range(self.history_table.rowCount()):
            self.history_table.setRowHeight(row, 60)  # Увеличили высоту до 60 пикселей

        # Автоматическое растягивание столбцов
        self.history_table.resizeColumnsToContents()

    def start_analysis_entry(self):
        """Начало ввода результатов анализа"""
        # Получение выбранного пациента и типа анализа
        patient_id = self.patient_combo.currentData()
        patient_name = self.patient_combo.currentText()

        analysis_id = self.analysis_combo.currentData()
        analysis_name = self.analysis_combo.currentText()

        # Получение параметров выбранного типа анализа
        parameters = db.get_analysis_parameters(analysis_id)

        if not parameters:
            QMessageBox.warning(self, "Ошибка", "Для выбранного типа анализа не определены параметры")
            return

        # Открытие формы для ввода результатов
        entry_form = AnalysisEntryForm(patient_name, analysis_name, parameters, self)
        if entry_form.exec() == QDialog.Accepted:
            # Сохранение результатов в базу данных
            success = db.add_analysis_result(
                patient_id=patient_id,
                analysis_type_id=analysis_id,
                lab_user_id=self.user_data['id'],
                result_data=entry_form.result_data
            )

            if success:
                QMessageBox.information(
                    self,
                    "Успех",
                    "Результаты анализа успешно сохранены"
                )
                # Обновление истории анализов
                self.load_analysis_history()
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Не удалось сохранить результаты анализа"
                )

    def view_analysis_result(self, result):
        """Просмотр результатов анализа в отдельном окне с таблицей"""
        dialog = AnalysisResultDialog(result, self)
        dialog.exec()

    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logout_signal.emit()

    def show_all_patients(self):
        """Показать всех пациентов в выпадающем списке"""
        self.patient_combo.clear()
        self.patients = db.get_all_patients()
        for patient in self.patients:
            self.patient_combo.addItem(patient['full_name'], patient['id'])

        QMessageBox.information(
            self,
            "Информация",
            f"Отображены все пациенты ({len(self.patients)})"
        )

    def show_patients_without_analysis(self):
        """Показать только пациентов, у которых нет анализов выбранного типа"""
        # Получаем ID выбранного типа анализа
        analysis_id = self.analysis_combo.currentData()
        analysis_name = self.analysis_combo.currentText()

        # Получаем пациентов без анализов данного типа
        patients_without_analysis = db.get_patients_without_analysis(analysis_id)

        # Обновляем выпадающий список
        self.patient_combo.clear()
        for patient in patients_without_analysis:
            self.patient_combo.addItem(patient['full_name'], patient['id'])

        QMessageBox.information(
            self,
            "Информация",
            f"Отображены пациенты, у которых нет анализа '{analysis_name}' ({len(patients_without_analysis)})"
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)  # Применяем стиль ко всему приложению

    # Тестовый пользователь
    test_user = {
        'id': 3,
        'username': 'lab1',
        'full_name': 'Иванова Мария Петровна',
        'role': 'lab'
    }

    window = LabTechnicianWindow(test_user)
    window.show()

    sys.exit(app.exec())