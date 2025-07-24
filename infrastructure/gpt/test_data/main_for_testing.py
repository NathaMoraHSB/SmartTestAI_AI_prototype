# main.py

import tkinter as tk
from infrastructure.gpt.test_data.gui import AssistantApp

if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantApp(root)
    root.mainloop()
