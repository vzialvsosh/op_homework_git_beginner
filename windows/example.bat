@echo off
set DIR=demo-dir
mkdir %DIR%
cd %DIR%

echo a = int(input("Введите первое число: ")) > calc.py
echo b = int(input("Введите второе число: ")) >> calc.py
echo print("Сумма:", a + b) >> calc.py

echo ✅ Файл calc.py создан
