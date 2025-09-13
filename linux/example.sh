#!/bin/bash
DIR="demo-dir"
mkdir -p "$DIR"
cd "$DIR"

cat << EOF > calc.py
a = int(input("Введите первое число: "))
b = int(input("Введите второе число: "))
print("Сумма:", a + b)
EOF

echo "✅ Файл calc.py создан"
