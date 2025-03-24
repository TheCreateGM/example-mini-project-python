import tkinter as tk
from tkinter import messagebox, ttk, font
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Add a task
def add_task():
    task = entry.get()
    if task:
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (task) VALUES (?)', (task,))
        conn.commit()
        conn.close()
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
        status_label.config(text="Task added successfully!")
    else:
        messagebox.showwarning("Input Error", "Please enter a task.")

# Update a task
def update_task():
    try:
        index = listbox.curselection()[0]
        task = listbox.get(index)
        # Auto-fill the entry with the selected task
        entry.delete(0, tk.END)
        entry.insert(0, task)

        # Create update confirm button
        confirm_update_button.pack(side=tk.RIGHT, pady=5, padx=5)
        status_label.config(text="Edit the task and click 'Confirm Update'")

    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to update.")

# Confirm update after editing
def confirm_update():
    try:
        index = listbox.curselection()[0]
        old_task = listbox.get(index)
        new_task = entry.get()
        if new_task:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET task = ? WHERE task = ?', (new_task, old_task))
            conn.commit()
            conn.close()
            listbox.delete(index)
            listbox.insert(index, new_task)
            entry.delete(0, tk.END)
            confirm_update_button.pack_forget()
            status_label.config(text="Task updated successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter a new task.")
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to update.")

# Delete a task
def delete_task():
    try:
        index = listbox.curselection()[0]
        task = listbox.get(index)

        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete: \n\n'{task}'?")

        if confirm:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE task = ?', (task,))
            conn.commit()
            conn.close()
            listbox.delete(index)
            status_label.config(text="Task deleted successfully!")

    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete.")

# Mark task as completed
def mark_completed():
    try:
        index = listbox.curselection()[0]
        task = listbox.get(index)
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        # Check if task is already completed
        cursor.execute('SELECT completed FROM tasks WHERE task = ?', (task,))
        completed = cursor.fetchone()[0]

        if completed:
            cursor.execute('UPDATE tasks SET completed = 0 WHERE task = ?', (task,))
            listbox.itemconfig(index, {'bg': 'white'})
            status_label.config(text="Task marked as incomplete!")
        else:
            cursor.execute('UPDATE tasks SET completed = 1 WHERE task = ?', (task,))
            listbox.itemconfig(index, {'bg': '#90EE90'})
            status_label.config(text="Task marked as completed!")

        conn.commit()
        conn.close()

    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to mark as completed.")

# Load tasks from database
def load_tasks():
    listbox.delete(0, tk.END)  # Clear existing items
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT task, completed FROM tasks')
    tasks = cursor.fetchall()
    conn.close()
    for task, completed in tasks:
        listbox.insert(tk.END, task)
        if completed:
            listbox.itemconfig(tk.END, {'bg': '#90EE90'})
    status_label.config(text=f"Loaded {len(tasks)} tasks")

# Search tasks
def search_tasks(*args):
    search_term = search_var.get().lower()
    listbox.delete(0, tk.END)

    if not search_term:
        load_tasks()
        return

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT task, completed FROM tasks WHERE LOWER(task) LIKE ?', (f'%{search_term}%',))
    tasks = cursor.fetchall()
    conn.close()

    for task, completed in tasks:
        listbox.insert(tk.END, task)
        if completed:
            listbox.itemconfig(tk.END, {'bg': '#90EE90'})

    status_label.config(text=f"Found {len(tasks)} matching tasks")

# Select task on click
def on_task_select(event):
    try:
        index = listbox.curselection()[0]
        task = listbox.get(index)
        entry.delete(0, tk.END)
        entry.insert(0, task)
        status_label.config(text="Task selected. Edit and click 'Update Task' or press other buttons.")
    except IndexError:
        pass

# Clear entry field
def clear_entry():
    entry.delete(0, tk.END)
    confirm_update_button.pack_forget()
    status_label.config(text="Ready")

# GUI setup
root = tk.Tk()
root.title("Easy To-Do List Manager")
root.geometry("600x700")
root.configure(bg='#f5f5f5')
root.minsize(500, 600)

# Create custom fonts
title_font = font.Font(family="Helvetica", size=16, weight="bold")
button_font = font.Font(family="Helvetica", size=10)
list_font = font.Font(family="Helvetica", size=12)

# Header
header_frame = tk.Frame(root, bg="#4a86e8", padx=10, pady=10)
header_frame.pack(fill=tk.X)

header_label = tk.Label(header_frame, text="✓ My To-Do List",
                         font=title_font, bg="#4a86e8", fg="white")
header_label.pack(pady=10)

instruction_label = tk.Label(header_frame,
                            text="Add new tasks, select tasks to update or delete, and mark tasks as completed.",
                            bg="#4a86e8", fg="white", wraplength=500)
instruction_label.pack(pady=(0,10))

# Main content frame
content_frame = tk.Frame(root, bg='#f5f5f5', padx=20, pady=20)
content_frame.pack(fill=tk.BOTH, expand=True)

# Search bar
search_frame = tk.Frame(content_frame, bg='#f5f5f5')
search_frame.pack(fill=tk.X, pady=(0, 10))

search_label = tk.Label(search_frame, text="Search:", bg='#f5f5f5')
search_label.pack(side=tk.LEFT, padx=(0, 5))

search_var = tk.StringVar()
search_var.trace("w", search_tasks)
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Task entry section
entry_frame = tk.Frame(content_frame, bg='#f5f5f5')
entry_frame.pack(fill=tk.X, pady=10)

entry_label = tk.Label(entry_frame, text="Task:", bg='#f5f5f5')
entry_label.pack(side=tk.LEFT, padx=(0, 5))

entry = ttk.Entry(entry_frame, width=50, font=list_font)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

clear_button = ttk.Button(entry_frame, text="✕", width=3, command=clear_entry)
clear_button.pack(side=tk.RIGHT)

# Style for buttons
style = ttk.Style()
style.configure('TButton', font=button_font)
style.configure('Primary.TButton', foreground='white', background='#4a86e8')
style.map('Primary.TButton', background=[('active', '#3a76d8')], foreground=[('active', 'white')])

# Button frame
button_frame = ttk.Frame(content_frame)
button_frame.pack(fill=tk.X, pady=10)

# Buttons
add_button = ttk.Button(
    button_frame,
    text="Add Task",
    command=add_task,
    style='Primary.TButton',
    padding=10
)
add_button.pack(side=tk.LEFT, pady=5, padx=5, expand=True, fill=tk.X)

update_button = ttk.Button(
    button_frame,
    text="Update Task",
    command=update_task,
    padding=10
)
update_button.pack(side=tk.LEFT, pady=5, padx=5, expand=True, fill=tk.X)

delete_button = ttk.Button(
    button_frame,
    text="Delete Task",
    command=delete_task,
    padding=10
)
delete_button.pack(side=tk.LEFT, pady=5, padx=5, expand=True, fill=tk.X)

mark_button = ttk.Button(
    button_frame,
    text="Toggle Completed",
    command=mark_completed,
    padding=10
)
mark_button.pack(side=tk.LEFT, pady=5, padx=5, expand=True, fill=tk.X)

# Confirm update button (hidden initially)
confirm_update_button = ttk.Button(
    button_frame,
    text="Confirm Update",
    command=confirm_update,
    style='Primary.TButton',
    padding=10
)

# Task list label
list_label = tk.Label(content_frame, text="Your Tasks:", bg='#f5f5f5', font=button_font, anchor='w')
list_label.pack(fill=tk.X, pady=(10, 5))

# Listbox with scrollbar
list_frame = tk.Frame(content_frame, bg='#f5f5f5')
list_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    list_frame,
    width=50,
    height=15,
    borderwidth=1,
    highlightthickness=1,
    selectmode=tk.SINGLE,
    font=list_font,
    bg='white',
    selectbackground='#4a86e8',
    selectforeground='white',
    highlightcolor='#4a86e8',
    activestyle='none',
    relief=tk.SOLID
)
listbox.pack(fill=tk.BOTH, expand=True)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Bind selection to event
listbox.bind('<<ListboxSelect>>', on_task_select)

# Status bar
status_frame = tk.Frame(root, bg="#e0e0e0", padx=10, pady=5)
status_frame.pack(fill=tk.X, side=tk.BOTTOM)

status_label = tk.Label(status_frame, text="Ready", bg="#e0e0e0", anchor='w')
status_label.pack(side=tk.LEFT)

refresh_button = ttk.Button(
    status_frame,
    text="↻ Refresh",
    command=load_tasks,
    width=10
)
refresh_button.pack(side=tk.RIGHT, padx=5)

# Keyboard shortcuts
root.bind('<Return>', lambda event: add_task())
root.bind('<Escape>', lambda event: clear_entry())

# Load tasks from database
setup_database()
load_tasks()

root.mainloop()
