#!/bin/bash
rm -rf git-task/
mkdir git-task/
cd git-task/
git init
git branch -m master main
echo "print('Hello, world!')" > main.py
git add main.py
git commit -m 'Greetings'
