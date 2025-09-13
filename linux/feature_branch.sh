#!/bin/bash
cd git-task/
git checkout -b feature/hello-name
echo -e "name = input()\nprint('Hello, ' + name)" > main.py
git add main.py
git commit -m Add_name
