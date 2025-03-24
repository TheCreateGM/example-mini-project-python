import tkinter as tk
from tkinter import ttk
import sqlite3

# Create a database or connect to one
conn = sqlite3.connect('contacts.db')
c = conn.cursor()

# Create table
c.execute("""CREATE TABLE IF NOT EXISTS contacts (
            name text,
            phone text,
            email text
            )""")

# Commit changes
conn.commit()

# Close connection
conn.close()

# Function to add contact
def add_contact():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("INSERT INTO contacts VALUES (:name, :phone, :email)",
              {
                  'name': name_entry.get(),
                  'phone': phone_entry.get(),
                  'email': email_entry.get()
              })
    conn.commit()
    conn.close()
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    query_contacts()

# Function to edit contact
def edit_contact():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("""UPDATE contacts SET
                name = :name,
                phone = :phone,
                email = :email
                WHERE oid = :oid""",
              {
                  'name': name_entry.get(),
                  'phone': phone_entry.get(),
                  'email': email_entry.get(),
                  'oid': selected_contact[0]
              })
    conn.commit()
    conn.close()
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    query_contacts()

# Function to delete contact
def delete_contact():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE oid= " + str(selected_contact[0]))
    conn.commit()
    conn.close()
    query_contacts()

# Function to search contacts
def search_contacts():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM contacts WHERE name LIKE ?", ('%' + search_entry.get() + '%',))
    records = c.fetchall()
    conn.close()
    contacts_tree.delete(*contacts_tree.get_children())
    for record in records:
        contacts_tree.insert('', tk.END, values=record)

# Function to query contacts
def query_contacts():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM contacts")
    records = c.fetchall()
    conn.close()
    contacts_tree.delete(*contacts_tree.get_children())
    for record in records:
        contacts_tree.insert('', tk.END, values=record)

# Function to select contact
def select_contact(event):
    global selected_contact
    selected_contact = contacts_tree.item(contacts_tree.focus())['values']
    name_entry.delete(0, tk.END)
    name_entry.insert(0, selected_contact[0])
    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, selected_contact[1])
    email_entry.delete(0, tk.END)
    email_entry.insert(0, selected_contact[2])

# Create main window with a modern style
root = tk.Tk()
root.title('Contact Book')
root.geometry("800x700")
root.configure(bg='#f0f0f0')
style = ttk.Style()
style.theme_use("clam")

# Configure modern styles
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=('Helvetica', 10))
style.configure("TEntry", padding=5, relief="flat")
style.configure("TButton", padding=8, relief="flat", background="#4a90e2", foreground="white")
style.map("TButton", background=[("active", "#357abd"), ("pressed", "#2a5d8f")])
style.configure("Treeview", background="white", fieldbackground="white", font=('Helvetica', 9))
style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

# Create a frame for inputs and buttons
input_frame = ttk.Frame(root, padding="20")
input_frame.grid(row=0, column=0, sticky="NSEW", padx=20, pady=10)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=0)

# Create labels and entry widgets
name_label = ttk.Label(input_frame, text='Name:')
name_label.grid(row=0, column=0, padx=10, pady=8, sticky="W")
name_entry = ttk.Entry(input_frame, width=50)
name_entry.grid(row=0, column=1, padx=10, pady=8, sticky="EW")

phone_label = ttk.Label(input_frame, text='Phone:')
phone_label.grid(row=1, column=0, padx=10, pady=8, sticky="W")
phone_entry = ttk.Entry(input_frame, width=50)
phone_entry.grid(row=1, column=1, padx=10, pady=8, sticky="EW")

email_label = ttk.Label(input_frame, text='Email:')
email_label.grid(row=2, column=0, padx=10, pady=8, sticky="W")
email_entry = ttk.Entry(input_frame, width=50)
email_entry.grid(row=2, column=1, padx=10, pady=8, sticky="EW")

# Create a frame for action buttons
button_frame = ttk.Frame(input_frame)
button_frame.grid(row=3, column=0, columnspan=2, sticky="EW", pady=15)
button_frame.columnconfigure((0, 1, 2), weight=1)

add_button = ttk.Button(button_frame, text='Add Contact', command=add_contact)
add_button.grid(row=0, column=0, padx=5, sticky="EW")

edit_button = ttk.Button(button_frame, text='Edit Contact', command=edit_contact)
edit_button.grid(row=0, column=1, padx=5, sticky="EW")

delete_button = ttk.Button(button_frame, text='Delete Contact', command=delete_contact)
delete_button.grid(row=0, column=2, padx=5, sticky="EW")

# Create a frame for search functionality
search_frame = ttk.Frame(root, padding="20")
search_frame.grid(row=1, column=0, sticky="EW", padx=20)
search_frame.columnconfigure(1, weight=1)

search_label = ttk.Label(search_frame, text='Search:')
search_label.grid(row=0, column=0, padx=10, sticky="W")
search_entry = ttk.Entry(search_frame, width=50)
search_entry.grid(row=0, column=1, padx=10, sticky="EW")

search_button = ttk.Button(search_frame, text='Search', command=search_contacts)
search_button.grid(row=0, column=2, padx=10, sticky="EW")

# Create a frame for the treeview
tree_frame = ttk.Frame(root, padding="20")
tree_frame.grid(row=2, column=0, sticky="NSEW", padx=20, pady=10)
root.rowconfigure(2, weight=1)

contacts_tree = ttk.Treeview(tree_frame, columns=('Name', 'Phone', 'Email', 'ID'), show='headings', height=15)
contacts_tree.heading('Name', text='Name')
contacts_tree.heading('Phone', text='Phone')
contacts_tree.heading('Email', text='Email')
contacts_tree.heading('ID', text='ID')
contacts_tree.column('Name', width=200)
contacts_tree.column('Phone', width=150)
contacts_tree.column('Email', width=250)
contacts_tree.column('ID', width=50)
contacts_tree.grid(row=0, column=0, sticky="NSEW")

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=contacts_tree.yview)
contacts_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky='NS')

tree_frame.columnconfigure(0, weight=1)
tree_frame.rowconfigure(0, weight=1)

# Bind select event
contacts_tree.bind('<ButtonRelease-1>', select_contact)

# Query contacts
query_contacts()

# Run main loop
root.mainloop()
