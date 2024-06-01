import tkinter as tk
from tkinter import messagebox
import subprocess
import pyperclip

def get_machine_id():
    try:
        result = subprocess.check_output("wmic csproduct get uuid", shell=True)
        result = result.decode().split('\n')[1].strip()
        return result
    except Exception as e:
        return str(e)

def copy_to_clipboard():
    machine_id = machine_id_label.cget("text")
    pyperclip.copy(machine_id)
    messagebox.showinfo("Copied", "Machine ID copied to clipboard!")

# Create the main window
root = tk.Tk()
root.title("Machine ID Viewer")

# Fetch and display the machine ID
machine_id = get_machine_id()
machine_id_label = tk.Label(root, text=machine_id, padx=10, pady=10)
machine_id_label.pack()

# Create the copy button
copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=10)

# Run the application
root.mainloop()
