#!/bin/bash
cd git-task/
echo -e "name = input()\nprint(fHello, ' + name)" > main.py
git add main.py
git commit -m 'Broke'
