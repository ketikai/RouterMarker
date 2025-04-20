import multiprocessing
import os
import customtkinter as tk

from CTkListbox import CTkListbox
from PIL import Image
from multiprocessing import Pool

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screen_width - width) / 2, (screen_height - height) / 2)
    window.geometry(size)


def select_path():
    _path = tk.filedialog.askdirectory()
    if _path == "":
        dir_path.get()
    else:
        dir_path.set(_path.replace("\\", "/"))
    # noinspection PyTypeChecker
    selected_dir.after(100, lambda: selected_dir.xview_moveto(1))


def browse_path():
    _path = dir_path.get()
    if _path is None or _path == "":
        _path = os.path.abspath(".")
    os.startfile(_path)

IMAGE_FILE_EXTENSION = ".png"
IMAGE_FILE_EXTENSION_LEN = len(".png")


# noinspection PyUnusedLocal
def update_image_paths(*args):
    global last_dir_path, dir_path, image_paths, select_title
    _dir_path = dir_path.get()
    if last_dir_path == _dir_path:
        return
    last_dir_path = _dir_path

    _paths = []
    for file in os.listdir(_dir_path):
        _path = os.path.join(_dir_path, file)
        if os.path.isfile(_path) and file.endswith(IMAGE_FILE_EXTENSION):
            _paths.append(str(file)[:-IMAGE_FILE_EXTENSION_LEN].replace("\\", "/"))

    image_paths.set(str(_paths))
    if len(_paths) > 0:
        select_image(0)
    else:
        select_title.set("0 / 0")

showing = None


# noinspection PyUnusedLocal
def on_select(*args):
    global image_path_list, image_view, image_title, action_title, selected_action, selected_action_callback, showing
    selection = image_path_list.curselection()
    if selection is not None:
        index = selection
        _file = image_path_list.get(index)
        _dir_path = dir_path.get()
        _image = Image.open(os.path.join(_dir_path, _file + IMAGE_FILE_EXTENSION))
        ratio = min(image_view.winfo_width() / _image.width, image_view.winfo_height() / _image.height)
        new_size = (int(_image.width * ratio), int(_image.height * ratio))
        showing = tk.CTkImage(_image, size=new_size)
        # noinspection PyTypeChecker
        image_view.configure(image=showing)
        image_title.set(_file)
        _action = load_action_txt(os.path.join(_dir_path, _file + ACTION_FILE_EXTENSION))
        if _action is not None:
            selected_action_callback = False
            selected_action.set(0)
            selected_action_callback = True
            action_title.set(action_table[_action + 1])
        else:
            selected_action.set(0)
            action_title.set(action_table[0])
        select_title.set(f"{index + 1} / {image_path_list.size()}")


def select_image(index):
    global image_path_list
    # 更新选择
    image_path_list.selection_clear()
    image_path_list.see(index)
    image_path_list.select(index)


def on_key_press(event):
    global image_path_list
    _key = str(event.char).upper()
    if _key not in "AD":
        return

    current_selection = image_path_list.curselection()
    max_index = image_path_list.size() - 1

    if current_selection is None:
        if max_index < 0:
            return
        select_image(0)
        return
    else:
        new_index = current_selection

    if _key == "A":
        new_index -= 1
    elif _key == "D":
        new_index += 1
    # 边界保护
    new_index = max(0, min(new_index, max_index))
    if new_index == current_selection:
        return
    select_image(new_index)

ACTION_FILE_EXTENSION = ".txt"
def save_action_txt(action_file, content):
    if 0 <= content < 9:
        with open(action_file, "w") as f: f.write(str(content))

def load_action_txt(action_file):
    if not os.path.exists(action_file):
        return None
    with open(action_file, "r") as f:
        _action = f.readline()
        if _action and _action != "":
            _action = int(_action)
            if 0 <= _action < 9:
                return _action
        return None


# noinspection PyUnusedLocal
def update_action_txt(*args):
    global image_path_list, action_title, dir_path, selected_action, pool, selected_action_callback
    if not selected_action_callback:
        return
    selection = image_path_list.curselection()
    if selection is not None:
        index = selection
        _file = image_path_list.get(index)
        _action = selected_action.get()
        if _action > 0:
            action_file = os.path.join(dir_path.get(), _file + ACTION_FILE_EXTENSION)
            pool.apply(func=save_action_txt, args=(action_file, _action - 1,))
        action_title.set(action_table[_action])


if __name__ == '__main__':
    multiprocessing.freeze_support()
    pool = Pool(1)
    root = tk.CTk()
    root.title('RouterMarker')
    center_window(root, 1280, 720)
    root.resizable(False, False)

    image_paths = tk.Variable()
    image_paths.set("[]")
    last_dir_path = ""
    dir_path = tk.StringVar()

    dir_container = tk.CTkFrame(root)
    dir_container.pack(fill=tk.X, padx=5, pady=5)
    tk.CTkLabel(dir_container, text="数据集路径").pack(side=tk.LEFT, fill=tk.X, padx=2, ipadx=5)
    selected_dir = tk.CTkEntry(dir_container, textvariable=dir_path, state="readonly")
    selected_dir.xview_moveto(1)
    selected_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    dir_path.trace_add("write", callback=update_image_paths)
    tk.CTkButton(dir_container, text="选择", command=select_path).pack(side=tk.LEFT, fill=tk.X, padx=2)
    tk.CTkButton(dir_container, text="浏览", command=browse_path).pack(side=tk.LEFT, fill=tk.X, padx=2)

    image_browser = tk.CTkFrame(root)
    image_browser.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    image_container = tk.CTkFrame(image_browser)
    image_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    image_title = tk.StringVar()
    tk.CTkEntry(image_container, textvariable=image_title, state="readonly").pack(side=tk.TOP, fill=tk.X, padx=2)
    image_view = tk.CTkLabel(image_container, text="")
    image_view.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=2, pady=5)

    action_container = tk.CTkFrame(image_browser, width=150)
    action_container.pack_propagate(False)
    action_container.pack(side=tk.LEFT, fill=tk.BOTH)
    selected_action = tk.IntVar()
    action_title = tk.StringVar()
    tk.CTkEntry(action_container, textvariable=action_title, state="readonly").pack(side=tk.TOP, fill=tk.X, padx=2)
    action_table = ["无动作", "停止移动", "向上移动", "向下移动", "向左移动", "向右移动", "向左上移动", "向左下移动", "向右上移动", "向右下移动"]
    for action in range(len(action_table)):
        action_button = tk.CTkRadioButton(action_container, text=action_table[action], value=action, variable=selected_action)
        action_button.pack(side=tk.TOP, fill=tk.X, padx=2, pady=5)
    selected_action_callback = True
    selected_action.trace_add("write", update_action_txt)

    select_container = tk.CTkFrame(image_browser)
    select_container.pack(side=tk.LEFT, fill=tk.BOTH)
    select_title = tk.StringVar()
    tk.CTkEntry(select_container, textvariable=select_title, state="readonly").pack(side=tk.TOP, fill=tk.X, padx=2)
    image_path_list = CTkListbox(select_container, listvariable=image_paths, command=on_select)
    image_path_list.pack(fill=tk.BOTH, expand=True, padx=2)

    dir_path.set(os.path.abspath("."))
    selected_action.set(0)
    select_title.set("0 / 0")
    root.bind("<KeyRelease>", on_key_press)
    root.mainloop()
    pool.close()
    pool.join()
