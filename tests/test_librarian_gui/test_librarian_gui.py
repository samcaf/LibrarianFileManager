import tkinter as tk

from librarian.gui.librarian_gui import LibrarianGUI

from project_info import *

if __name__ == "__main__":
    root = tk.Tk()
    app = LibrarianGUI(root, LOADOUT)
    root.mainloop()
