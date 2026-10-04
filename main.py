import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

from optimizer import (
    clean_temp_files,
    flush_dns,
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
    optimize_power_plan,
    optimize_visual_effects,
    run_all_safe_tweaks,
)


class PedroOptiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PEDRO OPTI")
        self.geometry("780x520")
        self.minsize(700, 420)
        self.configure(bg="#101820")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=8, background="#2f80ed", foreground="#ffffff")
        self.style.configure("TLabel", background="#101820", foreground="#eaf2ff")
        self.style.configure("TFrame", background="#101820")
        self.style.map("TButton", background=[("active", "#4d9aff")])

        self.title_label = ttk.Label(self, text="PEDRO OPTI", font=("Segoe UI", 22, "bold"))
        self.title_label.pack(pady=(16, 8))

        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.cpu_var = tk.StringVar(value="CPU: --")
        self.ram_var = tk.StringVar(value="RAM: --")
        self.disk_var = tk.StringVar(value="Disk: --")

        ttk.Label(self.top_frame, textvariable=self.cpu_var, font=("Segoe UI", 11)).grid(row=0, column=0, padx=10, sticky="w")
        ttk.Label(self.top_frame, textvariable=self.ram_var, font=("Segoe UI", 11)).grid(row=0, column=1, padx=10, sticky="w")
        ttk.Label(self.top_frame, textvariable=self.disk_var, font=("Segoe UI", 11)).grid(row=0, column=2, padx=10, sticky="w")

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill="x", padx=16, pady=(0, 12))

        actions = [
            ("Clean Temp Files", clean_temp_files),
            ("Flush DNS", flush_dns),
            ("High Performance Mode", optimize_power_plan),
            ("Reduce Visual Effects", optimize_visual_effects),
            ("Apply All Safe Tweaks", run_all_safe_tweaks),
        ]

        for i, (label, action) in enumerate(actions):
            button = ttk.Button(self.button_frame, text=label, command=lambda a=action: self.run_task(a))
            button.grid(row=0, column=i, padx=8, sticky="ew")
            self.button_frame.grid_columnconfigure(i, weight=1)

        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=18, bg="#111b24", fg="#eaf2ff", insertbackground="#ffffff")
        self.output.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.output.insert(tk.END, "PEDRO OPTI is ready. Select an action to begin.\n")
        self.output.configure(state="disabled")

        self.refresh_stats_loop()

    def log(self, text):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def run_task(self, func):
        def worker():
            try:
                self.log(f"Starting: {func.__name__}...")
                result = func()
                if isinstance(result, str):
                    self.log(result)
                elif isinstance(result, dict):
                    if "message" in result:
                        self.log(result["message"])
                    else:
                        self.log(str(result))
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


if __name__ == "__main__":
    app = PedroOptiApp()
    app.mainloop()

