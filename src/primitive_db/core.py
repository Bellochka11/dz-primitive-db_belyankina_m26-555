from .decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

SUPPORTED_DATA_TYPES = {'int', 'str', 'bool'}

select_cache = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Create a table with an automatically generated ID column."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return
    new_columns = {"ID": "int"}
    for column in columns:
        if ":" not in column:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return
        name, type_ = column.split(":", 1)
        if not name or type_ not in SUPPORTED_DATA_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return
        if any(existing.lower() == name.lower() for existing in new_columns):
            print(f"Некорректное значение: {name}. Попробуйте снова.")
            return
        new_columns[name] = type_
    metadata[table_name] = new_columns
    columns_info = ", ".join(
        f"{name}:{type_}" for name, type_ in new_columns.items()
    )
    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_info}"
    )
    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Delete a table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Выводит список существующих таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for table_name in metadata:
        print(f"- {table_name}")


@log_time
@handle_db_errors
def insert(metadata, table_name, values, table_data):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name]
    user_columns = list(columns.keys())[1:]

    if len(values) != len(user_columns):
        print("Ошибка: количество значений не соответствует количеству столбцов.")
        return table_data

    new_row = {}
    for column, value in zip(user_columns, values):
        expected_type = columns[column]

        if expected_type == "int" and type(value) is not int:
            print(f'Ошибка: "{column}" должен быть int.')
            return table_data
        if expected_type == "str" and type(value) is not str:
            print(f'Ошибка: "{column}" должен быть str.')
            return table_data
        if expected_type == "bool" and type(value) is not bool:
            print(f'Ошибка: "{column}" должен быть bool.')
            return table_data

        new_row[column] = value

    new_id = max((row["ID"] for row in table_data), default=0) + 1
    new_row = {"ID": new_id, **new_row}
    table_data.append(new_row)

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )
    return table_data


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    """Возвращает записи таблицы с учётом условия фильтрации."""

    cache_key = (
        tuple(
            tuple(sorted(row.items()))
            for row in table_data
        ),
        tuple(sorted(where_clause.items())) if where_clause else None,
    )

    return select_cache(
        cache_key,
        lambda: (
            [row.copy() for row in table_data]
            if where_clause is None
            else [
                row.copy()
                for row in table_data
                if all(
                    row.get(column) == value
                    for column, value in where_clause.items()
                )
            ]
        ),
    )



@handle_db_errors
def update(metadata, table_name, table_data, set_clause, where_clause):
    """Обновляет записи таблицы по заданному условию."""

    if table_name not in metadata:
        print(f'Ошибка: таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name]

    set_column, set_value = next(iter(set_clause.items()))
    where_column, where_value = next(iter(where_clause.items()))

    if set_column not in columns:
        print(f'Ошибка: столбец "{set_column}" не существует.')
        return None

    if where_column not in columns:
        print(f'Ошибка: столбец "{where_column}" не существует.')
        return None

    if set_column == "ID":
        print("Ошибка: нельзя изменять столбец ID.")
        return None

    expected_type = columns[set_column]
    valid_types = {
        "int": int,
        "str": str,
        "bool": bool,
    }

    if type(set_value) is not valid_types[expected_type]:
        print(
            f'Ошибка: столбец "{set_column}" '
            f'должен иметь тип {expected_type}.'
        )
        return None

    if type(where_value) is not valid_types[columns[where_column]]:
        print(
            f'Ошибка: столбец "{where_column}" '
            f'должен иметь тип {columns[where_column]}.'
        )
        return None

    matching_rows = [
        row for row in table_data
        if row.get(where_column) == where_value
    ]

    if not matching_rows:
        print("Совпадающих записей не найдено.")
        return None

    for row in matching_rows:
        row[set_column] = set_value

    print(f"Обновлено записей: {len(matching_rows)}.")
    return table_data



@confirm_action("удаление записей")
@handle_db_errors
def delete(metadata, table_name, table_data, where_clause):
    """Удаляет записи, соответствующие условию."""

    if table_name not in metadata:
        print(f'Ошибка: таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name]

    for column in where_clause:
        if column not in columns:
            print(f'Ошибка: столбец "{column}" не существует.')
            return None

    matching_rows = [
        row
        for row in table_data
        if all(
            row.get(column) == value
            for column, value in where_clause.items()
        )
    ]

    if not matching_rows:
        print("Совпадающих записей не найдено.")
        return None

    result = [
        row
        for row in table_data
        if not all(
            row.get(column) == value
            for column, value in where_clause.items()
        )
    ]

    print(f"Удалено записей: {len(matching_rows)}.")
    return result


@handle_db_errors
def info(metadata, table_name, table_data):
    """Выводит информацию о таблице и количестве записей."""
    if table_name not in metadata:
        print(f'Ошибка: таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]
    columns_info = ", ".join(
        f"{column}:{data_type}"
        for column, data_type in columns.items()
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_info}")
    print(f"Количество записей: {len(table_data)}")
