import zipfile
import json
import tkinter as tk
from tkinter import scrolledtext


def setup():
    try:
        with open("pre_data.json", encoding="UTF-8") as file_in:
            pre_data = json.load(file_in)
        archive_path = pre_data["archive"]
        setup_path = pre_data["setup"]
    except Exception:
        print('Could not read data from pre_data.json')
        return

    #открывается интерфейс и начинается выполнение команд setup
    username = "Admin"
    root = tk.Tk()
    root.title(f"{username}@localhost Shell Emulator")
    #возможно, стоит где-то хранить все текущие данные системы, для этого заведем переменную app_context
    app_context = {"root": archive_path, "setup": setup_path}
    ui = {"root": root}
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both')
    ui['text_area'] = text_area
    #text_area.config(state=tk.DISABLED)
    try:
        with open(setup_path, encoding='UTF-8') as setup_file:
            app_context['currpath'] = app_context['root'][:-4]
            app_context['username'] = 'root'
            for line in setup_file:
                exec_command(line.strip(), app_context, ui)
            entry = tk.Entry(root)
            entry.pack(fill='x')
            ui["entry"] = entry
            entry.bind('<Return>', lambda x, data=app_context, gui=ui: execute(x, data, ui))
            #exec_command(entry)
            print_line(ui, f"{app_context['username']}@localhost: ", False)
            root.mainloop()
        root.destroy()
    except Exception as e:
        print('Error of setup', e)

def execute(x, app_context, ui):
    command = ui['entry'].get()
    print_line(ui, command, True)
    exec_command(command, app_context, ui)
    ui['entry'].delete(0, tk.END)
    print_line(ui, f"{app_context['username']}@localhost {app_context['currpath'][12:]}: ", False)

def print_line(ui, line, newline):
    if "text_area" in ui:
        ui["text_area"].configure(state='normal')
        ui["text_area"].insert(tk.END, line+"\n" if newline else line)
        ui["text_area"].configure(state='disabled')
        #ui['entry'].clear()


def exec_command(command, app_context, ui):
    if command.startswith('ls'):
        ls(app_context, ui)
    elif command.startswith('cd'):
        cd(command[3:], app_context, ui)
    elif command.startswith('exit'):
        exit(ui)
    elif command.startswith('rev'):
        rev(command[4:] if len(command) > 3 else '', app_context, ui)
    elif command.startswith('clear'):
        clear(command[6:], app_context, ui)
    else:
        raise 'Command error'
    return

def ls(app_context, ui):
    #app_context['currpath'] += '/dir_1'
    #print_line(ui, app_context['currpath'], True)
    with zipfile.ZipFile(app_context['root'], 'r') as archive:
        for filename in archive.namelist():
            if filename.startswith(app_context['currpath']) and len(filename := filename[len(app_context['currpath']) + 1:]) > 2 and (filename.count('/') == 0 or filename.count('.') == 0 and filename.count('/') == 1):
                print_line(ui, filename, True)
            #print_line(ui, file, True)

def cd(direction, app_context, ui):
    if direction == '..' or direction == '':
        app_context['currpath'] = 'file_system'
        return
    with zipfile.ZipFile(app_context['root'], 'r') as archive:
        for directory in archive.namelist():
            directory = directory[len(app_context['currpath']) + 1:-1]
            if (directory.count('/') == 0 or directory.count('.') == 0 and directory.count('/') == 1):
                if directory == direction:
                    app_context['currpath'] += '/' + directory
                    return
    print_line(ui, f'No directory {direction}', True)

def exit(ui):
    ui['root'].quit()

def rev(filepath, app_context, ui):
    #получает имя файла и выводит все строки из него задом наперед
    if (" " not in filepath and not len(filepath) == 0):
        newpath = app_context['root'][:-4] + '/' + filepath
        #newpath = get_full_path(filepath, app_context['currpath'])
        # Открываем zip-архив
        with zipfile.ZipFile(app_context['root'], 'r') as archive:
            # Проверяем, существует ли файл в архиве
            if newpath in archive.namelist():
                # Открываем файл внутри архива
                with archive.open(newpath) as file:
                    for line in file:
                        print_line(ui, line.decode('utf-8').strip()[::-1], True)
            else:
                print_line(ui, f'no such file or direction {filepath}', True)
    elif (len(filepath) == 0):
        print_line(ui, '1 argument expected, got 0', True)
    else:
        print_line(ui, f"Incorrect input {filepath}", True)

def clear(command, app_context, ui):
    if "text_area" in ui:
        ui["text_area"].configure(state='normal')
        ui["text_area"].delete('1.0', tk.END)
        ui["text_area"].configure(state='disabled')

def get_full_path(path, currpath):
    if path == '.':
        return currpath
    elif path == '..':
        return currpath[:currpath[:-1].rfind('/') + 1]
    elif path.startswith('/'):
        return path
    return currpath + path


setup()