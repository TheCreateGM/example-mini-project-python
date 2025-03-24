import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Set up a modern theme if available
try:
    from ttkthemes import ThemedTk
    # pip install ttkthemes
    use_themed_tk = True
except ImportError:
    use_themed_tk = False
    ThemedTk = None

# Color scheme
COLORS = {
    "primary": "#3498db",
    "secondary": "#2980b9",
    "background": "#f5f5f5",
    "text": "#333333",
    "success": "#2ecc71",
    "danger": "#e74c3c",
    "warning": "#f39c12"
}

# Create a database or connect to one
conn = sqlite3.connect('students.db')

# Create a cursor
c = conn.cursor()

# Create table
c.execute("""CREATE TABLE IF NOT EXISTS students (
            name text,
            age integer,
            grade text,
            email text
            )""")

# Commit our command
conn.commit()

# Close our connection
conn.close()

# Create a function to add a record to the database
def add_record():
    # Validate inputs
    if not name.get() or not age.get() or not grade.get() or not email.get():
        messagebox.showerror("Error", "Please fill in all fields")
        return

    try:
        # Validate age is a number
        int(age.get())
    except ValueError:
        messagebox.showerror("Error", "Age must be a number")
        return

    # Create a database or connect to one
    conn = sqlite3.connect('students.db')

    # Create a cursor
    c = conn.cursor()

    # Insert Into Table
    c.execute("INSERT INTO students VALUES (:name, :age, :grade, :email)",
              {
                  'name': name.get(),
                  'age': age.get(),
                  'grade': grade.get(),
                  'email': email.get()
              })

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

    # Clear The Text Boxes
    name.delete(0, tk.END)
    age.delete(0, tk.END)
    grade.delete(0, tk.END)
    email.delete(0, tk.END)

    # Show success message
    status_label.config(text="Record added successfully!", foreground=COLORS["success"])

    # Populate the list
    query_database()

# Create a function to query the database
def query_database():
    # Clear the treeview
    for record in student_tree.get_children():
        student_tree.delete(record)

    # Create a database or connect to one
    conn = sqlite3.connect('students.db')

    # Create a cursor
    c = conn.cursor()

    # Query the database
    c.execute("SELECT *, oid FROM students")
    records = c.fetchall()

    # Add data to the treeview
    for i, record in enumerate(records):
        # Alternate row colors
        if i % 2 == 0:
            student_tree.insert(parent='', index='end', iid=i, text='',
                               values=(record[4], record[0], record[1], record[2], record[3]),
                               tags=('evenrow',))
        else:
            student_tree.insert(parent='', index='end', iid=i, text='',
                               values=(record[4], record[0], record[1], record[2], record[3]),
                               tags=('oddrow',))

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

# Create a function to delete a record from the database
def delete_record():
    # Check if a record is selected
    if not student_tree.selection():
        messagebox.showerror("Error", "Please select a record to delete")
        return

    # Confirm delete
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
        return

    # Get the ID from the selected item
    selected_item = student_tree.selection()[0]
    record_id = student_tree.item(selected_item, 'values')[0]

    # Create a database or connect to one
    conn = sqlite3.connect('students.db')

    # Create a cursor
    c = conn.cursor()

    # Delete a record using a parameterized query
    c.execute("DELETE FROM students WHERE oid = ?", (record_id,))

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

    # Show success message
    status_label.config(text="Record deleted successfully!", foreground=COLORS["success"])

    # Refresh the treeview
    query_database()

# Create a function to update a record in the database
def update_record():
    # Validate inputs
    if not name_editor.get() or not age_editor.get() or not grade_editor.get() or not email_editor.get():
        messagebox.showerror("Error", "Please fill in all fields")
        return

    try:
        # Validate age is a number
        int(age_editor.get())
    except ValueError:
        messagebox.showerror("Error", "Age must be a number")
        return

    # Create a database or connect to one
    conn = sqlite3.connect('students.db')

    # Create a cursor
    c = conn.cursor()

    # Get record ID from the selected item
    record_id = editor.title().split()[-1]

    c.execute("""UPDATE students SET
        name = :name,
        age = :age,
        grade = :grade,
        email = :email
        WHERE oid = :oid""",
        {
            'name': name_editor.get(),
            'age': age_editor.get(),
            'grade': grade_editor.get(),
            'email': email_editor.get(),
            'oid': record_id
        })

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

    # Close the editor window
    editor.destroy()

    # Show success message
    status_label.config(text="Record updated successfully!", foreground=COLORS["success"])

    # Populate the list
    query_database()

# Create a function to edit a record
def edit_record():
    # Check if a record is selected
    if not student_tree.selection():
        messagebox.showerror("Error", "Please select a record to edit")
        return

    # Get the ID from the selected item
    selected_item = student_tree.selection()[0]
    record_id = student_tree.item(selected_item, 'values')[0]

    global editor

    if use_themed_tk and ThemedTk:
        editor = ThemedTk(theme="arc")
    else:
        editor = tk.Toplevel()

    editor.title('Edit Record - ID: ' + str(record_id))
    editor.geometry("400x350")
    editor.configure(bg=COLORS["background"])
    editor.resizable(False, False)

    # Add some padding
    frame = ttk.Frame(editor, padding="20")
    frame.pack(fill="both", expand=True)

    # Create a database or connect to one
    conn = sqlite3.connect('students.db')

    # Create a cursor
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE oid = ?", (record_id,))
    records = c.fetchall()

    # Create Global Variables for text box names
    global name_editor
    global age_editor
    global grade_editor
    global email_editor

    # Create form title
    title_label = ttk.Label(frame, text="Edit Student Record", font=("Helvetica", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

    # Create Text Box Labels with modern styling
    name_label = ttk.Label(frame, text="Name:")
    name_label.grid(row=1, column=0, pady=10, sticky="w")

    age_label = ttk.Label(frame, text="Age:")
    age_label.grid(row=2, column=0, pady=10, sticky="w")

    grade_label = ttk.Label(frame, text="Grade:")
    grade_label.grid(row=3, column=0, pady=10, sticky="w")

    email_label = ttk.Label(frame, text="Email:")
    email_label.grid(row=4, column=0, pady=10, sticky="w")

    # Create Text Boxes with modern styling
    name_editor = ttk.Entry(frame, width=30, font=("Helvetica", 10))
    name_editor.grid(row=1, column=1, pady=10, padx=10)

    age_editor = ttk.Entry(frame, width=30, font=("Helvetica", 10))
    age_editor.grid(row=2, column=1, pady=10, padx=10)

    grade_editor = ttk.Entry(frame, width=30, font=("Helvetica", 10))
    grade_editor.grid(row=3, column=1, pady=10, padx=10)

    email_editor = ttk.Entry(frame, width=30, font=("Helvetica", 10))
    email_editor.grid(row=4, column=1, pady=10, padx=10)

    # Create button frame
    button_frame = ttk.Frame(frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=20)

    # Create Save and Cancel buttons
    save_btn = ttk.Button(button_frame, text="Save Changes", command=update_record, style="Accent.TButton")
    save_btn.grid(row=0, column=0, padx=10)

    cancel_btn = ttk.Button(button_frame, text="Cancel", command=editor.destroy)
    cancel_btn.grid(row=0, column=1, padx=10)

    # Insert the current data
    for record in records:
        name_editor.insert(0, record[0])
        age_editor.insert(0, record[1])
        grade_editor.insert(0, record[2])
        email_editor.insert(0, record[3])

    # Close the database connection
    conn.close()

# Function to handle treeview selection
def on_tree_select(event):
    selected_item = student_tree.selection()
    if selected_item:
        # Enable delete and edit buttons when an item is selected
        delete_btn.config(state="normal")
        edit_btn.config(state="normal")
    else:
        # Disable buttons if no selection
        delete_btn.config(state="disabled")
        edit_btn.config(state="disabled")

# Create the main window with themed Tk if available
if use_themed_tk and ThemedTk:
    root = ThemedTk(theme="arc")
else:
    root = tk.Tk()

root.title('Student Record Management')
root.geometry("800x650")
root.configure(bg=COLORS["background"])
root.resizable(True, True)

# Configure styles for ttk widgets
style = ttk.Style()
style.configure("TFrame", background=COLORS["background"])
style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"], font=("Helvetica", 10))
style.configure("TButton", font=("Helvetica", 10))
style.configure("Accent.TButton", background=COLORS["primary"])
style.configure("Danger.TButton", background=COLORS["danger"])

# Create a notebook for tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=15)

# Create add record tab
add_frame = ttk.Frame(notebook, padding=20)
notebook.add(add_frame, text="Add Record")

# Create view records tab
view_frame = ttk.Frame(notebook, padding=20)
notebook.add(view_frame, text="View Records")

# ----- Add Record Tab -----
# Create a title label
title_label = ttk.Label(add_frame, text="Add New Student", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

# Create input fields with labels
name_label = ttk.Label(add_frame, text="Name:")
name_label.grid(row=1, column=0, pady=10, sticky="w")
name = ttk.Entry(add_frame, width=40, font=("Helvetica", 10))
name.grid(row=1, column=1, padx=5, pady=10)

age_label = ttk.Label(add_frame, text="Age:")
age_label.grid(row=2, column=0, pady=10, sticky="w")
age = ttk.Entry(add_frame, width=40, font=("Helvetica", 10))
age.grid(row=2, column=1, padx=5, pady=10)

grade_label = ttk.Label(add_frame, text="Grade:")
grade_label.grid(row=3, column=0, pady=10, sticky="w")
grade = ttk.Entry(add_frame, width=40, font=("Helvetica", 10))
grade.grid(row=3, column=1, padx=5, pady=10)

email_label = ttk.Label(add_frame, text="Email:")
email_label.grid(row=4, column=0, pady=10, sticky="w")
email = ttk.Entry(add_frame, width=40, font=("Helvetica", 10))
email.grid(row=4, column=1, padx=5, pady=10)

# Add button frame
button_frame = ttk.Frame(add_frame)
button_frame.grid(row=5, column=0, columnspan=2, pady=20)

# Add submit button
submit_btn = ttk.Button(button_frame, text="Add Record", command=add_record, style="Accent.TButton")
submit_btn.grid(row=0, column=0, padx=5, pady=10)

# Clear form button
clear_btn = ttk.Button(button_frame, text="Clear Form",
                        command=lambda: [name.delete(0, tk.END), age.delete(0, tk.END),
                                         grade.delete(0, tk.END), email.delete(0, tk.END)])
clear_btn.grid(row=0, column=1, padx=5, pady=10)

# ----- View Records Tab -----
# Create a frame for the treeview
tree_frame = ttk.Frame(view_frame)
tree_frame.pack(fill="both", expand=True)

# Create a scrollbar
tree_scroll = ttk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

# Create the treeview
student_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
student_tree.pack(fill="both", expand=True)

# Configure the scrollbar
tree_scroll.config(command=student_tree.yview)

# Define columns
student_tree['columns'] = ("ID", "Name", "Age", "Grade", "Email")

# Format columns
student_tree.column("#0", width=0, stretch=tk.NO)
student_tree.column("ID", anchor=tk.W, width=50)
student_tree.column("Name", anchor=tk.W, width=140)
student_tree.column("Age", anchor=tk.CENTER, width=50)
student_tree.column("Grade", anchor=tk.CENTER, width=80)
student_tree.column("Email", anchor=tk.W, width=200)

# Create headings
student_tree.heading("#0", text="", anchor=tk.W)
student_tree.heading("ID", text="ID", anchor=tk.W)
student_tree.heading("Name", text="Name", anchor=tk.W)
student_tree.heading("Age", text="Age", anchor=tk.CENTER)
student_tree.heading("Grade", text="Grade", anchor=tk.CENTER)
student_tree.heading("Email", text="Email", anchor=tk.W)

# Create striped row tags
student_tree.tag_configure('oddrow', background="#E8E8E8")
student_tree.tag_configure('evenrow', background="#FFFFFF")

# Bind the treeview selection event
student_tree.bind("<<TreeviewSelect>>", on_tree_select)

# Create a frame for buttons below the treeview
button_frame2 = ttk.Frame(view_frame)
button_frame2.pack(fill="x", pady=10)

# Create a refresh button
refresh_btn = ttk.Button(button_frame2, text="Refresh Data", command=query_database)
refresh_btn.pack(side=tk.LEFT, padx=5)

# Create an edit button
edit_btn = ttk.Button(button_frame2, text="Edit Selected", command=edit_record, state="disabled")
edit_btn.pack(side=tk.LEFT, padx=5)

# Create a delete button
delete_btn = ttk.Button(button_frame2, text="Delete Selected", command=delete_record,
                        style="Danger.TButton", state="disabled")
delete_btn.pack(side=tk.LEFT, padx=5)

# Create a status label
status_label = ttk.Label(root, text="", font=("Helvetica", 10))
status_label.pack(pady=10)

# Populate the treeview with data
query_database()

# Start the main loop
root.mainloop()
