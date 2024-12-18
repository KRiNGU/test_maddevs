```markdown
# test_maddevs

Проект для тестирования функции обработки сообщений, которая разбивает текст на фрагменты с учетом максимальной длины.
```

### Структура репозитория:

- **`pyproject.toml`**: файл с описанием зависимостей проекта.
- **`msg_split.py`**: файл с основной функцией `split_message` и определением классов ошибок.
- **`tests.py`**: файл с unit тестами для проверки корректности работы.
- **`source.html`**: два файла HTML с тестовыми данными:
  - Один для тестов.
  - Один для отработки стандартного случая применения функции.

## Описание работы скрипта

### Основной скрипт (`script.py`)

Этот скрипт предназначен для вызова функции разбивки сообщения на фрагменты с заданным максимальным размером. Скрипт обрабатывает исходный HTML-файл, в котором могут быть различные теги, и разбивает его на фрагменты.

Команда `python script.py --max_len=3072 ./source.html` выполняет следующие действия:

- Загружает HTML файл из `source.html`.
- Разбивает его содержимое на фрагменты, каждый из которых не превышает максимальной длины, переданной через аргумент `--max_len`.
- Выводит фрагменты в формате ```bash fragment #{number}: {fragmen_length} chars```
- Если фрагмент не может быть разбит корректно, выбрасывается исключение.

### Основная функция (`msg_split.py`)

Функция `split_message` принимает исходное сообщение (HTML) и максимальный размер фрагмента. Она разделяет сообщение на фрагменты, добавляя теги и учитывая ограничения по длине.

Также в файле определены классы ошибок, которые обрабатывают случаи, когда фрагмент слишком велик для заданной иерархии DOM-дерева.

### Unit тесты (`tests.py`)

Файл с тестами содержит набор юнит-тестов, которые проверяют правильность работы функции `split_message`. Тестируются различные сценарии, включая стандартные случаи и крайние случаи, когда разделение невозможно.

### HTML исходные файлы

- **`source.html`**: HTML файл, который используется в тестах для отработки стандартных случаев.
- **`source_test.html`**: Тестовый файл с различными ситуациями для проверки корректности обработки.

## Установка зависимостей

Для установки зависимостей используйте инструмент управления зависимостями **Poetry**:

```bash
poetry install
```

### Пример использования Poetry

Если вы используете **Poetry**, вам нужно сначала установить Poetry (если не установлен):

```bash
pip install poetry
```

Затем установить все зависимости:

```bash
poetry install
```

Запуск скрипта через Poetry:

```bash
poetry run python script.py --max_len=3072 ./source.html
```
