

SUPPORTED_DATA_TYPES = {'int', 'str', 'bool'}


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


def drop_table(metadata, table_name):
    """Delete a table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список существующих таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for table_name in metadata:
        print(f"- {table_name}")