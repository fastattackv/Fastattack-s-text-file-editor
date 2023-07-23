import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import requests
import zipfile
import win32com.client
import winreg
import sys
import ctypes

"""Tkinter functions order:
- validate_start
- show_start
- show_folder_select -> validate_folder_select
- show_shortcut_create
- show_downloading
"""

# tkinter variables
win = tk.Tk()
win.title("Fastattack's text editor installer")
win.geometry("350x350")
win.resizable(height=False, width=False)

win.grid_rowconfigure(0, weight=0)
win.grid_rowconfigure(1, weight=1)
win.grid_rowconfigure(2, weight=0)
win.grid_rowconfigure(0, weight=0)
win.grid_rowconfigure(1, weight=1)
win.grid_rowconfigure(2, weight=0)


button_validate = tk.Button(win)
button_back = tk.Button(win)
button1 = tk.Button(win)
label1 = tk.Label()
label2 = tk.Label()
checkbutton1 = tk.Checkbutton(win)
checkbutton2 = tk.Checkbutton(win)
checkbutton3 = tk.Checkbutton(win)
progress_bar = ttk.Progressbar(win, orient="horizontal", length=250, mode="determinate")

# variables
app_version = 0.0
global_path = ""
global_shortcut_desktop = tk.BooleanVar()
global_shortcut_start = tk.BooleanVar()
global_add_open_with = tk.BooleanVar()


# tkinter functions
def forget_all():
    button_validate.grid_forget()
    button_back.grid_forget()
    button1.grid_forget()
    label1.grid_forget()
    label2.grid_forget()
    checkbutton1.grid_forget()
    checkbutton2.grid_forget()
    checkbutton3.grid_forget()


def validate_start():
    global app_version
    try:
        data = requests.get("https://raw.githubusercontent.com/fastattackv/Fastattack-s-text-file-editor/main/Downloads/gitinfo.txt")
    except requests.exceptions.ConnectionError:
        rep = messagebox.askretrycancel("Checking version", "Connection error:\nCan't install the text editor")
        if rep:
            validate_start()
        else:
            win.destroy()
    except:
        rep = messagebox.askretrycancel("Checking version", "Error unknown:\nCan't install the text editor")
        if rep:
            validate_start()
        else:
            win.destroy()
    else:
        data = str(data.content).removeprefix("b'")
        data = data.removesuffix("'")
        data = data.split("\\n")
        app_version = float(data[0].removeprefix("Version="))
        installer_version = float(data[1].removeprefix("InstallerVersion="))
        if installer_version != 1.0:
            messagebox.showerror("Checking version", f"Installer version outdated\nLatest version: {installer_version}\nInstaller version: 1.0")
        else:
            show_start()


def show_start():
    forget_all()
    label1.configure(text="Welcome to\nFastattack's text editor installer\n                                                                                     ")
    label1.grid(row=0, column=1)
    label2.configure(text=f"Latest version: {app_version}")
    label2.grid(row=1, column=1)
    button_validate.configure(text="Continue", command=show_folder_select, state="normal")
    button_validate.grid(row=2, column=2, sticky="se")
    button_back.configure(text="Exit", command=win.destroy)
    button_back.grid(row=2, column=0, sticky="sw")


def show_folder_select():
    forget_all()
    if os.path.exists(global_path):
        if len(global_path) > 72:
            path = f"{global_path[0:36]}\n{global_path[36:72]}\n{global_path[72:]}"
        elif len(global_path) > 36:
            path = f"{global_path[0:36]}\n{global_path[36:]}"
        else:
            path = global_path
        label1.configure(text=f"Please select a path to install the app\n                                                                                   \n\nPath: {path}")
        button_validate.configure(text="Continue", command=show_shortcut_create, state="normal")
    else:
        label1.configure(text="Please select a path to install the app\n                                                                                   \n\nPath: No path selected")
        button_validate.configure(text="Continue", command=show_shortcut_create, state="disabled")
    label1.grid(row=0, column=1)
    button_validate.grid(row=2, column=2, sticky="se")
    button1.configure(text="Change path", command=validate_folder_select)
    button1.grid(row=1, column=1)
    button_back.configure(text="Back", command=show_start)
    button_back.grid(row=2, column=0, sticky="sw")


def validate_folder_select():
    global global_path
    path = filedialog.askdirectory(initialdir=rf"C:\Users\{os.getlogin()}\Desktop")
    if path != "":
        global_path = path
        show_folder_select()


def show_shortcut_create():
    forget_all()
    label1.configure(text="Finalization\n                                                                                   \n\n\n")
    label1.grid(row=0, column=1)
    checkbutton1.configure(text="Create shortcut on desktop", variable=global_shortcut_desktop, onvalue=True, offvalue=False)
    checkbutton1.grid(row=1, column=1, sticky="n", pady=5)
    checkbutton2.configure(text="Create shortcut in start menu search page", variable=global_shortcut_start, onvalue=True, offvalue=False)
    checkbutton2.grid(row=1, column=1)
    checkbutton3.configure(text="Add to the context menu", variable=global_add_open_with, onvalue=True, offvalue=False)
    checkbutton3.grid(row=1, column=1, sticky="s", pady=5)
    button_validate.configure(text="Continue", command=show_downloading, state="normal")
    button_validate.grid(row=2, column=2, sticky="se")
    button_back.configure(text="Back", command=show_folder_select)
    button_back.grid(row=2, column=0, sticky="sw")


def show_downloading():
    forget_all()
    label1.configure(text="Downloading\n                                                                                   \n\n\n")
    label1.grid(row=0, column=1)
    progress_bar.grid(row=1, column=1, padx=50, sticky="n")
    progress_bar["value"] = 0
    try:
        data = requests.get("https://github.com/fastattackv/Fastattack-s-text-file-editor/raw/main/Downloads/Fastattack's%20text%20file%20editor.zip")
    except requests.exceptions.ConnectionError:
        rep = messagebox.askretrycancel("Downloading", "Downloading failed:\nConnection error")
        if rep:
            show_downloading()
        else:
            show_shortcut_create()
    except:
        rep = messagebox.askretrycancel("Downloading", "Downloading failed:\nError unknown")
        if rep:
            show_downloading()
        else:
            show_shortcut_create()
    else:
        progress_bar["value"] = 25
        try:
            with open(f"{global_path}/Fastattack's text file editor.zip", "wb") as a:
                a.write(data.content)
        except PermissionError:
            rep = messagebox.askretrycancel("Downloading", "Writing failed:\nPermission error\nTry to run the program as administrator")
            if rep:
                show_downloading()
            else:
                show_shortcut_create()
        except:
            rep = messagebox.askretrycancel("Downloading", "Writing failed:\nError unknown")
            if rep:
                show_downloading()
            else:
                show_shortcut_create()
        else:
            progress_bar["value"] = 50
            try:
                with zipfile.ZipFile(f"{global_path}/Fastattack's text file editor.zip", "r") as zip_ref:
                    zip_ref.extractall(global_path)
            except zipfile.BadZipFile:
                rep = messagebox.askretrycancel("Downloading", "Extracting failed:\nFile corrupted")
                if rep:
                    show_downloading()
                else:
                    show_shortcut_create()
            except:
                rep = messagebox.askretrycancel("Downloading", "Extracting failed:\nError unknown")
                if rep:
                    show_downloading()
                else:
                    show_shortcut_create()
            else:
                progress_bar["value"] = 75
                os.remove(f"{global_path}/Fastattack's text file editor.zip")
                if global_shortcut_desktop.get():
                    wdir = global_path + rf"\Fastattack's text file editor (v{app_version})"
                    target = global_path + rf"\Fastattack's text file editor (v{app_version})\Fastattack's text editor.exe"
                    path = rf"C:\Users\{os.getlogin()}\Desktop\Fastattack's text editor.lnk"
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(path)
                    shortcut.Targetpath = target
                    shortcut.WorkingDirectory = wdir
                    shortcut.save()
                if global_shortcut_start.get():
                    wdir = global_path + rf"\Fastattack's text file editor (v{app_version})"
                    target = global_path + rf"\Fastattack's text file editor (v{app_version})\Fastattack's text editor.exe"
                    path = rf"C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Fastattack's text editor.lnk"
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(path)
                    shortcut.Targetpath = target
                    shortcut.WorkingDirectory = wdir
                    shortcut.save()
                if global_add_open_with.get():
                    key_path = r"*\\shell\\Fastattack's text editor"
                    command_key_path = r"*\\shell\\Fastattack's text editor\\command"
                    path1 = global_path.replace("/", "\\")
                    path = '"' + rf"{path1}\Fastattack's text file editor (v{app_version})\Fastattack's text editor.exe" + '" "%1"'
                    try:
                        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
                        command_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_key_path)
                        winreg.SetValue(key, "", winreg.REG_SZ, "Open with Fastattack's text editor")
                        winreg.SetValue(command_key, "", winreg.REG_SZ, path)
                    except:
                        messagebox.showerror("Adding to context menu", "Adding the app to context menu failed: Unknown error")
                progress_bar["value"] = 100
                messagebox.showinfo("Downloading", f"Installation complete\nFastattack's text file editor is installed at\n{global_path}")
                win.destroy()


if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
else:
    validate_start()
    win.mainloop()
