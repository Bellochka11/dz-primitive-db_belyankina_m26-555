import prompt


def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = prompt.string("Введите команду: ").strip().lower()

        if command == "exit":
            break
        elif command == "help":
            continue
        else:
            print(f"Неизвестная команда: {command}")
