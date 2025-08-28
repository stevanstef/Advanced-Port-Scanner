import time
from tkinter import *
from tkinter import ttk
import subprocess
import threading
import platform
import subprocess
from datetime import datetime
from tkinter import filedialog
import csv
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

global process 
process = None
global scan_running 
scan_running = False
global display_percent
display_percent = 0

root = ttk.Window(themename="flatly")
root.title("Advanced Port Scanner")

frm = ttk.Frame(root, padding=20)
frm.grid()

live_feed = Text(frm, height=10, width=70, wrap="word", state='disabled')
live_feed.grid(column=0, row=1, columnspan=2, pady=(0, 15))

ttk.Label(frm, text="Target IP or Domain:").grid(column=0, row=3, sticky=E, padx=(0, 10), pady=6)
target = ttk.Entry(frm, width=30)
target.grid(column=1, row=3, sticky=W)
target.insert(0, "127.0.0.1")

ttk.Label(frm, text="Start Port:").grid(column=0, row=4, sticky=E, padx=(0, 10), pady=6)
port_start = ttk.Entry(frm, width=10)
port_start.grid(column=1, row=4, sticky=W)
port_start.insert(0, "0")

ttk.Label(frm, text="End Port:").grid(column=0, row=5, sticky=E, padx=(0, 10), pady=6)
port_end = ttk.Entry(frm, width=10)
port_end.grid(column=1, row=5, sticky=W)
port_end.insert(0, "65535")

def run_scan(target_text, port_start_text, port_end_text):
    global process, scan_running, port_count, display_percent
    if process is not None and process.poll() is None:
        process.kill()
        live_feed.config(state='normal')
        live_feed.delete("1.0", END)
        live_feed.config(state='disabled')
        process = None
        return

    scan_button.config(text="Kill")
    live_feed.config(state='normal')
    live_feed.delete("1.0", END)
    live_feed.config(state='disabled')

    creationflags = 0
    if os.name == "nt":  # Only for Windows
        creationflags = subprocess.CREATE_NO_WINDOW

    process = subprocess.Popen(
        ["py", "-u", "scan.py", target_text, str(port_start_text), str(port_end_text)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,          
        bufsize=1,
        creationflags=creationflags  
    )
    total = int(port_end_text)-int(port_start_text) + 1
    port_count = 0
    for line in process.stdout:
        line = line.strip()
        if line.startswith("PROGRESS"):
            port_count = int(line.split()[1])
        else:
            live_feed.config(state='normal')
            live_feed.insert(END, f"{line}\n")
            live_feed.see(END)
            display_percent = int((port_count / total)*100)
            live_feed.config(state='disabled')
    scan_button.config(text="Scan")
    port_count = 0
    display_percent = int((port_count / total)*100)
    time.sleep(0.03)
    scan_running = False
    if process is not None:
        if process.stdout:
            process.stdout.close()
        process.wait()
    process = None

def ping():
    global scan_running
    if scan_running:
        return
    scan_running = True
    live_feed.config(state='normal')
    live_feed.delete("1.0", END)
    live_feed.config(state='disabled')
    target_text = target.get().strip()
    live_feed.config(state='normal')
    live_feed.insert("end", f"Pinging {target_text}...\n")
    live_feed.see(END)
    live_feed.config(state='disabled')

    root.after(500, lambda: show_ping_result(target_text))

def show_ping_result(host):
    global scan_running
    if ping_host(host):
        result_text = f"{host} is ALIVE\n"
    else:
        result_text = f"{host} is DOWN\n"
    live_feed.config(state='normal')
    live_feed.insert("end", result_text)
    live_feed.see(END)
    live_feed.config(state='disabled')
    scan_running = False

def ping_host(host):     
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        ping_process = subprocess.run(
            ["ping", param, "1", str(host)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return ping_process.returncode == 0
    except Exception:
        return False
    
def run_progress():
    while(scan_running == True):
        progress['value'] = display_percent
        percent_label.configure(text=f"{display_percent}%")
        root.update()
        time.sleep(0.03)
    
def scan_start():
    global scan_running
    target_text = target.get().strip()
    port_start_text = int(port_start.get().strip())
    port_end_text = int(port_end.get().strip())
    scan_running = True
    threading.Thread(target=run_progress, daemon=True).start()
    threading.Thread(target=run_scan, args=(target_text, port_start_text, port_end_text), daemon=True).start()

def toggle_theme():
    if theme_switch.instate(['selected']):
        root.style.theme_use("darkly")
        scan_button.configure(bootstyle="success")
        progress.configure(bootstyle="success")
    else:
        root.style.theme_use("flatly")
        scan_button.configure(bootstyle="primary")
        progress.configure(bootstyle="primary")

def export_to_csv():
    text_content = live_feed.get("1.0", "end").strip()
    
    lines = text_content.splitlines()
    rows = [[line] for line in lines]

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", 
        initialfile="port_scanner_export",
        filetypes=[("CSV files", "*.csv")]
    )

    if not file_path:
        return

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

scan_button = ttk.Button(frm, text="Scan", bootstyle="primary", command=scan_start)
scan_button.grid(column=0, row=0, padx=10, pady=10)
ping_button = ttk.Button(frm, text="Ping", bootstyle="secondary", command=ping)
ping_button.grid(column=1, row=0, padx=10, pady=10)

export_button = ttk.Button(root, text="Export to CSV", bootstyle="secondary", command=export_to_csv)
export_button.grid(column=2, row=0, padx=10, pady=10)

progress_frame = ttk.Frame(frm)
progress_frame.grid(column=0, row=2, columnspan=2, pady=(10, 15))

percent_label = ttk.Label(progress_frame, text="0%", font=("Segoe UI", 10, "bold"))
percent_label.pack(pady=(0))

bottom_frame = ttk.Frame(root)
bottom_frame.grid(row=5, column=0, sticky="sw")

profile = ttk.Label(bottom_frame, text="© 2025 Stevan Stefanovic", font=("Segoe UI", 8, "bold"))
profile.pack(side="left", anchor="sw", padx=0, pady=0)

progress = ttk.Progressbar(progress_frame, length=400, bootstyle="primary", maximum=100)
progress.pack()

theme_switch = ttk.Checkbutton(
    root,
    text="",
    bootstyle="success-round-toggle",
    command=toggle_theme
)
theme_switch.grid(column=4, row=5, padx=10, pady=10)

root.mainloop()