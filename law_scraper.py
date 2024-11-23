# Part 1: Imports and Base Classes
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import json
import random
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from threading import Thread, Lock, Event
from datetime import datetime
from queue import Queue
from typing import List, Dict, Set, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import deque
import uuid
import platform
import socket
import struct
import statistics

# Constants for stealth levels
STEALTH_LEVELS = {
    1: {
        "name": "Aggressive",
        "min_delay": 5,
        "max_delay": 15,
        "work_cycle": (30, 90),
        "rest_cycle": (10, 20),
        "backoff_factor": 1.5,
        "pattern_randomness": 0.2,
        "header_variation": 0.3
    },
    2: {
        "name": "Moderate",
        "min_delay": 10,
        "max_delay": 30,
        "work_cycle": (45, 120),
        "rest_cycle": (15, 30),
        "backoff_factor": 2.0,
        "pattern_randomness": 0.4,
        "header_variation": 0.5
    },
    3: {
        "name": "Conservative",
        "min_delay": 20,
        "max_delay": 60,
        "work_cycle": (60, 180),
        "rest_cycle": (20, 45),
        "backoff_factor": 2.5,
        "pattern_randomness": 0.6,
        "header_variation": 0.7
    },
    4: {
        "name": "Ultra-Conservative",
        "min_delay": 30,
        "max_delay": 120,
        "work_cycle": (90, 240),
        "rest_cycle": (30, 60),
        "backoff_factor": 3.0,
        "pattern_randomness": 0.8,
        "header_variation": 0.9
    }
}

class UserAgentRotator:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]

    def random(self):
        return random.choice(self.user_agents)

@dataclass
class ScraperMetrics:
    requests_made: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_response_time: float = 0
    average_response_time: float = 0
    detection_risk_score: float = 0
    pattern_entropy: float = 0
    last_update: float = 0

class DebugManager:
    def __init__(self):
        self.enabled = False
        self.window = None
        self.metrics = ScraperMetrics()
        self.update_queue = Queue()
        self.update_interval = 100  # ms
        self.metrics_history = {
            'response_times': deque(maxlen=1000),
            'success_rates': deque(maxlen=1000),
            'risk_scores': deque(maxlen=1000)
        }

    def initialize_window(self):
        if self.window is None:
            self.window = tk.Toplevel()
            self.window.title("Debug Information")
            self.window.geometry("800x600")
            self.setup_debug_ui()

    def setup_debug_ui(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Network tab
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text='Network')
        self.setup_network_tab(network_frame)

        # Performance tab
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text='Performance')
        self.setup_performance_tab(perf_frame)

        # Pattern Analysis tab
        pattern_frame = ttk.Frame(notebook)
        notebook.add(pattern_frame, text='Pattern Analysis')
        self.setup_pattern_tab(pattern_frame)

        # Storage tab
        storage_frame = ttk.Frame(notebook)
        notebook.add(storage_frame, text='Storage')
        self.setup_storage_tab(storage_frame)

        self.window.after(self.update_interval, self.update_debug_info)

    def setup_network_tab(self, parent):
        self.network_labels = {}
        metrics_frame = ttk.LabelFrame(parent, text="Network Metrics", padding=10)
        metrics_frame.pack(fill='x', padx=5, pady=5)

        metrics = [
            "Last Request Time",
            "Average Response Time",
            "Success Rate",
            "Active Connections",
            "Request Queue Size"
        ]

        for i, metric in enumerate(metrics):
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.network_labels[metric] = ttk.Label(metrics_frame, text="0")
            self.network_labels[metric].grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def setup_performance_tab(self, parent):
        self.perf_labels = {}
        metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill='x', padx=5, pady=5)

        metrics = [
            "CPU Usage",
            "Memory Usage",
            "Thread Count",
            "Queue Sizes",
            "Processing Rate"
        ]

        for i, metric in enumerate(metrics):
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.perf_labels[metric] = ttk.Label(metrics_frame, text="0")
            self.perf_labels[metric].grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def setup_pattern_tab(self, parent):
        self.pattern_labels = {}
        metrics_frame = ttk.LabelFrame(parent, text="Pattern Analysis", padding=10)
        metrics_frame.pack(fill='x', padx=5, pady=5)

        metrics = [
            "Detection Risk Score",
            "Pattern Entropy",
            "Behavior Score",
            "Timing Variation",
            "Request Distribution"
        ]

        for i, metric in enumerate(metrics):
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.pattern_labels[metric] = ttk.Label(metrics_frame, text="0")
            self.pattern_labels[metric].grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def setup_storage_tab(self, parent):
        self.storage_labels = {}
        metrics_frame = ttk.LabelFrame(parent, text="Storage Metrics", padding=10)
        metrics_frame.pack(fill='x', padx=5, pady=5)

        metrics = [
            "Data Size",
            "Cache Usage",
            "Save Frequency",
            "Load Time",
            "Processing Status"
        ]

        for i, metric in enumerate(metrics):
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.storage_labels[metric] = ttk.Label(metrics_frame, text="0")
            self.storage_labels[metric].grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def update_debug_info(self):
        if not self.window:
            return

        while not self.update_queue.empty():
            update = self.update_queue.get_nowait()
            self.process_update(update)

        self.window.after(self.update_interval, self.update_debug_info)

    def process_update(self, update):
        category, metric, value = update
        if category == 'network':
            self.network_labels[metric].config(text=str(value))
        elif category == 'performance':
            self.perf_labels[metric].config(text=str(value))
        elif category == 'pattern':
            self.pattern_labels[metric].config(text=str(value))
        elif category == 'storage':
            self.storage_labels[metric].config(text=str(value))

        if metric == 'response_time':
            self.metrics_history['response_times'].append(value)
        elif metric == 'success_rate':
            self.metrics_history['success_rates'].append(value)
        elif metric == 'risk_score':
            self.metrics_history['risk_scores'].append(value)

    def log_metric(self, category: str, metric: str, value: Union[str, float, int]):
        if self.enabled:
            self.update_queue.put((category, metric, value))

class StealthManager:
    def __init__(self):
        self.current_level = 2  # Default to Moderate
        self.custom_settings = {}
        self.user_agents = UserAgentRotator()
        self.last_request_time = 0
        self.request_count = 0

    def get_delay(self) -> float:
        base_delay = random.uniform(
            STEALTH_LEVELS[self.current_level]["min_delay"],
            STEALTH_LEVELS[self.current_level]["max_delay"]
        )

        progressive_factor = 1 + (self.request_count / 1000) * 0.1
        variation = random.gauss(0, base_delay * 0.1)

        return max(1, base_delay * progressive_factor + variation)

    def get_headers(self) -> Dict:
        return {
            'User-Agent': self.user_agents.random(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def should_take_break(self) -> bool:
        work_min, work_max = STEALTH_LEVELS[self.current_level]["work_cycle"]
        current_work_time = time.time() - self.last_request_time
        work_duration = random.uniform(work_min * 60, work_max * 60)
        return current_work_time >= work_duration

    def get_break_duration(self) -> float:
        rest_min, rest_max = STEALTH_LEVELS[self.current_level]["rest_cycle"]
        return random.uniform(rest_min * 60, rest_max * 60)

    def update_request_metrics(self):
        self.last_request_time = time.time()
        self.request_count += 1

    def get_min_work_time(self) -> float:
        # Minimum time to work before considering a break
        work_min, _ = STEALTH_LEVELS[self.current_level]["work_cycle"]
        return work_min * 30  # Return in seconds, reduced from full duration

class ControlPanel:
    def __init__(self, parent_frame, main_window):
        self.main_window = main_window
        self.frame = ttk.LabelFrame(parent_frame, text="Control Panel", padding="10")
        self.frame.pack(fill="x", expand=True)

        self.setup_profile_section()
        self.setup_timing_section()
        self.setup_cycle_section()
        self.setup_pattern_section()
        self.setup_debug_section()
        self.setup_scraping_controls()

        self.load_default_values()
        self.is_scraping = False

    def setup_profile_section(self):
        profile_frame = ttk.LabelFrame(self.frame, text="Configuration Profile", padding="5")
        profile_frame.pack(fill="x", pady=5)

        ttk.Label(profile_frame, text="Profile:").grid(row=0, column=0, padx=5, pady=2)
        self.profile_var = tk.StringVar(value="Default")
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var)
        self.profile_combo.grid(row=0, column=1, padx=5, pady=2)

        button_frame = ttk.Frame(profile_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=2)
        ttk.Button(button_frame, text="Save", command=self.save_profile).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Load", command=self.load_profile).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_profile).pack(side="left", padx=2)

    def setup_timing_section(self):
        timing_frame = ttk.LabelFrame(self.frame, text="Request Timing", padding="5")
        timing_frame.pack(fill="x", pady=5)

        self.base_delay_var = tk.DoubleVar()
        self.create_slider(timing_frame, "Base Delay:", self.base_delay_var, 0, 60, "seconds", 0)

        self.delay_var_var = tk.DoubleVar()
        self.create_slider(timing_frame, "Variation:", self.delay_var_var, 0, 30, "seconds", 1)

        self.prog_increase_var = tk.DoubleVar()
        self.create_slider(timing_frame, "Progressive Increase:", self.prog_increase_var, 0, 20, "%/hour", 2)

    def setup_cycle_section(self):
        cycle_frame = ttk.LabelFrame(self.frame, text="Work/Rest Cycles", padding="5")
        cycle_frame.pack(fill="x", pady=5)

        self.work_dur_var = tk.DoubleVar()
        self.create_slider(cycle_frame, "Work Duration:", self.work_dur_var, 30, 240, "minutes", 0)

        self.rest_dur_var = tk.DoubleVar()
        self.create_slider(cycle_frame, "Rest Duration:", self.rest_dur_var, 10, 60, "minutes", 1)

        self.cycle_var_var = tk.DoubleVar()
        self.create_slider(cycle_frame, "Random Variation:", self.cycle_var_var, 0, 30, "minutes", 2)

    def setup_pattern_section(self):
        pattern_frame = ttk.LabelFrame(self.frame, text="Pattern Controls", padding="5")
        pattern_frame.pack(fill="x", pady=5)

        self.req_rand_var = tk.DoubleVar()
        self.create_slider(pattern_frame, "Request Randomization:", self.req_rand_var, 0, 100, "%", 0)

        self.ua_freq_var = tk.DoubleVar()
        self.create_slider(pattern_frame, "User-Agent Frequency:", self.ua_freq_var, 5, 60, "minutes", 1)

        self.header_var_var = tk.DoubleVar()
        self.create_slider(pattern_frame, "Header Variation:", self.header_var_var, 0, 100, "%", 2)

    def setup_debug_section(self):
        debug_frame = ttk.LabelFrame(self.frame, text="Debug Controls", padding="5")
        debug_frame.pack(fill="x", pady=5)

        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(
            debug_frame,
            text="Enable Debug Mode",
            variable=self.debug_var,
            command=self.toggle_debug
        ).pack(side="left", padx=5)

        self.debug_window_btn = ttk.Button(
            debug_frame,
            text="Show Debug Window",
            command=self.show_debug_window,
            state="disabled"
        )
        self.debug_window_btn.pack(side="left", padx=5)

    def setup_scraping_controls(self):
        scrape_frame = ttk.LabelFrame(self.frame, text="Scraping Controls", padding="5")
        scrape_frame.pack(fill="x", pady=5)

        # Run Type
        ttk.Label(scrape_frame, text="Run Type:").grid(row=0, column=0, padx=5, pady=2)
        self.run_type = tk.StringVar(value="N")
        ttk.Radiobutton(scrape_frame, text="New", variable=self.run_type, value="N").grid(row=0, column=1)
        ttk.Radiobutton(scrape_frame, text="Restart", variable=self.run_type, value="R").grid(row=0, column=2)

        # URL Range
        ttk.Label(scrape_frame, text="URL Range:").grid(row=1, column=0, padx=5, pady=2)
        self.url_range = tk.StringVar()
        ttk.Entry(scrape_frame, textvariable=self.url_range, width=15).grid(row=1, column=1, columnspan=2)

        # Test Mode
        ttk.Label(scrape_frame, text="Test Count:").grid(row=2, column=0, padx=5, pady=2)
        self.test_count = tk.StringVar()
        ttk.Entry(scrape_frame, textvariable=self.test_count, width=10).grid(row=2, column=1, columnspan=2)

        # Start/Stop Button
        self.start_button = ttk.Button(scrape_frame, text="Start Scraping", command=self.toggle_scraping)
        self.start_button.grid(row=3, column=0, columnspan=3, pady=10)

    def create_slider(self, parent, label, variable, min_val, max_val, unit, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, padx=5, pady=2, sticky="w")

        slider = ttk.Scale(
            parent,
            from_=min_val,
            to=max_val,
            variable=variable,
            orient="horizontal"
        )
        slider.grid(row=row, column=1, padx=5, pady=2, sticky="ew")

        value_label = ttk.Label(parent, text=f"0 {unit}")
        value_label.grid(row=row, column=2, padx=5, pady=2, sticky="w")

        def update_label(*args):
            value_label.config(text=f"{variable.get():.1f} {unit}")

        variable.trace_add("write", update_label)
        parent.grid_columnconfigure(1, weight=1)

    def load_default_values(self):
        moderate = STEALTH_LEVELS[2]
        self.base_delay_var.set((moderate["min_delay"] + moderate["max_delay"]) / 2)
        self.delay_var_var.set(moderate["max_delay"] - moderate["min_delay"])
        self.work_dur_var.set(moderate["work_cycle"][1])
        self.rest_dur_var.set(moderate["rest_cycle"][1])
        self.req_rand_var.set(moderate["pattern_randomness"] * 100)
        self.header_var_var.set(moderate["header_variation"] * 100)

    def save_profile(self):
        name = simpledialog.askstring("Save Profile", "Enter profile name:")
        if name:
            profile = self.get_current_settings()

            profiles_dir = Path("profiles")
            profiles_dir.mkdir(exist_ok=True)

            with open(profiles_dir / f"{name}.json", "w") as f:
                json.dump(profile, f, indent=4)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(profiles_dir / f"auto_{timestamp}.json", "w") as f:
                json.dump(profile, f, indent=4)

            self.update_profile_list()

    def load_profile(self):
        if not self.profile_var.get():
            return

        profiles_dir = Path("profiles")
        profile_path = profiles_dir / f"{self.profile_var.get()}.json"

        if profile_path.exists():
            with open(profile_path) as f:
                profile = json.load(f)

            self.apply_profile_settings(profile)

    def apply_profile_settings(self, profile):
        self.base_delay_var.set(profile["base_delay"])
        self.delay_var_var.set(profile["delay_variation"])
        self.prog_increase_var.set(profile["progressive_increase"])
        self.work_dur_var.set(profile["work_duration"])
        self.rest_dur_var.set(profile["rest_duration"])
        self.cycle_var_var.set(profile["cycle_variation"])
        self.req_rand_var.set(profile["request_randomization"])
        self.ua_freq_var.set(profile["ua_frequency"])
        self.header_var_var.set(profile["header_variation"])

    def delete_profile(self):
        if not self.profile_var.get():
            return

        if messagebox.askyesno("Delete Profile", f"Delete profile {self.profile_var.get()}?"):
            profile_path = Path("profiles") / f"{self.profile_var.get()}.json"
            if profile_path.exists():
                profile_path.unlink()
            self.update_profile_list()

    def update_profile_list(self):
        profiles_dir = Path("profiles")
        profiles = [p.stem for p in profiles_dir.glob("*.json")
                   if not p.stem.startswith("auto_")]
        self.profile_combo["values"] = profiles

    def toggle_debug(self):
        self.debug_window_btn["state"] = "normal" if self.debug_var.get() else "disabled"

    def show_debug_window(self):
        pass  # Will be connected to DebugManager

    def get_current_settings(self):
        return {
            "base_delay": self.base_delay_var.get(),
            "delay_variation": self.delay_var_var.get(),
            "progressive_increase": self.prog_increase_var.get(),
            "work_duration": self.work_dur_var.get(),
            "rest_duration": self.rest_dur_var.get(),
            "cycle_variation": self.cycle_var_var.get(),
            "request_randomization": self.req_rand_var.get(),
            "ua_frequency": self.ua_freq_var.get(),
            "header_variation": self.header_var_var.get()
        }

    def toggle_scraping(self):
        if not self.is_scraping:
            try:
                range_start, range_end = map(int, self.url_range.get().split('-'))
                test_count = int(self.test_count.get()) if self.test_count.get() else None

                config = {
                    'run_type': self.run_type.get(),
                    'range_start': range_start,
                    'range_end': range_end,
                    'test_count': test_count
                }

                self.is_scraping = True
                self.start_button.config(text="Stop Scraping")
                self.main_window.start_scraping(config)

            except ValueError as e:
                messagebox.showerror("Error", "Invalid input format")
                return
        else:
            self.is_scraping = False
            self.start_button.config(text="Start Scraping")
            self.main_window.stop_scraping()

    def reset_scraping(self):
        self.is_scraping = False
        self.start_button.config(text="Start Scraping")

class GraphPanel:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Performance Graphs", padding="10")
        self.frame.pack(fill="x", padx=10, pady=5)

        # Collapsible section control
        self.is_expanded = tk.BooleanVar(value=False)
        self.toggle_btn = ttk.Checkbutton(
            self.frame,
            text="Show Graphs",
            variable=self.is_expanded,
            command=self.toggle_graphs
        )
        self.toggle_btn.pack(fill="x")

        # Graph container
        self.graph_frame = ttk.Frame(self.frame)

        # Data storage
        self.data = {
            'timestamps': deque(maxlen=1000),
            'success_rate': deque(maxlen=1000),
            'response_time': deque(maxlen=1000),
            'risk_score': deque(maxlen=1000)
        }

        # Initialize graphs
        self.setup_graphs()

        # Update timer
        self.update_interval = 30000  # 30 seconds
        self.last_update = time.time()

    def setup_graphs(self):
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 6), dpi=100)
        self.fig.tight_layout(pad=3.0)

        # Success Rate Graph
        self.ax1.set_title('Success Rate')
        self.ax1.set_ylabel('Rate (%)')
        self.success_line, = self.ax1.plot([], [], 'g-')
        self.ax1.grid(True)

        # Response Time Graph
        self.ax2.set_title('Response Time')
        self.ax2.set_ylabel('Time (s)')
        self.response_line, = self.ax2.plot([], [], 'b-')
        self.ax2.grid(True)

        # Risk Score Graph
        self.ax3.set_title('Detection Risk')
        self.ax3.set_ylabel('Risk Score')
        self.risk_line, = self.ax3.plot([], [], 'r-')
        self.ax3.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def toggle_graphs(self):
        if self.is_expanded.get():
            self.graph_frame.pack(fill="both", expand=True, pady=5)
        else:
            self.graph_frame.pack_forget()

    def update_data(self, success_rate, response_time, risk_score):
        current_time = time.time()

        self.data['timestamps'].append(current_time)
        self.data['success_rate'].append(success_rate)
        self.data['response_time'].append(response_time)
        self.data['risk_score'].append(risk_score)

        if current_time - self.last_update >= self.update_interval:
            self.update_graphs()
            self.last_update = current_time

    def update_graphs(self):
        if not self.is_expanded.get():
            return

        # Convert timestamps to relative time (minutes)
        times = [(t - min(self.data['timestamps'])) / 60 for t in self.data['timestamps']]

        # Update each graph
        self.success_line.set_data(times, self.data['success_rate'])
        self.ax1.relim()
        self.ax1.autoscale_view()

        self.response_line.set_data(times, self.data['response_time'])
        self.ax2.relim()
        self.ax2.autoscale_view()

        self.risk_line.set_data(times, self.data['risk_score'])
        self.ax3.relim()
        self.ax3.autoscale_view()

        self.canvas.draw_idle()

class LawScraper:
    def __init__(self, debug_manager, stealth_manager, status_callback):
        self.BASE_URL = "https://www.law.com/americanlawyer/law-firm-profile/?id={}"
        self.save_directory = None
        self.debug_manager = debug_manager
        self.stealth_manager = stealth_manager
        self.status_callback = status_callback

        # Initialize state
        self.is_running = False
        self.pause_event = Event()
        self.session = requests.Session()

        # Initialize stats
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0,
            'start_time': None
        }

        # Setup logger
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger('LawScraper')
        logger.setLevel(logging.INFO)

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create file handler
        log_file = log_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

        return logger

    def initialize(self, save_directory):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)

        self.logger.info("Starting scraper with direct connection mode")
        self.logger.info(f"Save directory: {self.save_directory}")
        self.logger.info(f"Stealth level: {self.stealth_manager.current_level}")

    def check_url(self, id):
        url = self.BASE_URL.format(id)
        self.logger.info(f"Attempting request to {url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            response = requests.get(url, headers=headers, timeout=10)
            self.logger.info(f"Response status code: {response.status_code}")

            if response.status_code == 200:
                # Save raw response content
                debug_dir = Path("debug_html")
                debug_dir.mkdir(exist_ok=True)

                # Save raw response
                with open(debug_dir / f"raw_response_{id}.txt", "wb") as f:
                    f.write(response.content)

                # Try to decode and save as text
                try:
                    content = response.content.decode('utf-8')
                    with open(debug_dir / f"decoded_response_{id}.html", "w", encoding='utf-8') as f:
                        f.write(content)
                except UnicodeDecodeError:
                    self.logger.warning("Could not decode response as UTF-8")

                # Log first 1000 characters of content
                self.logger.info(f"First 1000 chars of response: {str(response.content[:1000])}")

                # Check for key HTML patterns
                patterns_to_check = [
                    '<h1 class="page-title left"',
                    'class="overview-title"',
                    'class="survey-name-firms"',
                    'class="firms-para"'
                ]

                for pattern in patterns_to_check:
                    if pattern in str(response.content):
                        self.logger.info(f"Found pattern: {pattern}")
                    else:
                        self.logger.warning(f"Missing pattern: {pattern}")

                # Continue with normal processing
                soup = BeautifulSoup(response.content, "html.parser")
                firm_name = soup.find("h1", class_="page-title left")

                if firm_name:
                    self.stats['successful_requests'] += 1
                    self.update_success_metrics(True)
                    return url
                else:
                    self.logger.warning("No firm name found in parsed content")
                    # Log all h1 tags found
                    h1s = soup.find_all("h1")
                    if h1s:
                        self.logger.info(f"Found {len(h1s)} h1 tags: {[str(h1) for h1 in h1s]}")

            elif response.status_code == 429:
                self.logger.warning("Rate limit detected")
                time.sleep(60)
                return None

            self.update_success_metrics(False)
            return None

        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            self.update_success_metrics(False)
            return None

    def update_success_metrics(self, success):
        self.stats['requests_made'] += 1
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1

        success_rate = (self.stats['successful_requests'] / self.stats['requests_made']) * 100
        self.status_callback(f"Success Rate: {success_rate:.1f}%")

        if self.debug_manager.enabled:
            self.debug_manager.log_metric('network', 'Success Rate', f"{success_rate:.1f}%")

    def apply_cooldown(self):
        cooldown_time = random.uniform(300, 900)  # 5-15 minutes
        self.logger.info(f"Entering cooldown for {cooldown_time:.0f} seconds")
        self.status_callback(f"Cooling down for {cooldown_time/60:.1f} minutes...")
        time.sleep(cooldown_time)

    def crawl_ids(self, config, progress_window):
        self.is_running = True
        self.stats['start_time'] = time.time()

        last_id, discovered_urls = self.initialize_crawler(config)
        if last_id is None:
            return []

        max_id = config['test_count'] if config['test_count'] else config['range_end']
        total_remaining = max_id - last_id + 1
        processed = 0

        # Special handling for test mode
        is_test_mode = bool(config['test_count'])
        if is_test_mode:
            delay_range = (1, 3)  # 1-3 seconds delay in test mode
            self.logger.info("Running in test mode with shortened delays")
        else:
            current_level = self.stealth_manager.current_level
            delay_range = (
                STEALTH_LEVELS[current_level]["min_delay"],
                STEALTH_LEVELS[current_level]["max_delay"]
            )

        self.logger.info(f"Starting crawl from ID {last_id} to {max_id}")

        for current_id in range(last_id, max_id + 1):
            if not self.is_running:
                break

            processed += 1
            percentage = (processed / total_remaining) * 100

            self.logger.info(f"Checking ID: {current_id} ({percentage:.1f}% complete)")
            progress_window.update_crawler(percentage, f"Checking ID: {current_id}")

            try:
                url = self.check_url(current_id)
                if url:
                    discovered_urls.add(url)
                    self.logger.info(f"Found valid URL for ID {current_id}: {url}")
                else:
                    self.logger.info(f"No valid URL found for ID {current_id}")
            except Exception as e:
                self.logger.error(f"Error checking ID {current_id}: {str(e)}")

            # Add a small delay between requests
            delay = random.uniform(*delay_range)
            self.logger.info(f"Waiting {delay:.1f} seconds before next request")
            time.sleep(delay)

            # Save progress every 5 requests in test mode
            if is_test_mode and processed % 5 == 0:
                self.save_progress(current_id, discovered_urls)
                self.logger.info(f"Saved progress after {processed} requests")

        self.save_progress(max_id, discovered_urls)
        progress_window.update_crawler(100, "Crawling complete!")
        return list(discovered_urls)

    def initialize_crawler(self, config):
        progress_file = self.save_directory / 'crawler_progress.json'

        if config['run_type'] == 'N':
            last_id = config['range_start']
            discovered_urls = set()
            if progress_file.exists():
                progress_file.unlink()
        else:
            try:
                with open(progress_file) as f:
                    progress = json.load(f)
                    last_id = progress["last_id"]
                    discovered_urls = set(progress["discovered_urls"])

                    if last_id > config['range_end']:
                        messagebox.showwarning(
                            "Range Warning",
                            f"Last processed ID ({last_id}) is beyond specified range end ({config['range_end']})"
                        )
                        return None, None
            except FileNotFoundError:
                last_id = config['range_start']
                discovered_urls = set()

        return last_id, discovered_urls

    def save_progress(self, last_id, discovered_urls):
        progress_file = self.save_directory / 'crawler_progress.json'
        with open(progress_file, 'w') as f:
            json.dump({
                "last_id": last_id,
                "discovered_urls": list(discovered_urls)
            }, f)

    def scrape_data(self, discovered_urls, output_file, progress_window):
        all_data = []
        failed_urls = []

        for i, url in enumerate(discovered_urls):
            if not progress_window.is_running:
                break

            percentage = (i / len(discovered_urls)) * 100
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "html.parser")

                data = {
                    "URL": url,
                    "Firm Name": None,
                    "Am Law 200 Ranking": None,
                    "NLJ 500 Ranking": None,
                    "Equity Partners": None,
                    "Non-Equity Partners": None,
                    "Total Revenue": None,
                    "Profit Per Equity Partner": None,
                    "Revenue Per Lawyer": None,
                    "Total Headcount": None,
                    "Firm Description": None
                }

                try:
                    data["Firm Name"] = soup.find("h1", class_="page-title left").text.strip()
                except AttributeError:
                    pass

                try:
                    am_law_section = soup.find("p", string="Am Law 200").find_parent("div", class_="rankings")
                    am_law_2024 = am_law_section.find("p", class_="date-firms", string="2024").find_next_sibling("p", class_="rank-firms")
                    data["Am Law 200 Ranking"] = am_law_2024.text.strip().replace("#", "")
                except AttributeError:
                    pass

                try:
                    nlj_500_section = soup.find("p", string="NLJ 500").find_parent("div", class_="rankings")
                    nlj_500_2024 = nlj_500_section.find("p", class_="date-firms", string="2024").find_next_sibling("p", class_="rank-firms")
                    data["NLJ 500 Ranking"] = nlj_500_2024.text.strip().replace("#", "")
                except AttributeError:
                    pass

                metrics = {
                    "Equity Partners": "Equity Partners:",
                    "Non-Equity Partners": "Non-Equity Partners:",
                    "Total Revenue": "Total Revenue:",
                    "Profit Per Equity Partner": "Profit Per Equity Partner:",
                    "Revenue Per Lawyer": "Revenue Per Lawyer:",
                    "Total Headcount": "Total Headcount*:"
                }

                for key, label in metrics.items():
                    try:
                        data[key] = soup.find("p", string=label).find_next("div").text.strip()
                    except AttributeError:
                        pass

                # Get Firm Description
                try:
                    data["Firm Description"] = soup.find("p", class_="firms-para").text.strip()
                except AttributeError:
                    pass

                all_data.append(data)
                progress_window.update_scraper(percentage, f"Scraping: {data['Firm Name'] or 'Unknown Firm'}")

            except requests.RequestException as e:
                failed_urls.append((url, str(e)))
                progress_window.update_scraper(percentage, f"Error: {str(e)[:30]}...")

            time.sleep(random.uniform(self.MIN_DELAY, self.MAX_DELAY))

        df = pd.DataFrame(all_data)
        output_path = f"{output_file}.xlsx"
        df.to_excel(output_path, index=False)

        if failed_urls:
            failed_df = pd.DataFrame(failed_urls, columns=["URL", "Error"])
            failed_output_path = f"{output_file}_failed.xlsx"
            failed_df.to_excel(failed_output_path, index=False)

        progress_window.update_scraper(100, "Scraping complete!")
        return len(all_data), len(failed_urls)

    def extract_firm_data(self, soup, url):
        data = {
            "URL": url,
            "Firm Name": None,
            "Am Law 200 Ranking": None,
            "NLJ 500 Ranking": None,
            "Equity Partners": None,
            "Non-Equity Partners": None,
            "Total Revenue": None,
            "Profit Per Equity Partner": None,
            "Revenue Per Lawyer": None,
            "Total Headcount": None,
            "Firm Description": None
        }

        try:
            # Debug: Print all classes in the HTML
            all_classes = [elem.get('class', []) for elem in soup.find_all(class_=True)]
            self.logger.info(f"Found classes in HTML: {set([c for classes in all_classes for c in classes])}")

            # Debug: Check for overview-title elements
            overview_titles = soup.find_all("p", class_="overview-title")
            self.logger.info(f"Found overview titles: {[t.text for t in overview_titles]}")

            # Debug: Check for rankings elements
            rankings = soup.find_all("div", class_="rankings")
            self.logger.info(f"Found {len(rankings)} rankings divs")

            # Debug: Look for firm name specifically
            h1_elements = soup.find_all("h1")
            self.logger.info(f"Found h1 elements: {[h.get('class', []) for h in h1_elements]}")

            # Debug: Save raw HTML for inspection
            debug_dir = Path("debug_html")
            debug_dir.mkdir(exist_ok=True)
            with open(debug_dir / f"raw_page_{url.split('=')[-1]}.html", "w", encoding='utf-8') as f:
                f.write(str(soup.prettify()))

            # Now try to extract data
            # Firm Name
            firm_name = soup.find("h1", class_="page-title left")
            if firm_name:
                data["Firm Name"] = firm_name.text.strip()
                self.logger.info(f"Found firm name: {data['Firm Name']}")

            # Rankings
            # Am Law 200
            amlaw_section = soup.find("p", class_="survey-name-firms", string="Am Law 200")
            if amlaw_section:
                self.logger.info("Found Am Law section")
                rank_div = amlaw_section.find_parent("div", class_="rankings")
                if rank_div:
                    rank = rank_div.find("p", class_="rank-firms")
                    if rank:
                        data["Am Law 200 Ranking"] = rank.text.strip()
                        self.logger.info(f"Found Am Law rank: {data['Am Law 200 Ranking']}")

            # Metrics with overview-title
            metrics = {
                "Equity Partners": "Equity Partners:",
                "Non-Equity Partners": "Non-Equity Partners:",
                "Total Revenue": "Total Revenue:",
                "Profit Per Equity Partner": "Profit Per Equity Partner:",
                "Revenue Per Lawyer": "Revenue Per Lawyer:",
                "Total Headcount": "Total Headcount*:"
            }

            for key, title in metrics.items():
                title_elem = soup.find("p", class_="overview-title", string=title)
                if title_elem:
                    self.logger.info(f"Found title element for {key}")
                    value_div = title_elem.find_parent("div", class_="col-md-6").find_next_sibling("div", class_="col-md-6")
                    if value_div:
                        data[key] = value_div.text.strip()
                        self.logger.info(f"Found value for {key}: {data[key]}")

            # Firm Description
            desc = soup.find("p", class_="firms-para")
            if desc:
                data["Firm Description"] = desc.text.strip()
                self.logger.info("Found firm description")

            # Save what we found
            found_fields = [k for k, v in data.items() if v is not None]
            missing_fields = [k for k, v in data.items() if v is None]

            self.logger.info(f"Successfully extracted: {', '.join(found_fields)}")
            if missing_fields:
                self.logger.warning(f"Could not find: {', '.join(missing_fields)}")

        except Exception as e:
            self.logger.error(f"Error extracting data: {str(e)}")
            self.logger.error(f"Error details:", exc_info=True)

        return data

    def save_interim_data(self, all_data, failed_urls, output_file):
        interim_file = Path(f"{output_file}_interim.xlsx")
        pd.DataFrame(all_data).to_excel(interim_file, index=False)

        if failed_urls:
            failed_file = Path(f"{output_file}_failed_interim.xlsx")
            pd.DataFrame(failed_urls, columns=["URL", "Error"]).to_excel(
                failed_file, index=False
            )

    def save_final_data(self, all_data, failed_urls, output_file):
        final_file = Path(f"{output_file}.xlsx")
        pd.DataFrame(all_data).to_excel(final_file, index=False)

        if failed_urls:
            failed_file = Path(f"{output_file}_failed.xlsx")
            pd.DataFrame(failed_urls, columns=["URL", "Error"]).to_excel(
                failed_file, index=False
            )

        self.logger.info(f"Data saved to {final_file}")

class ProgressFrame:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        self.frame.pack(fill="x", padx=10, pady=5)

        # Crawler Progress
        self.crawler_frame = ttk.Frame(self.frame)
        self.crawler_frame.pack(fill="x", pady=2)
        ttk.Label(self.crawler_frame, text="Crawler:").pack(side="left", padx=5)
        self.crawler_progress = ttk.Progressbar(self.crawler_frame, length=400, mode='determinate')
        self.crawler_progress.pack(side="left", padx=5, fill="x", expand=True)
        self.crawler_label = ttk.Label(self.crawler_frame, text="0%")
        self.crawler_label.pack(side="left", padx=5)

        # Scraper Progress
        self.scraper_frame = ttk.Frame(self.frame)
        self.scraper_frame.pack(fill="x", pady=2)
        ttk.Label(self.scraper_frame, text="Scraper:").pack(side="left", padx=5)
        self.scraper_progress = ttk.Progressbar(self.scraper_frame, length=400, mode='determinate')
        self.scraper_progress.pack(side="left", padx=5, fill="x", expand=True)
        self.scraper_label = ttk.Label(self.scraper_frame, text="0%")
        self.scraper_label.pack(side="left", padx=5)

    def update_crawler(self, percentage, message=""):
        self.crawler_progress['value'] = percentage
        self.crawler_label.config(text=f"{percentage:.1f}%")

    def update_scraper(self, percentage, message=""):
        self.scraper_progress['value'] = percentage
        self.scraper_label.config(text=f"{percentage:.1f}%")


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Law Firm Data Scraper")
        self.root.geometry("1000x800")

        # Set up logger
        self.logger = logging.getLogger('MainWindow')

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Initialize managers
        self.debug_manager = DebugManager()
        self.stealth_manager = StealthManager()

        # Create components
        self.control_panel = ControlPanel(self.main_frame, self)
        self.progress_frame = ProgressFrame(self.main_frame)
        self.graph_panel = GraphPanel(self.main_frame)

        # Create status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill="x", side="bottom", pady=2)

        # Initialize scraper
        self.scraper = LawScraper(
            self.debug_manager,
            self.stealth_manager,
            self.update_status
        )

    def update_crawler(self, percentage, message=""):
        self.progress_frame.update_crawler(percentage, message)
        self.update_status(message)

    def update_scraper(self, percentage, message=""):
        self.progress_frame.update_scraper(percentage, message)
        self.update_status(message)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def start_scraping(self, config):
        # Get save info before starting thread
        save_dir = filedialog.askdirectory(title="Select save directory")
        if not save_dir:
            return

        file_name = simpledialog.askstring("File Name", "Enter a name for the output file (without extension):")
        if not file_name:
            return

        def run_scraper():
            try:
                # Initialize scraper
                self.scraper.initialize(save_dir)

                # Run crawling process
                logging.info("Starting crawling phase...")
                discovered_urls = self.scraper.crawl_ids(config, self)

                if discovered_urls:
                    logging.info(f"Crawling complete. Found {len(discovered_urls)} URLs. Starting scraping phase...")
                    success_count, fail_count = self.scraper.scrape_data(
                        discovered_urls,
                        f"{save_dir}/{file_name}",
                        self
                    )
                    logging.info(f"Scraping complete. Successful: {success_count}, Failed: {fail_count}")
                else:
                    logging.warning("No valid URLs found during crawling phase.")
                    messagebox.showwarning("Scraping Complete", "No valid URLs were found to scrape.")

            except Exception as e:
                logging.error(f"Scraping failed: {str(e)}")
                messagebox.showerror("Error", f"Scraping failed: {str(e)}")
            finally:
                self.control_panel.reset_scraping()

        # Start scraping thread with collected info
        Thread(target=run_scraper, daemon=True).start()

    def stop_scraping(self):
        if hasattr(self, 'scraper'):
            self.scraper.is_running = False

    def start(self):
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        parser.add_argument(
            "--debug-level",
            type=int,
            choices=[1,2,3],
            default=1,
            help="Debug detail level"
        )
        args = parser.parse_args()

        # Initialize debug mode if specified
        if args.debug:
            self.debug_manager.enabled = True
            self.control_panel.debug_var.set(True)
            self.control_panel.debug_window_btn.config(state="normal")
            if args.debug_level > 1:
                self.debug_manager.initialize_window()

        # Start the GUI
        self.root.mainloop()

def main():
    # Set up logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    try:
        app = MainWindow()
        app.start()
    except Exception as e:
        logging.critical(f"Application crashed: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"Application crashed: {str(e)}\nCheck logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
