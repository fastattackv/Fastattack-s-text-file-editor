import tkinter as tk
from tkinter import font
from tkinter import messagebox, filedialog, simpledialog
from sys import argv
import re
import webbrowser


# program internal functions
def save():
    """saves the entered text in the active_file, if no active_file : creates one
    """
    global active_file, saved
    data = text_box.get("1.0", "end").removesuffix("\n")
    if active_file != "":
        with open(active_file, "w") as file_opened:
            file_opened.write(data)
        reset_textbox_modified()
    else:
        create(loa=False)


def load(file=""):
    """load the file in the textbox

    :param file: file to load, if nothing entered: asks a file to load
    """
    global active_file, saved
    if (active_file != "" and close()) or active_file == "":
        if file == "":
            file = filedialog.askopenfilename(title="Open")
        if file != "":
            try:
                with open(file, "r") as file_opened:
                    data = file_opened.read()
            except FileNotFoundError:
                messagebox.showerror("Loading file", f"File {file} not found")
            except UnicodeDecodeError:
                messagebox.showerror("Reading file", f"Decoding error while reading\n{file}\nCan't read the file")
            else:
                if data == "":
                    active_file = file
                    fen.title(f"Fastattack's text file editor - {active_file} - Saved")
                else:
                    active_file = file
                    text_box.delete("1.0", "end")
                    text_box.insert("1.0", data)
                    reset_textbox_modified()


def create(loa=True):
    """asks a file name and creates a file

    :param loa: True if the file needs to be loaded after creation
    """
    global active_file
    file = filedialog.asksaveasfilename(title="Save as")
    if file != "":
        if "." not in file:
            file += ".txt"
        try:
            open(file, "x")
        except:
            messagebox.showerror("Fastattack's text file editor", "File creation failure")
        else:
            if loa:
                load(file)
            else:
                active_file = file
                save()


def close() -> bool:
    """Closes the opened file, asks to save if file not saved

    :return: True if closed, False if closing was aborted
    """
    global active_file, saved, lock_mode, readonly
    if not saved:
        rep = messagebox.askyesnocancel("Closing file", "The opened file is not saved\nDo you want to save it ?")
        if rep:
            save()
            lock_mode = False
            readonly = False
            mode_update()
            active_file = ""
            text_box.delete("1.0", "end")
            reset_textbox_modified()
            return True
        elif rep is None:
            return False
        else:
            lock_mode = False
            readonly = False
            mode_update()
            active_file = ""
            text_box.delete("1.0", "end")
            reset_textbox_modified()
            return True
    else:
        lock_mode = False
        readonly = False
        mode_update()
        saved = True
        fen.title("Fastattack's text file editor - No file loaded")
        active_file = ""
        text_box.delete("1.0", "end")
        reset_textbox_modified()
        return True


# binding functions
def bind_save(event):  # bound to control + s
    save()


def bind_load(event):  # bound to control + l
    load()


def bind_new(event):  # bound to control + n
    create()


def undo(event=None):  # bound to control + z
    try:
        text_box.edit_undo()
    except tk.TclError:
        pass
    else:
        text_box.see("insert")


def redo(event=None):  # bound to control + shift + z
    try:
        text_box.edit_redo()
    except tk.TclError:
        pass
    else:
        text_box.see("insert")


# textbox saved functions
def textbox_modified(event):
    """Modify saved variable to False when text is modified or to True when reseted
    """
    global saved
    if text_box.edit_modified():
        saved = False
    else:
        saved = True
    if active_file == "":
        fen.title("Fastattack's text file editor - No file loaded")
    else:
        if readonly:
            fen.title(f"Fastattack's text file editor - {active_file} - Readonly mode")
        elif saved:
            fen.title(f"Fastattack's text file editor - {active_file} - Saved")
        else:
            fen.title(f"Fastattack's text file editor - {active_file} - Not saved")


def reset_textbox_modified():
    """Resets the edit_modified var if needed
    """
    if text_box.edit_modified():
        text_box.edit_modified(False)


# other functions
def closing_window():
    """Handles closing window
    """
    if close():
        fen.destroy()


def copy():
    try:
        text = text_box.selection_get()
    except tk.TclError:
        pass
    else:
        fen.clipboard_clear()
        fen.clipboard_append(text)


def cut():
    try:
        text = text_box.selection_get()
    except tk.TclError:
        pass
    else:
        fen.clipboard_clear()
        fen.clipboard_append(text)
        indexes = text_box.tag_ranges(tk.SEL)
        # noinspection PyTypeChecker
        text_box.delete(indexes[0::2], indexes[1::2])


def paste():
    try:
        text = fen.clipboard_get()
    except tk.TclError:
        pass
    else:
        text_box.insert(text_box.index(tk.INSERT), text)


def font_enter():
    new_font = simpledialog.askstring("Modify character font", "Enter the new font\nAll the characters will be set as the new size\nThe list of fonts depends on what you installed", initialvalue=global_font.actual()["family"])
    if new_font is not None:
        if new_font in font.families(fen):
            global_font.config(family=new_font)
        else:
            messagebox.showwarning("Modify character font", f"Font family {new_font} not found")


def font_arial():
    global_font.config(family="Arial")


def font_calibri():
    global_font.config(family="Calibri")


def font_TimesNewRoman():
    global_font.config(family="Arial")


def font_pixelated():
    global_font.config(family="Terminal")


def size_enter():
    size = simpledialog.askinteger("Modify character size", "Enter the new character size\nAll the characters will be "
                                                            "set as the new size\nThe size should be between 1 and 250 (default size is 11)", minvalue=1, maxvalue=250, initialvalue=global_font.actual()["size"])
    if size is not None:
        global_font.config(size=size)


def size_5():
    global_font.config(size=5)


def size_11():
    global_font.config(size=11)


def size_25():
    global_font.config(size=25)


def size_50():
    global_font.config(size=50)


def search_refresh(info=False) -> tuple:
    """Places the cursor at the occurrence (searched_index) of the search item (searched_item) and highlights all the occurrences

    :param info: False by default, if True: the function returns a tuple with additional info
    :return: if info is True: returns a tuple containing: searched item, number of all occurrences, actual occurrence
    """
    global searched_index
    if searched_item != "":
        data = text_box.get("1.0", "end")
        if searched_item in data:
            occurences = [m.start() for m in re.finditer(searched_item, data)]
            for occurence in occurences:
                text_box.tag_add(str(occurence), f"1.0+{occurence}c", f"1.0+{occurence+len(searched_item)}c")
                text_box.tag_configure(str(occurence), background="yellow", foreground="black")
            if searched_index > len(occurences)-1:
                searched_index = 0
            elif searched_index < 0:
                searched_index = len(occurences)-1
            text_box.mark_set("insert", f"1.0+{occurences[searched_index]}c")
            text_box.see("insert")
            if info:
                return searched_item, len(occurences), searched_index+1
        else:
            if info:
                return searched_item, 0, 0
            else:
                messagebox.showinfo("Searching", f"{searched_item} not found in the text")
    else:
        if info:
            return "",
        else:
            for tag in text_box.tag_names():
                text_box.tag_delete(tag)


def search_item(event=None):
    global searched_item, searched_index
    to_search = simpledialog.askstring("Search", "Enter the item to search in the file")
    if to_search is not None:
        if searched_item != "":
            search_stop()
        searched_item = to_search
        searched_index = 0
        search_refresh()


def search_stop(event=None):
    global searched_item
    searched_item = ""
    search_refresh()


def search_previous(event=None):
    global searched_index
    searched_index -= 1
    search_refresh()


def search_next(event=None):
    global searched_index
    searched_index += 1
    search_refresh()


def search_info(event=None):
    info = search_refresh(info=True)
    if info[0] == "":
        messagebox.showinfo("Searching", f"Not searching for any item in the text")
    elif info[1] == 0 and info[2] == 0:
        messagebox.showinfo("Searching", f"Searching for item {info[0]}\nNot found in the text")
    else:
        messagebox.showinfo("Searching", f"Searching for item {info[0]}\n{info[2]} out of {info[1]} total occurrences")


def help_tutorial():
    global lock_mode, readonly
    load("tutorial.txt")
    readonly = True
    lock_mode = True
    mode_update()


def help_github():
    webbrowser.open("https://github.com/fastattackv")


def mode_update():
    """Called to update the window's title or textbox state if edition mode is modified
    """
    if readonly:
        if active_file != "":
            save()
            fen.title(f"Fastattack's text file editor - {active_file} - Readonly mode")
            text_box.configure(state="disabled")
        else:
            messagebox.showwarning("Switching edition mode", "Can't switch to readonly mode if no file are loaded")
    else:
        fen.title(f"Fastattack's text file editor - {active_file} - Saved")
        text_box.configure(state="normal")


def switchmode(event=None):
    """Switches to readonly or modify mode if lock_mode if False
    """
    global readonly
    if lock_mode:
        messagebox.showinfo("Switching edition mode", "Can't switch editing mode for this file")
    else:
        if active_file != "":
            if readonly:
                readonly = False
            else:
                readonly = True
            mode_update()
        else:
            messagebox.showwarning("Switching edition mode", "Can't switch to readonly mode if no file are loaded")


# variables
saved = True
active_file = ""
searched_item = ""
searched_index = 0
readonly = False
lock_mode = False

# window definition
fen = tk.Tk()
fen.title("Fastattack's text file editor - No file loaded")
fen.geometry("1280x720")
fen.protocol("WM_DELETE_WINDOW", closing_window)
fen.resizable(width=True, height=True)
fen.grid_columnconfigure(0, weight=1)
fen.grid_columnconfigure(1, weight=0)
fen.grid_rowconfigure(0, weight=0)
fen.grid_rowconfigure(1, weight=0)
fen.grid_rowconfigure(2, weight=0)
fen.grid_rowconfigure(3, weight=0)
fen.grid_rowconfigure(4, weight=0)
fen.grid_rowconfigure(5, weight=0)
fen.grid_rowconfigure(6, weight=0)
fen.grid_rowconfigure(7, weight=1)
fen.grid_rowconfigure(8, weight=0)

# menubar definition
menubar = tk.Menu(fen)
fen.config(menu=menubar)
menu_file = tk.Menu(menubar)
menu_file.add_command(label="New", command=create, accelerator="CTRL+N")
menu_file.add_command(label="Load", command=load, accelerator="CTRL+L")
menu_file.add_command(label="Save", command=save, accelerator="CTRL+S")
menu_file.add_separator()
menu_file.add_command(label="Switch edition mode", command=switchmode, accelerator="CTRL+E")
menu_file.add_separator()
menu_file.add_command(label="Close", command=close)
menubar.add_cascade(label="File", menu=menu_file)
menu_edit = tk.Menu(menubar)
menu_edit.add_command(label="Undo", command=undo, accelerator="CTRL+Z")
menu_edit.add_command(label="Redo", command=redo, accelerator="CTRL+SHIFT+Z")
menu_edit.add_separator()
menu_edit.add_command(label="Copy", command=copy, accelerator="CTRL+C")
menu_edit.add_command(label="Cut", command=cut, accelerator="CTRL+X")
menu_edit.add_command(label="Paste", command=paste, accelerator="CTRL+V")
menu_edit.add_separator()
menu_font = tk.Menu(menu_edit)
menu_font.add_command(label="Arial", command=font_arial)
menu_font.add_command(label="Calibri", command=font_calibri)
menu_font.add_command(label="Times New Roman", command=font_TimesNewRoman)
menu_font.add_command(label="Pixelated", command=font_pixelated)
menu_font.add_command(label="Enter a font...", command=font_enter)
menu_edit.add_cascade(label="Font", menu=menu_font)
menu_size = tk.Menu(menu_edit)
menu_size.add_command(label="5", command=size_5)
menu_size.add_command(label="11", command=size_11)
menu_size.add_command(label="25", command=size_25)
menu_size.add_command(label="50", command=size_50)
menu_size.add_command(label="Enter size...", command=size_enter)
menu_edit.add_cascade(label="Size", menu=menu_size)
menubar.add_cascade(label="Edit", menu=menu_edit)
menubar.add_separator()
menu_search = tk.Menu(menubar)
menu_search.add_command(label="Modify search", command=search_item, accelerator="CTRL+F")
menu_search.add_command(label="Stop searching", command=search_stop, accelerator="CTRL+SHIFT+F")
menu_search.add_command(label="Previous occurrence", command=search_previous, accelerator="CTRL+P")
menu_search.add_command(label="Next occurrence", command=search_next, accelerator="CTRL+M")
menu_search.add_command(label="Search info", command=search_info, accelerator="CTRL+ALT+F")
menubar.add_cascade(label="Search", menu=menu_search)
menubar.add_separator()
menu_help = tk.Menu(menubar)
menu_help.add_command(label="Open tutorial", command=help_tutorial)
menu_help.add_command(label="Open github page", command=help_github)
menubar.add_cascade(label="Help", menu=menu_help)

# widgets definition
global_font = font.Font(family="Calibri", size=11)
yscrollbar = tk.Scrollbar(fen, orient="vertical")
yscrollbar.grid(row=0, column=1, rowspan=8, sticky="nswe")
xscrollbar = tk.Scrollbar(fen, orient="horizontal")
xscrollbar.grid(row=8, column=0, columnspan=2, sticky="nswe")
text_box = tk.Text(fen, wrap="none", yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set, undo=True, font=global_font)
text_box.grid(row=0, column=0, rowspan=8, sticky="nswe")
yscrollbar.config(command=text_box.yview)
xscrollbar.config(command=text_box.xview)
fen.bind_all("<Control-s>", bind_save)
fen.bind_all("<Control-l>", bind_load)
fen.bind_all("<Control-n>", bind_new)
fen.bind_all("<Control-z>", undo)
fen.bind_all("<Control-Z>", redo)
fen.bind_all("<Control-f>", search_item)
fen.bind_all("<Control-F>", search_stop)
fen.bind_all("<Control-p>", search_previous)
fen.bind_all("<Control-m>", search_next)
fen.bind_all("<Control-Alt-f>", search_info)
fen.bind_all("<Control-e>", switchmode)
text_box.bind("<<Modified>>", textbox_modified)

# if file opened by "open with" : loads it
try:
    active_file = argv[1]
except IndexError:
    pass
else:
    load(active_file)

fen.mainloop()
