import json
import os
import webbrowser
from tkinter import (
    Tk, Frame, Label, Button, Checkbutton,
    BooleanVar, Scrollbar, Canvas, VERTICAL, RIGHT, LEFT, Y, BOTH
)

PROCESSED_JOBS_FILE = "processed_jobs.json"

# =====================================================
# LOAD / SAVE DATA
# =====================================================

def load_jobs():
    if not os.path.exists(PROCESSED_JOBS_FILE):
        return {}
    with open(PROCESSED_JOBS_FILE, "r") as f:
        return json.load(f)

def save_jobs(data):
    with open(PROCESSED_JOBS_FILE, "w") as f:
        json.dump(data, f, indent=2)

jobs_data = load_jobs()

# =====================================================
# UI HELPERS
# =====================================================

def open_url(url):
    webbrowser.open(url)

def open_file(path):
    if os.path.exists(path):
        webbrowser.open(path)

def refresh():
    root.destroy()
    os.execv(__file__, ["python", __file__])

# =====================================================
# TKINTER SETUP
# =====================================================

root = Tk()
root.title("Resume Application Tracker")
root.geometry("1100x600")

main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=True)

canvas = Canvas(main_frame)
scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)

scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

# =====================================================
# HEADER
# =====================================================

headers = ["Job Title", "Applied", "Actions"]
for i, text in enumerate(headers):
    Label(
        scrollable_frame,
        text=text,
        font=("Arial", 11, "bold"),
        padx=10
    ).grid(row=0, column=i, sticky="w")

row_index = 1

# =====================================================
# POPULATE JOBS
# =====================================================

for url, data in jobs_data.items():
    if data.get("archived", False):
        continue

    job_title = data.get("job_title", "Unknown Job")
    resume_path = data.get("resume_path", "")
    applied_var = BooleanVar(value=data.get("applied", False))

    Label(
        scrollable_frame,
        text=job_title,
        wraplength=400,
        justify="left"
    ).grid(row=row_index, column=0, sticky="w", padx=10, pady=5)

    def make_applied_toggle(u, var):
        def toggle():
            jobs_data[u]["applied"] = var.get()
            save_jobs(jobs_data)
        return toggle

    Checkbutton(
        scrollable_frame,
        variable=applied_var,
        command=make_applied_toggle(url, applied_var)
    ).grid(row=row_index, column=1)

    action_frame = Frame(scrollable_frame)
    action_frame.grid(row=row_index, column=2, sticky="w")

    Button(
        action_frame,
        text="Open Job",
        command=lambda u=url: open_url(u)
    ).pack(side=LEFT, padx=2)

    Button(
        action_frame,
        text="Open Resume",
        command=lambda p=resume_path: open_file(p)
    ).pack(side=LEFT, padx=2)

    def make_archive(u):
        def archive():
            jobs_data[u]["archived"] = True
            save_jobs(jobs_data)
            refresh()
        return archive

    Button(
        action_frame,
        text="Archive",
        command=make_archive(url)
    ).pack(side=LEFT, padx=2)

    row_index += 1

# =====================================================
# FOOTER
# =====================================================

Label(
    root,
    text="Applied = checked | Archived jobs are hidden | State is saved automatically",
    pady=10
).pack()

root.mainloop()
