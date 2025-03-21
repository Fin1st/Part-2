#!/usr/bin/env python3
import os
import subprocess
import time

# Функция для запуска команды и получения вывода
def run_command(command, inputs=None):
    print(f"\n\033[1;35m>>> Выполняем команду: {command}\033[0m")
    
    process = subprocess.Popen(
        ['python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Даем время на запуск программы
    time.sleep(0.5)
    
    # Отправляем команду
    process.stdin.write(command + '\n')
    process.stdin.flush()
    
    # Если есть дополнительные входные данные
    if inputs:
        for input_data in inputs:
            time.sleep(0.3)
            process.stdin.write(input_data + '\n')
            process.stdin.flush()
    
    # Даем время на выполнение
    time.sleep(0.5)
    
    # Отправляем команду выхода
    process.stdin.write('exit\n')
    process.stdin.flush()
    
    # Получаем вывод
    stdout, stderr = process.communicate()
    
    # Выводим результат
    print('\033[1;36mРезультат:\033[0m')
    print(stdout)
    
    if stderr:
        print('\033[1;31mОшибки:\033[0m')
        print(stderr)
    
    print('\033[1;35m' + '-' * 60 + '\033[0m')
    return stdout, stderr

# Тестирование справки
def test_help():
    print('\033[1;32m=== Тестирование справки ===\033[0m')
    run_command('help')

# Тестирование создания фигур
def test_create_shapes():
    print('\033[1;32m=== Тестирование создания фигур ===\033[0m')
    
    # Создаем точку
    run_command('create point 10 20 TestPoint')
    
    # Создаем овал (новая фигура)
    run_command('create oval 30 40 15 10 TestOval')
    
    # Создаем прямоугольник
    run_command('create rectangle 50 60 30 20 TestRectangle')
    
    # Проверяем список фигур
    run_command('list')

# Тестирование информации о фигурах
def test_shape_info():
    print('\033[1;32m=== Тестирование информации о фигурах ===\033[0m')
    
    # Создаем овал и получаем информацию о нем
    process = subprocess.Popen(
        ['python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(0.5)
    
    commands = [
        'create oval 100 100 50 30 InfoOval',
        'info 1',
        'exit'
    ]
    
    for cmd in commands:
        process.stdin.write(cmd + '\n')
        process.stdin.flush()
        time.sleep(0.3)
    
    stdout, stderr = process.communicate()
    print('\033[1;36mРезультат:\033[0m')
    print(stdout)
    
    if stderr:
        print('\033[1;31mОшибки:\033[0m')
        print(stderr)
    
    print('\033[1;35m' + '-' * 60 + '\033[0m')

# Тестирование сохранения и загрузки
def test_save_load():
    print('\033[1;32m=== Тестирование сохранения и загрузки ===\033[0m')
    
    # Создаем фигуры и сохраняем их
    process = subprocess.Popen(
        ['python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(0.5)
    
    commands = [
        'create point 5 5 SavePoint',
        'create oval 25 25 10 5 SaveOval',
        'save test_shapes',
        'list',
        'exit'
    ]
    
    for cmd in commands:
        process.stdin.write(cmd + '\n')
        process.stdin.flush()
        time.sleep(0.3)
    
    stdout, stderr = process.communicate()
    print('\033[1;36mРезультат сохранения:\033[0m')
    print(stdout)
    
    # Загружаем сохраненные фигуры
    run_command('load test_shapes')
    
    # Проверяем список загруженных фигур
    run_command('list')
    
    # Удаляем тестовый файл
    if os.path.exists('test_shapes.shapes'):
        os.remove('test_shapes.shapes')
        print('\033[1;33mТестовый файл удален\033[0m')

# Тестирование удаления фигур
def test_delete():
    print('\033[1;32m=== Тестирование удаления фигур ===\033[0m')
    
    # Создаем фигуры
    process = subprocess.Popen(
        ['python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(0.5)
    
    commands = [
        'create point 1 1 DeletePoint',
        'create oval 2 2 3 4 DeleteOval',
        'list',
        'delete 1',
        'y',
        'list',
        'clear',
        'y',
        'list',
        'exit'
    ]
    
    for cmd in commands:
        process.stdin.write(cmd + '\n')
        process.stdin.flush()
        time.sleep(0.3)
    
    stdout, stderr = process.communicate()
    print('\033[1;36mРезультат удаления:\033[0m')
    print(stdout)
    
    if stderr:
        print('\033[1;31mОшибки:\033[0m')
        print(stderr)
    
    print('\033[1;35m' + '-' * 60 + '\033[0m')

# Запуск всех тестов
def run_all_tests():
    print('\033[1;32m======= НАЧАЛО ТЕСТИРОВАНИЯ =======\033[0m')
    
    test_help()
    test_create_shapes()
    test_shape_info()
    test_save_load()
    test_delete()
    
    print('\033[1;32m======= ТЕСТИРОВАНИЕ ЗАВЕРШЕНО =======\033[0m')

# Запускаем тесты
if __name__ == '__main__':
    run_all_tests()
