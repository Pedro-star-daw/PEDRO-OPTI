import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from optimizer import (
    backup_startup_entries,
    clean_temp_files,
    disable_startup_entries,
    flush_dns,
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
    list_startup_entries,
    optimize_power_plan,
    optimize_visual_effects,
    restore_startup_entries,
    run_all_safe_tweaks,
)


class PedroOptiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PEDRO OPTI")
        self.geometry("900x620")
        self.minsize(820, 540)
        self.configure(bg="#111827")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=10, background="#2563eb", foreground="#ffffff")
        self.style.configure("TLabel", background="#111827", foreground="#e5e7eb")
        self.style.configure("TFrame", background="#111827")
        self.style.configure("TEntry", fieldbackground="#0f172a", foreground="#e5e7eb")
        self.style.map("TButton", background=[("active", "#3b82f6")])

        self.title_label = ttk.Label(self, text="PEDRO OPTI", font=("Segoe UI", 24, "bold"))
        self.title_label.pack(pady=(16, 10))

        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill="x", padx=18, pady=(0, 12))

        self.cpu_var = tk.StringVar(value="CPU: --")
        self.ram_var = tk.StringVar(value="RAM: --")
        self.disk_var = tk.StringVar(value="Disk: --")

        ttk.Label(self.stats_frame, textvariable=self.cpu_var, font=("Segoe UI", 11)).grid(row=0, column=0, padx=10, sticky="w")
        ttk.Label(self.stats_frame, textvariable=self.ram_var, font=("Segoe UI", 11)).grid(row=0, column=1, padx=10, sticky="w")
        ttk.Label(self.stats_frame, textvariable=self.disk_var, font=("Segoe UI", 11)).grid(row=0, column=2, padx=10, sticky="w")

        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill="x", padx=18, pady=(0, 12))

        actions = [
            ("Clean Temp", clean_temp_files),
            ("Flush DNS", flush_dns),
            ("Power Boost", optimize_power_plan),
            ("Visual Tweak", optimize_visual_effects),
            ("Run All", run_all_safe_tweaks),
            ("Backup Startup", backup_startup_entries),
            ("Restore Startup", restore_startup_entries),
        ]

        for i, (label, action) in enumerate(actions):
            btn = ttk.Button(self.action_frame, text=label, command=lambda a=action: self.run_task(a))
            btn.grid(row=0, column=i, padx=6, sticky="ew")
            self.action_frame.grid_columnconfigure(i, weight=1)

        self.content = ttk.Frame(self)
        self.content.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        self.startup_panel = ttk.Frame(self.content)
        self.startup_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ttk.Label(self.startup_panel, text="Startup Programs", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))

        self.startup_listbox = tk.Listbox(self.startup_panel, bg="#0f172a", fg="#e5e7eb", selectbackground="#2563eb", height=16)
        self.startup_listbox.pack(fill="both", expand=True)

        self.startup_buttons = ttk.Frame(self.startup_panel)
        self.startup_buttons.pack(fill="x", pady=(8, 0))

        ttk.Button(self.startup_buttons, text="Refresh", command=self.refresh_startup_list).pack(side="left", padx=(0, 6))
        ttk.Button(self.startup_buttons, text="Disable Selected", command=self.disable_selected_startup).pack(side="left", padx=(0, 6))
        ttk.Button(self.startup_buttons, text="Restore Startup", command=lambda: self.run_task(restore_startup_entries)).pack(side="left")

        self.output_panel = ttk.Frame(self.content)
        self.output_panel.pack(side="right", fill="both", expand=True)

        ttk.Label(self.output_panel, text="Activity Log", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        self.output = scrolledtext.ScrolledText(self.output_panel, wrap=tk.WORD, height=18, bg="#0f172a", fg="#e5e7eb", insertbackground="#ffffff")
        self.output.pack(fill="both", expand=True)
        self.output.insert(tk.END, "PEDRO OPTI is ready.\n")
        self.output.configure(state="disabled")

        self.refresh_stats_loop()
        self.refresh_startup_list()

    def log(self, text):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def run_task(self, func):
        def worker():
            try:
                self.log(f"Running: {func.__name__}...")
                result = func()
                if isinstance(result, dict) and "message" in result:
                    self.log(result["message"])
                elif isinstance(result, str):
                    self.log(result)
                else:
                    self.log(f"Completed: {func.__name__}")
            except Exception as exc:
                self.log(f"Error: {exc}")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_stats_loop(self):
        try:
            self.cpu_var.set(f"CPU: {get_cpu_usage()}%")
            self.ram_var.set(f"RAM: {get_memory_usage()}%")
            self.disk_var.set(f"Disk: {get_disk_usage()}%")
        except Exception:
            self.cpu_var.set("CPU: unavailable")
            self.ram_var.set("RAM: unavailable")
            self.disk_var.set("Disk: unavailable")
        self.after(3000, self.refresh_stats_loop)

    def refresh_startup_list(self):
        self.startup_listbox.delete(0, tk.END)
        entries = list_startup_entries()
        if not entries:
            self.startup_listbox.insert(tk.END, "No startup items found.")
            return
        for entry in entries:
            value = entry.get("name", "Unknown")
            self.startup_listbox.insert(tk.END, value)

    def disable_selected_startup(self):
        selected = self.startup_listbox.curselection()
        if not selected:
            messagebox.showinfo("PEDRO OPTI", "Select one or more startup items first.")
            return

        choices = [self.startup_listbox.get(index) for index in selected]
        result = disable_startup_entries(choices)
        self.log(result.get("message", "Startup items updated."))
        self.refresh_startup_list()


if __name__ == "__main__":
    app = PedroOptiApp()
    app.mainloop()
