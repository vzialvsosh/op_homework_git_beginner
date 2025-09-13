import os
import subprocess
import sys
import stat
import pytest
import platform
import shutil
from pathlib import Path

DIR = "git-task"

def _remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


@pytest.fixture(scope="session", autouse=True)
def cleanup_dir():
    if os.path.isdir(DIR):
        shutil.rmtree(DIR, onerror=_remove_readonly)
    yield
    if os.path.isdir(DIR):
        shutil.rmtree(DIR, onerror=_remove_readonly)


def run_script(script_name: str):
    system = platform.system().lower()
    if "windows" in system:
        script = Path("windows") / f"{script_name}.bat"
        cmd = ["cmd", "/c", str(script.resolve())]
    else:
        script = Path("linux") / f"{script_name}.sh"
        cmd = ["bash", str(script.resolve())]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{script} упал: {result.stderr}")


def run_cmd(cmd: str, cwd=DIR):
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Команда '{cmd}' завершилась с ошибкой: {result.stderr}")
    return result.stdout.strip()


# === Фикстуры шагов ===

@pytest.fixture(scope="session")
def step1_init():
    run_script("init_git")
    yield


@pytest.fixture(scope="session")
def step2_feature(step1_init):
    run_script("feature_branch")
    yield


@pytest.fixture(scope="session")
def step3_break(step2_feature):
    run_script("break_code")
    yield


@pytest.fixture(scope="session")
def step4_revert(step3_break):
    run_script("revert_code")
    yield

@pytest.fixture(scope="session")
def step5_merge(step4_revert):
    run_script("merge_to_main")
    yield

# === Тесты первого этапа <init_git> ===

## Проверяем что создалась директория DIR
def test_directory_exists(step1_init):
    assert os.path.isdir(DIR), f"Директория {DIR} не существует"

## Проверяем что создался репозиторий (файл .git)
def test_git_initialized(step1_init):
    assert os.path.isdir(os.path.join(DIR, ".git")), ".git не найден"
    out = run_cmd("git status")
    assert "On branch" in out, "git status не показал ветку"

## Проверяем что создался скрипт main.py
def test_main_py_exists(step1_init):
    path = os.path.join(DIR, "main.py")
    assert os.path.isfile(path), "main.py не найден"

## Проверяем что скрипт main.py исполняется и печатает "Hello, world!"
def test_main_py_hello_world(step1_init):
    proc = subprocess.run(
        [sys.executable, "main.py"],
        cwd=DIR,
        capture_output=True,
        text=True
    )
    assert proc.returncode == 0, f"main.py завершился с ошибкой: {proc.stderr}"
    assert proc.stdout.strip() == "Hello, world!", f"main.py вывел не то: {proc.stdout.strip()}"


# === Тесты второго этапа <feature_branch> ===

## Проверяем что создалась ветка "feature/hello-name"
def test_branch_created(step2_feature):
    branches = run_cmd("git branch")
    assert "feature/hello-name" in branches, "ветка feature/hello-name не создана"


## Проверяем что новый main.py содержит "input()"
def test_main_py_has_input(step2_feature):
    with open(os.path.join(DIR, "main.py"), encoding="utf-8") as f:
        code = f.read()
    assert "input(" in code, "main.py не содержит input()"


## Проверяем что "python main.py Alice" напечатает "Hello, Alice"
def test_main_py_output_with_name(step2_feature):
    proc = subprocess.run(
        [sys.executable, "main.py"],
        cwd=DIR,
        input="Alice\n",
        capture_output=True,
        text=True
    )
    assert proc.returncode == 0, f"main.py завершился с ошибкой: {proc.stderr}"
    assert "Hello, Alice" in proc.stdout.strip(), f"main.py вывел не то: {proc.stdout.strip()}"


# === Тесты третьего этапа <break_code> ===

## Проверяем что main.py сломан и падает при запуске
def test_main_py_fails(step3_break):
    proc = subprocess.run(
        [sys.executable, "main.py"],
        cwd=DIR,
        input="Bob\n",
        capture_output=True,
        text=True
    )
    assert proc.returncode != 0, "main.py должен падать, но завершился успешно"


## Проверяем изменения были закомичены
def test_changes_committed(step3_break):
    status = run_cmd("git status --porcelain")
    assert status.strip() == "", f"Есть незакоммиченные изменения:\n{status}"


# === Тесты четвертого этапа <revert_code> ===


## Проверяем что hash текущего состояния отличается от первого рабочего состояния
def test_head_changed(step2_feature, step4_revert):
    good_hash = run_cmd("git rev-parse HEAD~2")
    current_hash = run_cmd("git rev-parse HEAD")
    assert good_hash != current_hash, "HEAD не изменился после revert"

## Проверяем что последний коммит - Revert
def test_commit_message_revert(step4_revert):
    log = run_cmd("git log -1 --pretty=%B")
    assert "Revert" in log, f"Последний коммит не содержит 'Revert': {log}"

## Проверяем что после Revert код снова стал рабочим
def test_main_py_output_after_revert(step4_revert):
    proc = subprocess.run(
        [sys.executable, "main.py"],
        cwd=DIR,
        input="Charlie\n",
        capture_output=True,
        text=True
    )
    assert proc.returncode == 0, f"main.py завершился с ошибкой: {proc.stderr}"
    assert "Hello, Charlie" in proc.stdout.strip(), f"main.py вывел не то: {proc.stdout.strip()}"

# === Тесты пятого этапа <merge_to_main> ===

## Проверяем что текущая ветка main
def test_current_branch_is_main(step5_merge):
    branch = run_cmd("git branch --show-current")
    assert branch == "main", f"Текущая ветка не main, а {branch}"


## Проверяем что в ветке main последняя рабочая версия кода
def test_main_py_output_in_main(step5_merge):
    proc = subprocess.run(
        [sys.executable, "main.py"],
        cwd=DIR,
        input="Diana\n",
        capture_output=True,
        text=True
    )
    assert proc.returncode == 0, f"main.py завершился с ошибкой: {proc.stderr}"
    assert "Hello, Diana" in proc.stdout.strip(), f"main.py вывел не то: {proc.stdout.strip()}"