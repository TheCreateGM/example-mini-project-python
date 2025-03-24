import hashlib
import random
import socket
import requests
import time
import json
import tkinter as tk
from tkinter import ttk, scrolledtext
import sqlite3
from tkinter import messagebox

# Detailed mock geolocation data mapping for our worldwide sting simulation
GEO_ZONES = {
    "NA": {"range": (1, 63), "desc": "North America"},
    "EU": {"range": (77, 95), "desc": "Europe"},
    "AS": {"range": (101, 126), "desc": "Asia"},
    "SA": {"range": (179, 189), "desc": "South America"},
    "AF": {"range": (196, 211), "desc": "Africa"},
    "OC": {"range": (218, 223), "desc": "Oceania"}
}

def get_worldwide_public_ip(discord_id):
    # Compute a secure hash of the provided Discord ID to generate a consistent random seed.
    hash_obj = hashlib.sha256(discord_id.encode()).hexdigest()
    seed = int(hash_obj, 16) % 2**32
    random.seed(seed)

    # Deterministically select a region from our predefined geo-zones.
    region = random.choice(list(GEO_ZONES.keys()))
    ip_start, ip_end = GEO_ZONES[region]["range"]

    # Generate a preliminary public IP within the chosen region's range, using random values.
    public_ip = f"{random.randint(ip_start, ip_end)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    # Attempt to refine the public IP by merging it with a real base IP fetched online.
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        base_ip = json.loads(response.text)["ip"]
        octets = base_ip.split(".")
        # Replace the first octet with a randomized value within our region's numeric range.
        octets[0] = str(random.randint(ip_start, ip_end))
        public_ip = ".".join(octets)
    except Exception:
        # If fetching the real IP fails, the simulation continues with the randomly generated IP.
        pass

    return public_ip, GEO_ZONES[region]["desc"]

def resolve_private_ip(discord_id):
    # Use the same hash principle to generate a consistent private IP address.
    hash_obj = hashlib.sha256(discord_id.encode()).hexdigest()
    seed = int(hash_obj, 16) % 2**32
    random.seed(seed)
    # Construct a private IP from the 192.168 subnet with detailed randomization.
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

def fake_global_scan(discord_id):
    # Simulate a comprehensive global scan by adding a delay to mimic network probing.
    time.sleep(0.9)  # Adding deliberate latency for realism.

    # Emulate packet transmission using a UDP socket to mimic network scanning activity.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(discord_id.encode(), ("1.1.1.1", 53))
        sock.close()
    except Exception:
        # Failures in packet transmission do not halt the simulation.
        pass

    # Derive simulated private and public IPs alongside geographic region data.
    private_ip = resolve_private_ip(discord_id)
    public_ip, region = get_worldwide_public_ip(discord_id)
    return private_ip, public_ip, region

def save_to_database(discord_id, private_ip, public_ip, region):
    conn = sqlite3.connect('scan_results.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_results (
            discord_id TEXT PRIMARY KEY,
            private_ip TEXT,
            public_ip TEXT,
            region TEXT
        )
    ''')
    cursor.execute('''
        INSERT OR REPLACE INTO scan_results (discord_id, private_ip, public_ip, region)
        VALUES (?, ?, ?, ?)
    ''', (discord_id, private_ip, public_ip, region))
    conn.commit()
    conn.close()

def view_database():
    def fetch_data():
        conn = sqlite3.connect('scan_results.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scan_results')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def on_close():
        db_window.destroy()

    db_window = tk.Toplevel()
    db_window.title("Database Records")
    db_window.geometry("700x400")
    db_window.configure(bg="#f0f0f0")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Treeview', font=('Arial', 11), rowheight=25)
    style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

    tree_frame = ttk.Frame(db_window)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, columns=("discord_id", "private_ip", "public_ip", "region"), show='headings')
    tree.pack(fill=tk.BOTH, expand=True)

    tree_scroll.config(command=tree.yview)

    tree.heading("discord_id", text="Discord ID")
    tree.heading("private_ip", text="Private IP")
    tree.heading("public_ip", text="Public IP")
    tree.heading("region", text="Region")

    for row in fetch_data():
        tree.insert("", tk.END, values=row)

    close_button = ttk.Button(db_window, text="Close", command=on_close)
    close_button.pack(pady=10)

def convert_id_to_ip():
    def on_submit():
        discord_id = entry.get().strip()
        if not discord_id.isdigit():
            messagebox.showerror("Invalid Input", "Discord ID must consist of digits only.")
            return

        # Update progress
        progress_label.config(text="Scanning in progress...")
        progress_bar["value"] = 20
        root.update()
        time.sleep(0.3)

        progress_bar["value"] = 40
        root.update()

        # Perform the scan
        private_ip, public_ip, region = fake_global_scan(discord_id)

        progress_bar["value"] = 80
        root.update()
        time.sleep(0.2)

        # Save results
        save_to_database(discord_id, private_ip, public_ip, region)

        progress_bar["value"] = 100
        progress_label.config(text="Scan completed!")
        root.update()

        # Display results in a clear format
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "--- SCAN RESULTS ---\n\n", "header")
        result_text.insert(tk.END, "Target Discord ID: ", "label")
        result_text.insert(tk.END, f"{discord_id}\n\n", "value")

        result_text.insert(tk.END, "Private IP Address: ", "label")
        result_text.insert(tk.END, f"{private_ip}\n\n", "value")

        result_text.insert(tk.END, "Public IP Address: ", "label")
        result_text.insert(tk.END, f"{public_ip}\n\n", "value")

        result_text.insert(tk.END, "Geographic Region: ", "label")
        result_text.insert(tk.END, f"{region}\n\n", "value")

        result_text.insert(tk.END, "Data retrieval complete!", "success")
        result_text.config(state=tk.DISABLED)

        # Reset progress bar after completion
        progress_bar["value"] = 0

    # Set up the main window
    root = tk.Tk()
    root.title("Network Scan Interface")
    root.geometry("700x600")
    root.configure(bg="#f0f0f0")

    # Apply a modern style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Arial', 11), background='#4a7abc', foreground='white')
    style.configure('TLabel', font=('Arial', 11), background='#f0f0f0')
    style.configure('TFrame', background='#f0f0f0')
    style.configure('TProgressbar', thickness=8, background='#4a7abc')

    # Create a main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create a header
    header_label = ttk.Label(main_frame, text="Discord Detect Interface", font=('Arial', 18, 'bold'))
    header_label.pack(pady=10)

    # Create description
    description = ttk.Label(main_frame, text="Enter a Discord ID to perform a worldwide network scan",
                         font=('Arial', 11))
    description.pack(pady=5)

    # Create a frame for input
    input_frame = ttk.Frame(main_frame)
    input_frame.pack(fill=tk.X, pady=15)

    # Create input label and entry
    input_label = ttk.Label(input_frame, text="Discord ID (numbers only):")
    input_label.pack(side=tk.LEFT, padx=5)

    entry = ttk.Entry(input_frame, width=30, font=('Arial', 11))
    entry.pack(side=tk.LEFT, padx=5)

    # Create a scan button
    scan_button = ttk.Button(input_frame, text="Start Scan", command=on_submit)
    scan_button.pack(side=tk.LEFT, padx=5)

    # Create a view database button
    view_db_button = ttk.Button(input_frame, text="View Database", command=view_database)
    view_db_button.pack(side=tk.LEFT, padx=5)

    # Create a frame for progress
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=10)

    progress_label = ttk.Label(progress_frame, text="Ready to scan")
    progress_label.pack(anchor=tk.W, padx=5, pady=5)

    progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=650, mode='determinate')
    progress_bar.pack(fill=tk.X, padx=5)

    # Create a frame for results
    result_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding=10)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # Create a scrolled text widget for results
    result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15, font=('Consolas', 11))
    result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    result_text.config(state=tk.DISABLED)

    # Configure text tags for styling
    result_text.tag_configure("header", font=('Arial', 12, 'bold'), foreground='#4a7abc')
    result_text.tag_configure("label", font=('Arial', 10, 'bold'))
    result_text.tag_configure("value", font=('Consolas', 10))
    result_text.tag_configure("success", font=('Arial', 10, 'bold'), foreground='green')

    # Add footer
    footer = ttk.Label(main_frame, text="All scans are simulated for educational purposes", font=('Arial', 9))
    footer.pack(pady=5)

    # Set focus to entry
    entry.focus()

    # Bind Enter key to submit function
    root.bind('<Return>', lambda event: on_submit())

    root.mainloop()

if __name__ == '__main__':
    convert_id_to_ip()
