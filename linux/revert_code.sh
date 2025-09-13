#!/bin/bash
cd git-task/
git revert --no-commit HEAD
git commit -m Revert
