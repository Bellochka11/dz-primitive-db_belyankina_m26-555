import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

METADATA = "db_meta.json"


def print_help():
    """Выводит список доступных команд."""
    print("\n*** Управление таблицами ***")
    print(
        "create_table <имя_таблицы> <столбец1:тип> ... "
        "- создать таблицу"
    )
    print("list_tables - показать список всех таблиц")
    print("drop_table <имя_таблицы> - удалить таблицу")
    print("help - справочная информация")
    print("exit - выход из программы\n")


def run():
    """Запускает основной цикл работы базы данных."""
    print_help()

    while True:
        user_command = prompt.string(prompt="Введите команду: ")

        if not user_command or not user_command.strip():
            continue

        try:
            args = shlex.split(user_command)
        except ValueError:
            print("Ошибка: проверьте кавычки в команде.")
            continue

        if not args:
            continue

        command = args[0].lower()

        if command == "help":
            print_help()
            continue

        if command == "exit":
            break

        if command == "list_tables":
            if len(args) != 1:
                print("Использование: list_tables")
                continue
            metadata = load_metadata(METADATA)
            list_tables(metadata)
            continue

        if command == "create_table":
            if len(args) < 3:
                print(
                    "Использование: create_table "
                    "<имя_таблицы> <столбец1:тип> ..."
                )
                continue

            metadata = load_metadata(METADATA)
            table_name = args[1]
            columns = args[2:]
            table_existed = table_name in metadata

            create_table(metadata, table_name, columns)

            if not table_existed and table_name in metadata:
                save_metadata(METADATA, metadata)
            continue

        if command == "drop_table":
            if len(args) != 2:
                print("Использование: drop_table <имя_таблицы>")
                continue

            metadata = load_metadata(METADATA)
            table_name = args[1]
            if table_name not in metadata:
                drop_table(metadata, table_name)
                continue

            drop_table(metadata, table_name)
            save_metadata(METADATA, metadata)
            continue

        print(f"Неизвестная команда: {command}. Введите help.")