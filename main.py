#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный модуль векторного редактора с CLI интерфейсом.
Обеспечивает взаимодействие пользователя с редактором через командную строку.
"""

import sys
import json
import uuid
import os
import pickle
from shape import Shape
from shapes_2d import Point, Line, Circle, Square, Rectangle, Oval, RegularPolygon
from shapes_3d import Parallelepiped, Tetrahedron


class VectorEditor:
    """Класс векторного редактора с CLI интерфейсом."""
    
    def __init__(self):
        """Инициализация редактора."""
        self.shapes = {}  # Словарь для хранения фигур (id -> фигура)
        self.next_id = 1  # Счетчик для генерации ID
        self.commands = {
            'help': self.show_help,
            'create': self.create_shape,
            'list': self.list_shapes,
            'info': self.show_shape_info,
            'delete': self.delete_shape,
            'clear': self.clear_shapes,
            'save': self.save_shapes,
            'load': self.load_shapes,
            'exit': self.exit_editor
        }
        
        # Словарь доступных типов фигур и их конструкторов
        self.shape_types = {
            'point': {
                'class': Point,
                'params': ['x', 'y'],
                'help': 'Создать точку: create point x y [name]'
            },
            'line': {
                'class': Line,
                'params': ['x1', 'y1', 'x2', 'y2'],
                'help': 'Создать отрезок: create line x1 y1 x2 y2 [name]'
            },
            'circle': {
                'class': Circle,
                'params': ['center_x', 'center_y', 'radius'],
                'help': 'Создать круг: create circle center_x center_y radius [name]'
            },
            'square': {
                'class': Square,
                'params': ['x', 'y', 'side_length'],
                'help': 'Создать квадрат: create square x y side_length [name]'
            },
            'rectangle': {
                'class': Rectangle,
                'params': ['x', 'y', 'width', 'height'],
                'help': 'Создать прямоугольник: create rectangle x y width height [name]'
            },
            'oval': {
                'class': Oval,
                'params': ['center_x', 'center_y', 'radius_x', 'radius_y'],
                'help': 'Создать овал: create oval center_x center_y radius_x radius_y [name]'
            },
            'polygon': {
                'class': RegularPolygon,
                'params': ['center_x', 'center_y', 'num_sides', 'side_length'],
                'help': 'Создать правильный многоугольник: create polygon center_x center_y num_sides side_length [name]'
            },
            'parallelepiped': {
                'class': Parallelepiped,
                'params': ['x', 'y', 'z', 'width', 'height', 'depth'],
                'help': 'Создать параллелепипед: create parallelepiped x y z width height depth [name]'
            },
            'tetrahedron': {
                'class': Tetrahedron,
                'params': ['x', 'y', 'z', 'edge_length'],
                'help': 'Создать тетраэдр: create tetrahedron x y z edge_length [name]'
            }
        }
    
    def show_help(self, args=None):
        """
        Показать справку по командам.
        
        Args:
            args: Не используется
        """
        print("\n\033[1;36mДоступные команды:\033[0m")
        print("  \033[1;37mhelp                      \033[0m- Показать эту справку")
        print("  \033[1;37mcreate <тип> <параметры>  \033[0m- Создать новую фигуру")
        print("  \033[1;37mlist                      \033[0m- Показать список всех фигур")
        print("  \033[1;37minfo <id>                 \033[0m- Показать информацию о фигуре")
        print("  \033[1;37mdelete <id>               \033[0m- Удалить фигуру")
        print("  \033[1;37mclear                     \033[0m- Удалить все фигуры")
        print("  \033[1;37msave <filename>           \033[0m- Сохранить фигуры в файл")
        print("  \033[1;37mload <filename>           \033[0m- Загрузить фигуры из файла")
        print("  \033[1;37mexit                      \033[0m- Выйти из редактора")
        
        print("\n\033[1;36mДоступные типы фигур:\033[0m")
        for shape_type, info in self.shape_types.items():
            print(f"  \033[1;37m{info['help']}\033[0m")
    
    def create_shape(self, args):
        """
        Создать новую фигуру.
        
        Args:
            args (list): Аргументы команды (тип фигуры и параметры)
        """
        if not args:
            print("\033[1;31mОшибка: Не указан тип фигуры\033[0m")
            return
        
        shape_type = args[0].lower()
        if shape_type not in self.shape_types:
            print(f"\033[1;31mОшибка: Неизвестный тип фигуры '{shape_type}'\033[0m")
            print("\033[1;33mИспользуйте 'help' для просмотра доступных типов фигур\033[0m")
            return
        
        shape_info = self.shape_types[shape_type]
        required_params = shape_info['params']
        
        # Проверяем, достаточно ли параметров
        if len(args) - 1 < len(required_params):
            print(f"\033[1;31mОшибка: Недостаточно параметров для создания фигуры '{shape_type}'\033[0m")
            print(f"\033[1;33mИспользование: {shape_info['help']}\033[0m")
            return
        
        # Извлекаем параметры
        params = args[1:len(required_params) + 1]
        
        # Проверяем, являются ли параметры числами
        try:
            # Преобразуем строковые параметры в числа
            numeric_params = []
            for param in params:
                # Для num_sides в многоугольнике нужно целое число
                if shape_type == 'polygon' and param == params[2]:
                    numeric_params.append(int(param))
                else:
                    numeric_params.append(float(param))
        except ValueError:
            print("\033[1;31mОшибка: Параметры должны быть числами\033[0m")
            return
        
        # Проверяем, указано ли имя
        name = None
        if len(args) > len(required_params) + 1:
            name = args[len(required_params) + 1]
        else:
            # Если имя не указано, используем тип фигуры с порядковым номером
            name = f"{shape_type.capitalize()} {self.next_id}"
        
        # Создаем фигуру
        try:
            shape_class = shape_info['class']
            shape = shape_class(*numeric_params, name=name)
            
            # Назначаем ID и добавляем в словарь
            shape.id = self.next_id
            self.shapes[shape.id] = shape
            self.next_id += 1
            
            print(f"\033[1;32mСоздана фигура: {shape}\033[0m")
        except Exception as e:
            print(f"\033[1;31mОшибка при создании фигуры: {e}\033[0m")
    
    def list_shapes(self, args=None):
        """
        Показать список всех фигур.
        
        Args:
            args: Не используется
        """
        if not self.shapes:
            print("\033[1;33mСписок фигур пуст\033[0m")
            return
        
        print("\n\033[1;36mСписок фигур:\033[0m")
        for shape_id, shape in self.shapes.items():
            print(f"  \033[1;34m{shape_id}\033[0m: \033[1;37m{shape}\033[0m")
    
    def show_shape_info(self, args):
        """
        Показать подробную информацию о фигуре.
        
        Args:
            args (list): Аргументы команды (ID фигуры)
        """
        if not args:
            print("\033[1;31mОшибка: Не указан ID фигуры\033[0m")
            return
        
        try:
            shape_id = int(args[0])
        except ValueError:
            print("\033[1;31mОшибка: ID должен быть числом\033[0m")
            return
        
        if shape_id not in self.shapes:
            print(f"\033[1;31mОшибка: Фигура с ID {shape_id} не найдена\033[0m")
            return
        
        shape = self.shapes[shape_id]
        info = shape.get_info()
        
        print(f"\n\033[1;36mИнформация о фигуре {shape_id}:\033[0m")
        # Форматируем JSON для лучшего отображения
        formatted_json = json.dumps(info, indent=2, ensure_ascii=False)
        # Добавляем цвета для ключей и значений
        formatted_json = formatted_json.replace('"', '\033[1;34m"\033[0m')
        formatted_json = formatted_json.replace(':', '\033[0m:')
        print(formatted_json)
    
    def delete_shape(self, args):
        """
        Удалить фигуру.
        
        Args:
            args (list): Аргументы команды (ID фигуры)
        """
        if not args:
            print("\033[1;31mОшибка: Не указан ID фигуры\033[0m")
            return
        
        try:
            shape_id = int(args[0])
        except ValueError:
            print("\033[1;31mОшибка: ID должен быть числом\033[0m")
            return
        
        if shape_id not in self.shapes:
            print(f"\033[1;31mОшибка: Фигура с ID {shape_id} не найдена\033[0m")
            return
        
        # Запрос подтверждения перед удалением
        shape = self.shapes[shape_id]
        print(f"\033[1;33mВы уверены, что хотите удалить фигуру: {shape}? (y/n)\033[0m")
        confirm = input("\033[1;32m> \033[0m").strip().lower()
        if confirm == 'y' or confirm == 'yes' or confirm == 'да':
            self.shapes.pop(shape_id)
            print(f"\033[1;32mУдалена фигура: {shape}\033[0m")
        else:
            print("\033[1;33mУдаление отменено\033[0m")
    
    def clear_shapes(self, args=None):
        """
        Удалить все фигуры.
        
        Args:
            args: Не используется
        """
        if not self.shapes:
            print("\033[1;33mСписок фигур уже пуст\033[0m")
            return
            
        count = len(self.shapes)
        # Запрос подтверждения перед удалением всех фигур
        print(f"\033[1;33mВы уверены, что хотите удалить все фигуры ({count} шт.)? (y/n)\033[0m")
        confirm = input("\033[1;32m> \033[0m").strip().lower()
        if confirm == 'y' or confirm == 'yes' or confirm == 'да':
            self.shapes.clear()
            print(f"\033[1;32mУдалено фигур: {count}\033[0m")
        else:
            print("\033[1;33mУдаление отменено\033[0m")
    
    def save_shapes(self, args):
        """
        Сохранить фигуры в файл.
        
        Args:
            args (list): Аргументы команды (имя файла)
        """
        if not args:
            print("\033[1;31mОшибка: Не указано имя файла\033[0m")
            return
        
        filename = args[0]
        
        # Добавляем расширение .shapes, если оно не указано
        if not filename.endswith('.shapes'):
            filename += '.shapes'
        
        try:
            with open(filename, 'wb') as file:
                # Создаем словарь с данными для сохранения
                data = {
                    'shapes': self.shapes,
                    'next_id': self.next_id
                }
                pickle.dump(data, file)
            print(f"\033[1;32mФигуры успешно сохранены в файл '{filename}'\033[0m")
        except Exception as e:
            print(f"\033[1;31mОшибка при сохранении фигур: {e}\033[0m")
    
    def load_shapes(self, args):
        """
        Загрузить фигуры из файла.
        
        Args:
            args (list): Аргументы команды (имя файла)
        """
        if not args:
            print("\033[1;31mОшибка: Не указано имя файла\033[0m")
            return
        
        filename = args[0]
        
        # Добавляем расширение .shapes, если оно не указано
        if not filename.endswith('.shapes'):
            filename += '.shapes'
        
        if not os.path.exists(filename):
            print(f"\033[1;31mОшибка: Файл '{filename}' не найден\033[0m")
            return
        
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                
                # Проверяем структуру загруженных данных
                if not isinstance(data, dict) or 'shapes' not in data or 'next_id' not in data:
                    print("\033[1;31mОшибка: Некорректный формат файла\033[0m")
                    return
                
                # Запрос подтверждения перед загрузкой, если есть текущие фигуры
                if self.shapes:
                    print(f"\033[1;33mВнимание: У вас уже есть {len(self.shapes)} фигур. Загрузка заменит их. Продолжить? (y/n)\033[0m")
                    confirm = input("\033[1;32m> \033[0m").strip().lower()
                    if not (confirm == 'y' or confirm == 'yes' or confirm == 'да'):
                        print("\033[1;33mЗагрузка отменена\033[0m")
                        return
                
                # Очищаем текущие фигуры и загружаем новые
                self.shapes = data['shapes']
                self.next_id = data['next_id']
                
                print(f"\033[1;32mФигуры успешно загружены из файла '{filename}'\033[0m")
                print(f"\033[1;32mЗагружено фигур: {len(self.shapes)}\033[0m")
        except Exception as e:
            print(f"\033[1;31mОшибка при загрузке фигур: {e}\033[0m")
    
    def exit_editor(self, args=None):
        """
        Выйти из редактора.
        
        Args:
            args: Не используется
        """
        print("\033[1;33mВыход из редактора\033[0m")
        sys.exit(0)
    
    def process_command(self, command_line):
        """
        Обработать введенную команду.
        
        Args:
            command_line (str): Строка с командой
        """
        # Разбиваем строку на команду и аргументы
        parts = command_line.strip().split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:]
        
        # Выполняем команду, если она существует
        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"Ошибка: Неизвестная команда '{command}'")
            print("Используйте 'help' для просмотра доступных команд")
    
    def run(self):
        """Запустить интерактивный режим редактора."""
        print("\033[1;36m" + "=" * 60 + "\033[0m")
        print("\033[1;36m" + "Векторный редактор CLI v2.0".center(60) + "\033[0m")
        print("\033[1;36m" + "=" * 60 + "\033[0m")
        print("\033[1;33mВведите 'help' для просмотра доступных команд\033[0m")
        
        while True:
            try:
                command_line = input("\n\033[1;32m> \033[0m")
                if command_line.strip():
                    self.process_command(command_line)
            except KeyboardInterrupt:
                print("\n\033[1;33mПрервано пользователем\033[0m")
                break
            except EOFError:
                print("\n\033[1;33mКонец ввода\033[0m")
                break
            except Exception as e:
                print(f"\033[1;31mОшибка: {e}\033[0m")


if __name__ == "__main__":
    editor = VectorEditor()
    editor.run()
