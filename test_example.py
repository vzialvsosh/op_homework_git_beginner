import os
import subprocess
import platform
from pathlib import Path
import pytest
import shutil
import sys

DIR = "demo-dir"

@pytest.fixture(scope="session", autouse=True)
def setup_demo():
    system = platform.system().lower()
    if "windows" in system:
        script = Path("windows") / "example.bat"
        cmd = ["cmd", "/c", str(script.resolve())]
    else:
        script = Path("linux") / "example.sh"
        cmd = ["bash", str(script.resolve())]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{script} упал: {result.stderr}")

    yield

    if os.path.isdir(DIR):
        shutil.rmtree(DIR)


def test_demo_directory_exists():
    assert os.path.isdir(DIR), f"Папка {DIR} не создана"


def test_calc_file_exists():
    file_path = os.path.join(DIR, "calc.py")
    assert os.path.isfile(file_path), "Файл calc.py не создан"


def test_calc_file_runs():
    proc = subprocess.run(
        [sys.executable, "calc.py"],
        input="7\n5\n",
        cwd=DIR,
        capture_output=True,
        text=True
    )
    assert proc.returncode == 0, f"calc.py завершился с ошибкой: {proc.stderr}"
    assert "Сумма: 12" in proc.stdout.strip(), f"Неверный результат: {proc.stdout}"
