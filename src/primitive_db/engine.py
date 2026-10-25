import shlex

import prompt
from prettytable import PrettyTable

from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import (
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
)
from .utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA = "db_meta.json"



def print_help():
    """Prints the help message for the current mode."""

    print("\n*** Процесс работы с таблицами ***")
    print("Функции:")
    print(
        "create_table <имя_таблицы> <столбец1:тип> ... "
        "- создать таблицу"
    )
    print("list_tables - показать список всех таблиц")
    print("drop_table <имя_таблицы> - удалить таблицу")

    print("\n*** Операции с данными ***")
    print("Функции:")
    print(
        "insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("select from <имя_таблицы> - прочитать все записи.")
    print(
        "update <имя_таблицы> set <столбец> = <новое_значение> "
        "where <столбец_условия> = <значение_условия> "
        "- обновить запись."
    )
    print(
        "delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("exit - выход из программы")
    print("help - справочная информация\n")


def show_rows(metadata, table_name, rows):
    """Выводит записи таблицы в виде таблицы."""
    table = PrettyTable()
    table.field_names = list(metadata[table_name].keys())

    for row in rows:
        table.add_row(
            [row.get(column) for column in table.field_names]
        )

    print(table)


def run():
    """Запускает основной цикл работы базы данных."""
    print_help()
    available_commands = ["help","exit", "create_table",
                        "list_tables", "drop_table", "insert",
                        "select", "update", "delete", "info"]
    while True:
        user_command = prompt.string(prompt="Введите команду: ")

        if not user_command.strip():
            continue

        try:
            args = shlex.split(user_command)
        except ValueError:
            print("Ошибка: проверьте кавычки в команде.")
            continue

        if not args:
            continue

        command = args[0].lower()

        if command not in available_commands:
            print(f'Функции {command} нет. Попробуйте снова.')
            continue

        if command == "help":
            print_help()
            continue

        elif command == "exit":
            break

        metadata = load_metadata(METADATA)

        try:
            if command == "create_table":
                table_name = args[1]
                columns = args[2:]
                result = create_table(metadata, table_name, columns)
                if result is not None:
                    save_metadata(METADATA, result)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "drop_table":
                table_name = args[1]
                result = drop_table(metadata, table_name)
                if result is not None:
                    save_metadata(METADATA, result)

            elif command == "insert":
                table_name, values = parse_insert(args)
                table_data = load_table_data(table_name)
                old_length = len(table_data)

                result = insert(metadata, table_name, values, table_data)

                if result is not None and len(result) > old_length:
                    save_table_data(table_name, result)

            elif command == "select":
                table_name, where_clause = parse_select(args)

                if table_name not in metadata:
                    print(f'Ошибка: таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(table_name)
                result = select(table_data, where_clause)
                show_rows(metadata, table_name, result)

            elif command == "update":
                table_name, set_clause, where_clause = parse_update(args)
                if table_name not in metadata:
                    print(f'Ошибка: таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(table_name)
                result = update(
                    metadata,
                    table_name,
                    table_data,
                    set_clause,
                    where_clause,
                )

                if result is not None:
                    save_table_data(table_name, result)

            elif command == "delete":
                table_name, where_clause = parse_delete(args)

                if table_name not in metadata:
                    print(f'Ошибка: таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(table_name)

                result = delete(
                    metadata,
                    table_name,
                    table_data,
                    where_clause,
                )

                if result is not None:
                    save_table_data(table_name, result)

            elif command == "info":
                table_name = args[1]
                table_data = load_table_data(table_name)
                info(metadata, table_name, table_data)

        except (ValueError, IndexError) as error:
            print(f"Ошибка команды: {error}")
