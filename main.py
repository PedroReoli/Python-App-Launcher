import tkinter as tk
from py_app_launcher import PyAppLauncher

if __name__ == "__main__":
    root = tk.Tk()
    app = PyAppLauncher(root)
    root.mainloop()