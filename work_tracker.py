import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import datetime
import webbrowser
from pathlib import Path
import shutil
import time

class WorkTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Work Tracker - By Abdelrhman Hamed")
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set window to full screen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.state('zoomed')
        self.root.minsize(1024, 768)
        self.root.resizable(True, True)
        
        # Set working directory
        self.work_dir = Path("D:/Python Automation/WorkTracker")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.data_file = self.work_dir / "work_data.json"
        self.review_file = self.work_dir / "review_data.json"
        self.output_file = self.work_dir / "weekly_report.txt"
        self.temp_file = self.work_dir / "temp_data.json"
        self.timer_file = self.work_dir / "timer_state.json"
        self.backup_dir = self.work_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load existing data
        self.data = self.load_data()
        self.review_data = self.load_review_data()
        self.temp_data = self.load_temp_data()
        
        # Current tasks
        self.tasks = []
        self.completed_tasks = []
        self.plan_items = []
        self.completed_plan_items = []
        self.notes = ""  # new: daily notes
        
        # Track time
        self.start_time = None
        self.is_tracking = False
        self.login_time = None
        self.current_entry = None
        self.elapsed_seconds = 0
        
        # Load timer state
        self.load_timer_state()
        
        # Configure style
        self.setup_styles()
        
        # Create UI
        self.create_notebook()
        
        # Load previous session if exists
        self.load_previous_session()
        
        # Auto-check functions
        self.check_auto_start()
        self.check_end_of_day()
        self.check_thursday_review()
        
        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Setup custom styles for better UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        title_font_size = min(20, int(self.screen_width / 60))
        header_font_size = min(12, int(self.screen_width / 90))
        timer_font_size = min(32, int(self.screen_width / 35))
        
        style.configure('Title.TLabel', font=('Arial', title_font_size, 'bold'))
        style.configure('Header.TLabel', font=('Arial', header_font_size, 'bold'))
        style.configure('Status.TLabel', font=('Arial', max(10, int(header_font_size * 0.8))))
        style.configure('Timer.TLabel', font=('Arial', timer_font_size, 'bold'), foreground='#2E86C1')
        style.configure('Signature.TLabel', font=('Arial', max(9, int(header_font_size * 0.7)), 'italic'), 
                       foreground='#808080')
        style.configure('Action.TButton', font=('Arial', max(10, int(header_font_size * 0.8))), padding=6)
        style.configure('Danger.TButton', font=('Arial', max(10, int(header_font_size * 0.8))), padding=6, 
                       foreground='red')
        style.configure('Logout.TButton', font=('Arial', max(10, int(header_font_size * 0.8))), padding=6,
                       foreground='white', background='#c0392b')
    
    # ========== TIMER STATE MANAGEMENT ==========
    def save_timer_state(self):
        timer_state = {
            "is_tracking": self.is_tracking,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "login_time": self.login_time,
            "elapsed_seconds": self.elapsed_seconds,
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        with open(self.timer_file, 'w', encoding='utf-8') as f:
            json.dump(timer_state, f, indent=2, ensure_ascii=False)
    
    def load_timer_state(self):
        if self.timer_file.exists():
            try:
                with open(self.timer_file, 'r', encoding='utf-8') as f:
                    timer_state = json.load(f)
                
                if timer_state.get("date") == datetime.datetime.now().strftime("%Y-%m-%d"):
                    self.is_tracking = timer_state.get("is_tracking", False)
                    self.elapsed_seconds = timer_state.get("elapsed_seconds", 0)
                    self.login_time = timer_state.get("login_time")
                    
                    if timer_state.get("start_time"):
                        try:
                            self.start_time = datetime.datetime.fromisoformat(timer_state["start_time"])
                        except:
                            self.start_time = None
                    
                    if self.is_tracking and self.start_time:
                        now = datetime.datetime.now()
                        elapsed = (now - self.start_time).total_seconds()
                        self.elapsed_seconds = elapsed
                        self.update_timer_display()
                        self.update_timer()
                        self.status_label.config(text="⏳ Status: Working (background)...")
                        return True
                else:
                    self.is_tracking = False
                    self.elapsed_seconds = 0
                    self.start_time = None
                    self.save_timer_state()
            except Exception as e:
                print(f"Error loading timer state: {e}")
                self.is_tracking = False
                self.elapsed_seconds = 0
                self.start_time = None
        return False
    
    def get_elapsed_time(self):
        if self.is_tracking and self.start_time:
            now = datetime.datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            self.elapsed_seconds = elapsed
            self.save_timer_state()
            return elapsed
        return self.elapsed_seconds
    
    def update_timer_display(self):
        elapsed = self.get_elapsed_time()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if self.login_time:
            try:
                login_h, login_m = map(int, self.login_time.split(':'))
                now = datetime.datetime.now()
                login_dt = datetime.datetime(now.year, now.month, now.day, login_h, login_m)
                worked = (now - login_dt).seconds / 3600
                self.time_info_label.config(text=f"⏱️ Since login: {worked:.1f} hours")
            except:
                pass
    
    # ========== CREATE NOTEBOOK ==========
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.daily_frame, text="📋 Daily Work")
        self.create_daily_tab()
        
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="📊 History")
        self.create_history_tab()
        
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        self.create_settings_tab()
    
    def create_daily_tab(self):
        """Create the daily work tab with scrolling support and new notes/logout"""
        main_container = ttk.Frame(self.daily_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux(event):
            canvas.yview_scroll(int(-1*(event.num)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel_linux)
        canvas.bind_all("<Button-5>", on_mousewheel_linux)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def configure_canvas(event):
            canvas.itemconfig(1, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        main_frame = scrollable_frame
        
        # Header with title and logout button
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(header_frame, text="📋 Daily Work Tracker", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # Logout button - appears on the right
        self.logout_btn = ttk.Button(header_frame, text="🚪 Logout", 
                                     command=self.logout, style='Logout.TButton')
        self.logout_btn.pack(side=tk.RIGHT)
        
        # Status and Date
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="⏳ Status: Waiting for check-in", 
                                     style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.date_label = ttk.Label(status_frame, 
                                   text=f"📅 {datetime.datetime.now().strftime('%Y-%m-%d')}", 
                                   style='Status.TLabel')
        self.date_label.pack(side=tk.RIGHT, padx=10)
        
        # Previous session display
        prev_frame = ttk.LabelFrame(main_frame, text="📂 Previous Session", padding="8")
        prev_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.prev_session_label = ttk.Label(prev_frame, text="No previous sessions", 
                                           font=('Arial', 10), foreground='blue')
        self.prev_session_label.pack(anchor=tk.W)
        
        # Two column layout
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        left_column = ttk.Frame(columns_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_column = ttk.Frame(columns_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # LEFT COLUMN: Tasks
        task_frame = ttk.LabelFrame(left_column, text="📝 Today's Tasks", padding="10")
        task_frame.pack(fill=tk.BOTH, expand=True)
        
        task_input_frame = ttk.Frame(task_frame)
        task_input_frame.pack(fill=tk.X, pady=5)
        
        self.task_entry = ttk.Entry(task_input_frame, font=('Arial', 11))
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        ttk.Button(task_input_frame, text="➕ Add Task", 
                  command=self.add_task, style='Action.TButton').pack(side=tk.LEFT)
        
        task_list_frame = ttk.Frame(task_frame)
        task_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.task_listbox = tk.Listbox(task_list_frame, height=6, 
                                      font=('Arial', 11), selectmode=tk.SINGLE)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        task_scrollbar = ttk.Scrollbar(task_list_frame, orient=tk.VERTICAL, 
                                      command=self.task_listbox.yview)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=task_scrollbar.set)
        
        task_btn_frame = ttk.Frame(task_frame)
        task_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(task_btn_frame, text="✅ Complete", 
                  command=self.complete_task, style='Action.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(task_btn_frame, text="❌ Delete", 
                  command=self.delete_task, style='Action.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(task_btn_frame, text="🗑️ Clear All", 
                  command=self.clear_tasks, style='Action.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Label(task_frame, text="✅ Completed:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        
        self.completed_label = ttk.Label(task_frame, text="None", 
                                        font=('Arial', 10), foreground='green')
        self.completed_label.pack(anchor=tk.W, pady=2)
        
        # RIGHT COLUMN: Plan Points
        plan_frame = ttk.LabelFrame(right_column, text="📋 Today's Plan Points", padding="10")
        plan_frame.pack(fill=tk.BOTH, expand=True)
        
        plan_input_frame = ttk.Frame(plan_frame)
        plan_input_frame.pack(fill=tk.X, pady=5)
        
        self.plan_entry = ttk.Entry(plan_input_frame, font=('Arial', 11))
        self.plan_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.plan_entry.bind('<Return>', lambda e: self.add_plan_item())
        
        ttk.Button(plan_input_frame, text="➕ Add Point", 
                  command=self.add_plan_item, style='Action.TButton').pack(side=tk.LEFT)
        
        plan_list_frame = ttk.Frame(plan_frame)
        plan_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.plan_listbox = tk.Listbox(plan_list_frame, height=6, 
                                      font=('Arial', 11), selectmode=tk.SINGLE)
        self.plan_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        plan_scrollbar = ttk.Scrollbar(plan_list_frame, orient=tk.VERTICAL, 
                                      command=self.plan_listbox.yview)
        plan_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.plan_listbox.config(yscrollcommand=plan_scrollbar.set)
        
        plan_btn_frame = ttk.Frame(plan_frame)
        plan_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(plan_btn_frame, text="✅ Complete", 
                  command=self.complete_plan_item, style='Action.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(plan_btn_frame, text="❌ Delete", 
                  command=self.delete_plan_item, style='Action.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(plan_btn_frame, text="🗑️ Clear All", 
                  command=self.clear_plan_items, style='Action.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Label(plan_frame, text="✅ Completed:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        
        self.completed_plan_label = ttk.Label(plan_frame, text="None", 
                                             font=('Arial', 10), foreground='green')
        self.completed_plan_label.pack(anchor=tk.W, pady=2)
        
        # LOGIN AND SUBMIT SECTION
        login_frame = ttk.LabelFrame(main_frame, text="⏰ Login & Check-in", padding="10")
        login_frame.pack(fill=tk.X, pady=5, padx=10)
        
        login_inner = ttk.Frame(login_frame)
        login_inner.pack(fill=tk.X, pady=5)
        
        ttk.Label(login_inner, text="Login Time:", 
                 style='Header.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.login_hour = ttk.Combobox(login_inner, 
                                      values=[str(i).zfill(2) for i in range(24)], 
                                      width=3, state='readonly', font=('Arial', 11))
        self.login_hour.set(datetime.datetime.now().strftime("%H"))
        self.login_hour.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(login_inner, text=":", font=('Arial', 14)).pack(side=tk.LEFT)
        
        self.login_minute = ttk.Combobox(login_inner, 
                                        values=[str(i).zfill(2) for i in range(60)], 
                                        width=3, state='readonly', font=('Arial', 11))
        self.login_minute.set("00")
        self.login_minute.pack(side=tk.LEFT, padx=2)
        
        self.submit_btn = ttk.Button(login_inner, text="🚀 Start Check-in", 
                                    command=self.submit_checkin, style='Action.TButton')
        self.submit_btn.pack(side=tk.RIGHT, padx=10)
        
        # TIMER SECTION
        timer_frame = ttk.LabelFrame(main_frame, text="⏱️ Work Timer (Background)", padding="10")
        timer_frame.pack(fill=tk.X, pady=5, padx=10)
        
        timer_display_frame = ttk.Frame(timer_frame)
        timer_display_frame.pack()
        
        self.timer_label = ttk.Label(timer_display_frame, text="00:00:00", 
                                    style='Timer.TLabel')
        self.timer_label.pack()
        
        self.time_info_label = ttk.Label(timer_frame, text="", font=('Arial', 11))
        self.time_info_label.pack()
        
        timer_controls = ttk.Frame(timer_frame)
        timer_controls.pack(pady=5)
        
        ttk.Button(timer_controls, text="⏸️ Pause/Resume Timer", 
                  command=self.toggle_timer, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(timer_controls, text="🔄 Reset Timer", 
                  command=self.reset_timer, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # ========== NEW: NOTES SECTION ==========
        notes_frame = ttk.LabelFrame(main_frame, text="📝 Notes for Today", padding="10")
        notes_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=4, font=('Arial', 10))
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        # Bind key release to auto-save notes
        self.notes_text.bind('<KeyRelease>', self.save_notes_auto)
        
        # REVIEW SECTION
        review_frame = ttk.LabelFrame(main_frame, text="📊 End of Day Review", padding="10")
        review_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.review_text = scrolledtext.ScrolledText(review_frame, height=8, 
                                                    state=tk.DISABLED, font=('Arial', 10))
        self.review_text.pack(fill=tk.BOTH, expand=True)
        
        # ACTION BUTTONS
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, padx=10)
        
        ttk.Button(button_frame, text="✅ Complete Day", 
                  command=self.mark_all_completed, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Weekly Report", 
                  command=self.generate_weekly_report, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🤖 Auto Review with DeepSeek", 
                  command=self.auto_review_with_deepseek, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save All", 
                  command=self.save_all_data, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # SIGNATURE
        signature_frame = ttk.Frame(main_frame)
        signature_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(signature_frame, text="© 2026 Abdelrhman Hamed - All Rights Reserved", 
                 style='Signature.TLabel').pack(side=tk.RIGHT)
    
    # ========== NOTES AUTO-SAVE ==========
    def save_notes_auto(self, event=None):
        """Auto-save notes to temp data"""
        self.notes = self.notes_text.get("1.0", tk.END).strip()
        self.save_temp_data()
    
    # ========== LOGOUT ==========
    def logout(self):
        """Logout: stop timer, save data, clear UI, reset state"""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?\n\n"
                                "This will stop the timer, save all data, and clear the current session."):
            # Stop timer
            if self.is_tracking:
                self.is_tracking = False
                self.elapsed_seconds = self.get_elapsed_time()
                self.save_timer_state()
            
            # Save all data
            self.save_all_data()
            
            # Clear UI
            self.tasks.clear()
            self.completed_tasks.clear()
            self.plan_items.clear()
            self.completed_plan_items.clear()
            self.notes = ""
            self.login_time = None
            self.start_time = None
            self.elapsed_seconds = 0
            self.current_entry = None
            
            # Update UI components
            self.update_task_list()
            self.update_completed_label()
            self.update_plan_list()
            self.update_completed_plan_label()
            self.notes_text.delete("1.0", tk.END)
            self.timer_label.config(text="00:00:00")
            self.time_info_label.config(text="")
            self.status_label.config(text="🚪 Status: Logged out")
            self.prev_session_label.config(text="Session ended. Start a new day.")
            self.review_text.config(state=tk.NORMAL)
            self.review_text.delete("1.0", tk.END)
            self.review_text.config(state=tk.DISABLED)
            
            # Save empty temp
            self.save_temp_data()
            
            messagebox.showinfo("Logged Out", "You have been logged out.\nAll data has been saved.\nStart fresh tomorrow!")
    
    # ========== TIMER CONTROL METHODS ==========
    def toggle_timer(self):
        if self.is_tracking:
            self.is_tracking = False
            self.elapsed_seconds = self.get_elapsed_time()
            self.save_timer_state()
            self.status_label.config(text="⏸️ Status: Timer Paused")
            messagebox.showinfo("Timer Paused", 
                "⏸️ Timer has been paused.\n\nThe elapsed time has been saved.\nClick 'Pause/Resume Timer' again to continue.")
        else:
            if self.start_time:
                self.start_time = datetime.datetime.now() - datetime.timedelta(seconds=self.elapsed_seconds)
                self.is_tracking = True
                self.save_timer_state()
                self.update_timer()
                self.status_label.config(text="▶️ Status: Timer Resumed")
                messagebox.showinfo("Timer Resumed", 
                    "▶️ Timer has been resumed.\n\nThe timer is now running in the background.")
            else:
                messagebox.showwarning("Warning", "No active timer to resume. Please start check-in first.")
    
    def reset_timer(self):
        if messagebox.askyesno("Confirm Reset", 
            "Are you sure you want to reset the timer?\n\nThis will clear all elapsed time."):
            self.is_tracking = False
            self.elapsed_seconds = 0
            self.start_time = None
            self.timer_label.config(text="00:00:00")
            self.time_info_label.config(text="")
            self.save_timer_state()
            self.status_label.config(text="⏳ Status: Timer Reset")
            messagebox.showinfo("Timer Reset", "✅ Timer has been reset to zero.")
    
    # ========== HISTORY TAB ==========
    def create_history_tab(self):
        """Create the history tab with scrolling support"""
        main_container = ttk.Frame(self.history_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux(event):
            canvas.yview_scroll(int(-1*(event.num)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel_linux)
        canvas.bind_all("<Button-5>", on_mousewheel_linux)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def configure_canvas(event):
            canvas.itemconfig(1, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        history_main = scrollable_frame
        
        title_frame = ttk.Frame(history_main)
        title_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(title_frame, text="📊 Completed Tasks History", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Button(title_frame, text="🔄 Refresh", 
                  command=self.refresh_history, style='Action.TButton').pack(side=tk.RIGHT)
        
        filter_frame = ttk.Frame(history_main)
        filter_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(filter_frame, text="Filter by Date:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)
        
        self.filter_date = ttk.Entry(filter_frame, width=15, font=('Arial', 11))
        self.filter_date.pack(side=tk.LEFT, padx=5)
        self.filter_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(filter_frame, text="🔍 Search", 
                  command=self.filter_history, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="📅 Show All", 
                  command=self.show_all_history, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        self.stats_frame = ttk.LabelFrame(history_main, text="📈 Summary Statistics", padding="10")
        self.stats_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.stats_label = ttk.Label(self.stats_frame, text="Loading statistics...", 
                                     font=('Arial', 11))
        self.stats_label.pack(anchor=tk.W)
        
        history_list_frame = ttk.LabelFrame(history_main, text="📋 Completed Items", padding="10")
        history_list_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        tree_container = ttk.Frame(history_list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Date", "Tasks", "Plan Points", "Hours", "Status")
        self.history_tree = ttk.Treeview(tree_container, columns=columns, 
                                        show="headings", height=12)
        
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Tasks", text="Tasks Completed")
        self.history_tree.heading("Plan Points", text="Plan Points Completed")
        self.history_tree.heading("Hours", text="Hours Worked")
        self.history_tree.heading("Status", text="Status")
        
        self.history_tree.column("Date", width=min(150, int(self.screen_width * 0.12)))
        self.history_tree.column("Tasks", width=min(350, int(self.screen_width * 0.25)))
        self.history_tree.column("Plan Points", width=min(300, int(self.screen_width * 0.22)))
        self.history_tree.column("Hours", width=min(120, int(self.screen_width * 0.08)))
        self.history_tree.column("Status", width=min(120, int(self.screen_width * 0.08)))
        
        tree_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, 
                                      command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        tree_h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, 
                                        command=self.history_tree.xview)
        self.history_tree.configure(xscrollcommand=tree_h_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        detail_frame = ttk.LabelFrame(history_main, text="📝 Details", padding="10")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0), padx=10)
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, height=6, 
                                                    state=tk.DISABLED, font=('Arial', 10))
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        self.history_tree.bind('<<TreeviewSelect>>', self.show_history_details)
        
        sig_frame = ttk.Frame(history_main)
        sig_frame.pack(fill=tk.X, pady=10, padx=10)
        ttk.Label(sig_frame, text="© 2026 Abdelrhman Hamed - All Rights Reserved", 
                 style='Signature.TLabel').pack(side=tk.RIGHT)
        
        self.refresh_history()
    
    # ========== SETTINGS TAB ==========
    def create_settings_tab(self):
        """Create settings/administration tab with scrolling"""
        main_container = ttk.Frame(self.settings_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux(event):
            canvas.yview_scroll(int(-1*(event.num)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel_linux)
        canvas.bind_all("<Button-5>", on_mousewheel_linux)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def configure_canvas(event):
            canvas.itemconfig(1, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        settings_main = scrollable_frame
        
        ttk.Label(settings_main, text="⚙️ Settings & Administration", 
                 style='Title.TLabel').pack(pady=20)
        
        # Data Management Section
        data_frame = ttk.LabelFrame(settings_main, text="📁 Data Management", padding="15")
        data_frame.pack(fill=tk.X, pady=10, padx=20)
        
        backup_frame = ttk.Frame(data_frame)
        backup_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(backup_frame, text="Backup Data:", font=('Arial', 12)).pack(anchor=tk.W)
        ttk.Button(backup_frame, text="📦 Create Backup", 
                  command=self.create_backup, style='Action.TButton').pack(anchor=tk.W, pady=5)
        
        clear_frame = ttk.Frame(data_frame)
        clear_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(clear_frame, text="⚠️ Danger Zone:", 
                 font=('Arial', 12, 'bold'), foreground='red').pack(anchor=tk.W)
        
        ttk.Button(clear_frame, text="🗑️ Clear All Data", 
                  command=self.clear_all_data, style='Danger.TButton').pack(anchor=tk.W, pady=5)
        
        ttk.Label(clear_frame, text="This will delete ALL your data including tasks, history, and reviews.", 
                 font=('Arial', 9), foreground='red').pack(anchor=tk.W)
        
        files_frame = ttk.LabelFrame(settings_main, text="📂 File Locations", padding="15")
        files_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(files_frame, text=f"Data Directory: {self.work_dir}", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(files_frame, text=f"Data File: {self.data_file}", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(files_frame, text=f"Report File: {self.output_file}", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(files_frame, text=f"Backup Directory: {self.backup_dir}", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(files_frame, text=f"Timer State File: {self.timer_file}", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        
        info_frame = ttk.LabelFrame(settings_main, text="ℹ️ About", padding="15")
        info_frame.pack(fill=tk.X, pady=10, padx=20)
        
        about_text = """Daily Work Tracker v2.1
Developed by Abdelrhman Hamed

This application helps you track your daily tasks, plan points, and work hours.
It provides automatic check-in, timer, weekly reports, and DeepSeek integration.

NEW FEATURES:
• Background Timer - Timer continues running even when app is closed
• Timer persists across app restarts
• Pause/Resume timer functionality
• Timer state saved automatically
• Logout button - ends session and clears UI
• Daily Notes box - keep notes for each day

Features:
• To-Do list for tasks and plan points
• Automatic timer (background)
• End of day review
• Weekly reports
• DeepSeek auto-review
• Data backup and restore
• History tracking

© 2026 Abdelrhman Hamed - All Rights Reserved"""
        
        about_label = ttk.Label(info_frame, text=about_text, font=('Arial', 10), 
                               justify=tk.LEFT)
        about_label.pack(anchor=tk.W)
        
        sig_frame = ttk.Frame(settings_main)
        sig_frame.pack(fill=tk.X, pady=20, padx=20)
        ttk.Label(sig_frame, text="© 2026 Abdelrhman Hamed - All Rights Reserved", 
                 style='Signature.TLabel').pack(side=tk.RIGHT)
    
    # ========== REST OF THE METHODS ==========
    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append({"task": task, "completed": False})
            self.update_task_list()
            self.task_entry.delete(0, tk.END)
            self.save_temp_data()
        else:
            messagebox.showwarning("Warning", "Please enter a task")
    
    def complete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.tasks):
                task = self.tasks[index]
                if not task["completed"]:
                    task["completed"] = True
                    self.completed_tasks.append(task["task"])
                    self.update_task_list()
                    self.update_completed_label()
                    self.save_temp_data()
                    messagebox.showinfo("Success", f"✅ Completed: {task['task']}")
                else:
                    messagebox.showinfo("Info", "Task already completed")
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.tasks):
                task = self.tasks.pop(index)
                self.update_task_list()
                self.save_temp_data()
                messagebox.showinfo("Deleted", f"❌ Deleted: {task['task']}")
    
    def clear_tasks(self):
        if self.tasks and messagebox.askyesno("Confirm", "Delete all tasks?"):
            self.tasks.clear()
            self.completed_tasks.clear()
            self.update_task_list()
            self.update_completed_label()
            self.save_temp_data()
    
    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            status = "✅ " if task["completed"] else "⬜ "
            display_text = f"{status}{task['task']}"
            self.task_listbox.insert(tk.END, display_text)
            if task["completed"]:
                self.task_listbox.itemconfig(i, fg='gray')
    
    def update_completed_label(self):
        if self.completed_tasks:
            text = f"({len(self.completed_tasks)}) " + ', '.join(self.completed_tasks[:3])
            if len(self.completed_tasks) > 3:
                text += f" ... +{len(self.completed_tasks)-3} more"
            self.completed_label.config(text=text)
        else:
            self.completed_label.config(text="None")
    
    def add_plan_item(self):
        plan = self.plan_entry.get().strip()
        if plan:
            self.plan_items.append({"item": plan, "completed": False})
            self.update_plan_list()
            self.plan_entry.delete(0, tk.END)
            self.save_temp_data()
        else:
            messagebox.showwarning("Warning", "Please enter a plan point")
    
    def complete_plan_item(self):
        selection = self.plan_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.plan_items):
                item = self.plan_items[index]
                if not item["completed"]:
                    item["completed"] = True
                    self.completed_plan_items.append(item["item"])
                    self.update_plan_list()
                    self.update_completed_plan_label()
                    self.save_temp_data()
                    messagebox.showinfo("Success", f"✅ Completed: {item['item']}")
                else:
                    messagebox.showinfo("Info", "Plan point already completed")
    
    def delete_plan_item(self):
        selection = self.plan_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.plan_items):
                item = self.plan_items.pop(index)
                self.update_plan_list()
                self.save_temp_data()
                messagebox.showinfo("Deleted", f"❌ Deleted: {item['item']}")
    
    def clear_plan_items(self):
        if self.plan_items and messagebox.askyesno("Confirm", "Delete all plan points?"):
            self.plan_items.clear()
            self.completed_plan_items.clear()
            self.update_plan_list()
            self.update_completed_plan_label()
            self.save_temp_data()
    
    def update_plan_list(self):
        self.plan_listbox.delete(0, tk.END)
        for i, item in enumerate(self.plan_items):
            status = "✅ " if item["completed"] else "⬜ "
            display_text = f"{status}{item['item']}"
            self.plan_listbox.insert(tk.END, display_text)
            if item["completed"]:
                self.plan_listbox.itemconfig(i, fg='gray')
    
    def update_completed_plan_label(self):
        if self.completed_plan_items:
            text = f"({len(self.completed_plan_items)}) " + ', '.join(self.completed_plan_items[:3])
            if len(self.completed_plan_items) > 3:
                text += f" ... +{len(self.completed_plan_items)-3} more"
            self.completed_plan_label.config(text=text)
        else:
            self.completed_plan_label.config(text="None")
    
    def load_data(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"entries": []}
        return {"entries": []}
    
    def load_review_data(self):
        if self.review_file.exists():
            try:
                with open(self.review_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"reviews": []}
        return {"reviews": []}
    
    def load_temp_data(self):
        if self.temp_file.exists():
            try:
                with open(self.temp_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def save_review_data(self):
        with open(self.review_file, 'w', encoding='utf-8') as f:
            json.dump(self.review_data, f, indent=2, ensure_ascii=False)
    
    def save_temp_data(self):
        temp = {
            "tasks": self.tasks,
            "completed_tasks": self.completed_tasks,
            "plan_items": self.plan_items,
            "completed_plan_items": self.completed_plan_items,
            "login_time": self.login_time,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "is_tracking": self.is_tracking,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "elapsed_seconds": self.elapsed_seconds,
            "notes": self.notes  # save notes
        }
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            json.dump(temp, f, indent=2, ensure_ascii=False)
        self.save_timer_state()
    
    def save_all_data(self):
        self.save_data()
        self.save_review_data()
        self.save_temp_data()
        self.save_timer_state()
        messagebox.showinfo("Success", "✅ All data saved successfully")
    
    def load_previous_session(self):
        if self.temp_data:
            date = self.temp_data.get("date", "")
            if date == datetime.datetime.now().strftime("%Y-%m-%d"):
                self.tasks = self.temp_data.get("tasks", [])
                self.completed_tasks = self.temp_data.get("completed_tasks", [])
                self.plan_items = self.temp_data.get("plan_items", [])
                self.completed_plan_items = self.temp_data.get("completed_plan_items", [])
                self.login_time = self.temp_data.get("login_time")
                self.elapsed_seconds = self.temp_data.get("elapsed_seconds", 0)
                self.notes = self.temp_data.get("notes", "")
                
                self.update_task_list()
                self.update_completed_label()
                self.update_plan_list()
                self.update_completed_plan_label()
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", self.notes)
                
                if self.is_tracking and self.start_time:
                    self.update_timer()
                    self.status_label.config(text="⏳ Status: Working (background)...")
                else:
                    self.update_timer_display()
                
                if self.tasks or self.plan_items:
                    self.prev_session_label.config(
                        text=f"📂 Restored previous session ({date}) - {len(self.tasks)} tasks, {len(self.plan_items)} plan points"
                    )
            else:
                self.prev_session_label.config(
                    text=f"📂 Last session: {date} - {len(self.temp_data.get('tasks', []))} tasks, {len(self.temp_data.get('plan_items', []))} plan points"
                )
    
    def on_closing(self):
        self.save_all_data()
        self.root.destroy()
    
    def submit_checkin(self):
        if not self.tasks and not self.plan_items:
            if not messagebox.askyesno("Warning", "No tasks or plan points. Continue?"):
                return
        
        login_time = f"{self.login_hour.get()}:{self.login_minute.get()}"
        self.login_time = login_time
        
        # Get notes
        self.notes = self.notes_text.get("1.0", tk.END).strip()
        
        entry = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%H:%M"),
            "tasks": self.tasks.copy(),
            "completed_tasks": self.completed_tasks.copy(),
            "plan_items": self.plan_items.copy(),
            "completed_plan_items": self.completed_plan_items.copy(),
            "login_time": login_time,
            "completed": False,
            "completion_time": None,
            "hours_worked": 0,
            "task_count": len(self.tasks),
            "completed_count": len(self.completed_tasks),
            "plan_count": len(self.plan_items),
            "completed_plan_count": len(self.completed_plan_items),
            "notes": self.notes  # store notes in entry
        }
        
        self.current_entry = entry
        self.data["entries"].append(entry)
        self.save_data()
        self.save_temp_data()
        
        self.start_time = datetime.datetime.now()
        self.elapsed_seconds = 0
        self.is_tracking = True
        self.save_timer_state()
        self.update_timer()
        
        self.status_label.config(text="✅ Status: Working...")
        messagebox.showinfo("Success", 
                           f"✅ Check-in successful!\n"
                           f"{len(self.tasks)} tasks\n"
                           f"{len(self.plan_items)} plan points\n"
                           f"⏱️ Timer started (runs in background)")
    
    def update_timer(self):
        """Update timer continuously"""
        if self.is_tracking and self.start_time:
            now = datetime.datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            self.elapsed_seconds = elapsed
            
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            if self.login_time:
                try:
                    login_h, login_m = map(int, self.login_time.split(':'))
                    login_dt = datetime.datetime(now.year, now.month, now.day, login_h, login_m)
                    worked = (now - login_dt).seconds / 3600
                    self.time_info_label.config(text=f"⏱️ Since login: {worked:.1f} hours")
                except:
                    pass
            
            if int(elapsed) % 10 == 0:
                self.save_timer_state()
            
            self.root.after(1000, self.update_timer)
        else:
            self.update_timer_display()
    
    def mark_all_completed(self):
        if not self.data["entries"]:
            messagebox.showinfo("Info", "No sessions to complete")
            return
        
        latest = self.data["entries"][-1]
        if latest["completed"]:
            messagebox.showinfo("Info", "Day already completed")
            return
        
        incomplete_tasks = [t for t in latest["tasks"] if not t["completed"]]
        incomplete_plan = [p for p in latest["plan_items"] if not p["completed"]]
        
        if incomplete_tasks or incomplete_plan:
            msg = f"⚠️ Incomplete items:\n"
            if incomplete_tasks:
                msg += f"  - {len(incomplete_tasks)} incomplete tasks\n"
            if incomplete_plan:
                msg += f"  - {len(incomplete_plan)} incomplete plan points\n"
            msg += "\nComplete and finish day?"
            
            if not messagebox.askyesno("Incomplete Items", msg):
                return
            
            for task in latest["tasks"]:
                if not task["completed"]:
                    task["completed"] = True
                    if task["task"] not in self.completed_tasks:
                        self.completed_tasks.append(task["task"])
            
            for item in latest["plan_items"]:
                if not item["completed"]:
                    item["completed"] = True
                    if item["item"] not in self.completed_plan_items:
                        self.completed_plan_items.append(item["item"])
        
        try:
            login_h, login_m = map(int, latest["login_time"].split(':'))
            now = datetime.datetime.now()
            login_dt = datetime.datetime(now.year, now.month, now.day, login_h, login_m)
            worked = (now - login_dt).seconds / 3600
            
            latest["completed"] = True
            latest["completion_time"] = now.strftime("%H:%M")
            latest["hours_worked"] = round(worked, 2)
            latest["completed_count"] = len([t for t in latest["tasks"] if t["completed"]])
            latest["completed_plan_count"] = len([p for p in latest["plan_items"] if p["completed"]])
            # Store final notes
            latest["notes"] = self.notes_text.get("1.0", tk.END).strip()
            self.save_data()
            
            self.is_tracking = False
            self.save_timer_state()
            self.timer_label.config(text="✅ Day Complete!")
            self.status_label.config(text="✅ Status: Day completed")
            
            self.show_review(latest)
            self.refresh_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error completing: {e}")
    
    def show_review(self, entry):
        self.review_text.config(state=tk.NORMAL)
        self.review_text.delete("1.0", tk.END)
        
        task_list = '\n'.join(f"  {i+1}. {'✅ ' if t['completed'] else '⬜ '}{t['task']}" 
                             for i, t in enumerate(entry['tasks']))
        
        plan_list = '\n'.join(f"  {i+1}. {'✅ ' if p['completed'] else '⬜ '}{p['item']}" 
                             for i, p in enumerate(entry['plan_items']))
        
        notes_display = entry.get('notes', 'No notes for this day.')
        
        review = f"""╔══════════════════════════════════════════╗
║         END OF DAY REVIEW              ║
╚══════════════════════════════════════════╝

📅 Date: {entry['date']}
🕐 Login Time: {entry['login_time']}
✅ Completion Time: {entry['completion_time']}
⏱️ Hours Worked: {entry['hours_worked']:.1f} hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TASKS:
Total Tasks: {entry['task_count']}
Completed: {entry['completed_count']}
Progress: {int(entry['completed_count']/entry['task_count']*100) if entry['task_count'] > 0 else 0}%

{task_list if task_list else '  (No tasks)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 PLAN POINTS:
Total Plan Points: {entry['plan_count']}
Completed: {entry['completed_plan_count']}
Progress: {int(entry['completed_plan_count']/entry['plan_count']*100) if entry['plan_count'] > 0 else 0}%

{plan_list if plan_list else '  (No plan points)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 NOTES:
{notes_display}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 REVIEW QUESTIONS:
1. Did you complete all planned tasks?
   Answer: ________________________________

2. What challenges did you face?
   Answer: ________________________________

3. What will you do differently tomorrow?
   Answer: ________________________________

4. Are you satisfied with today's work?
   Answer: ________________________________
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

© 2026 Abdelrhman Hamed - All Rights Reserved"""
        
        self.review_text.insert("1.0", review)
        self.review_text.config(state=tk.DISABLED)
        
        self.review_data["reviews"].append({
            "date": entry['date'],
            "entry": entry,
            "review_answers": ""
        })
        self.save_review_data()
    
    def generate_weekly_report(self):
        today = datetime.datetime.now()
        week_ago = today - datetime.timedelta(days=7)
        
        weekly_entries = [
            e for e in self.data["entries"] 
            if datetime.datetime.strptime(e['date'], "%Y-%m-%d") >= week_ago
        ]
        
        if not weekly_entries:
            messagebox.showinfo("Info", "No data for this week")
            return
        
        report = f"""╔══════════════════════════════════════════╗
║         WEEKLY REPORT                  ║
╚══════════════════════════════════════════╝

Generated: {today.strftime('%Y-%m-%d %H:%M')}
Week: {week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}

📊 SUMMARY:
- Total Days Worked: {len(weekly_entries)}
- Total Hours: {sum(e.get('hours_worked', 0) for e in weekly_entries):.1f} hours
- Total Tasks: {sum(e.get('task_count', 0) for e in weekly_entries)}
- Completed Tasks: {sum(e.get('completed_count', 0) for e in weekly_entries)}
- Total Plan Points: {sum(e.get('plan_count', 0) for e in weekly_entries)}
- Completed Plan Points: {sum(e.get('completed_plan_count', 0) for e in weekly_entries)}

📈 DAILY BREAKDOWN:
{chr(10).join('─'*50)}
{chr(10).join(self.format_entry(e) for e in weekly_entries)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
© 2026 Abdelrhman Hamed - All Rights Reserved"""
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.review_text.config(state=tk.NORMAL)
        self.review_text.delete("1.0", tk.END)
        self.review_text.insert("1.0", report)
        self.review_text.config(state=tk.DISABLED)
        
        messagebox.showinfo("Success", f"✅ Report saved to:\n{self.output_file}")
    
    def format_entry(self, entry):
        return f"""📅 {entry['date']}
   Login: {entry['login_time']}
   Hours: {entry.get('hours_worked', 0):.1f}h
   Tasks: {entry.get('completed_count', 0)}/{entry.get('task_count', 0)}
   Plan: {entry.get('completed_plan_count', 0)}/{entry.get('plan_count', 0)}
"""
    
    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        entries = self.data.get("entries", [])
        
        if not entries:
            self.history_tree.insert("", tk.END, values=("No data", "", "", "", ""))
            self.update_statistics([])
            return
        
        for entry in reversed(entries):
            if entry.get("completed", False):
                tasks = entry.get("completed_tasks", [])
                plan_items = entry.get("completed_plan_items", [])
                hours = entry.get("hours_worked", 0)
                date = entry.get("date", "Unknown")
                status = "✅ Completed" if entry.get("completed") else "⏳ In Progress"
                
                tasks_str = ", ".join(tasks[:3])
                if len(tasks) > 3:
                    tasks_str += f" ... +{len(tasks)-3} more"
                
                plan_str = ", ".join(plan_items[:3])
                if len(plan_items) > 3:
                    plan_str += f" ... +{len(plan_items)-3} more"
                
                self.history_tree.insert("", tk.END, 
                                        values=(date, tasks_str, plan_str, f"{hours:.1f}h", status))
        
        self.update_statistics(entries)
    
    def update_statistics(self, entries):
        completed_entries = [e for e in entries if e.get("completed", False)]
        
        if not completed_entries:
            self.stats_label.config(text="📊 No completed entries found.")
            return
        
        total_days = len(completed_entries)
        total_hours = sum(e.get("hours_worked", 0) for e in completed_entries)
        total_tasks = sum(len(e.get("completed_tasks", [])) for e in completed_entries)
        total_plan = sum(len(e.get("completed_plan_items", [])) for e in completed_entries)
        
        avg_hours = total_hours / total_days if total_days > 0 else 0
        
        stats_text = f"""📊 Statistics:
• Total Days Completed: {total_days}
• Total Hours Worked: {total_hours:.1f} hours
• Average Hours/Day: {avg_hours:.1f} hours
• Total Tasks Completed: {total_tasks}
• Total Plan Points Completed: {total_plan}
• Overall Productivity: {int((total_tasks + total_plan) / (total_days * 2) * 100) if total_days > 0 else 0}%
• Developed by: Abdelrhman Hamed"""
        
        self.stats_label.config(text=stats_text)
    
    def filter_history(self):
        filter_date = self.filter_date.get().strip()
        
        if not filter_date:
            messagebox.showwarning("Warning", "Please enter a date (YYYY-MM-DD)")
            return
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        entries = self.data.get("entries", [])
        filtered = [e for e in entries if e.get("date") == filter_date]
        
        if not filtered:
            self.history_tree.insert("", tk.END, values=(f"No entries for {filter_date}", "", "", "", ""))
            return
        
        for entry in filtered:
            tasks = entry.get("completed_tasks", [])
            plan_items = entry.get("completed_plan_items", [])
            hours = entry.get("hours_worked", 0)
            date = entry.get("date", "Unknown")
            status = "✅ Completed" if entry.get("completed") else "⏳ In Progress"
            
            tasks_str = ", ".join(tasks[:3])
            if len(tasks) > 3:
                tasks_str += f" ... +{len(tasks)-3} more"
            
            plan_str = ", ".join(plan_items[:3])
            if len(plan_items) > 3:
                plan_str += f" ... +{len(plan_items)-3} more"
            
            self.history_tree.insert("", tk.END, 
                                    values=(date, tasks_str, plan_str, f"{hours:.1f}h", status))
    
    def show_all_history(self):
        self.filter_date.delete(0, tk.END)
        self.filter_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.refresh_history()
    
    def show_history_details(self, event):
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = self.history_tree.item(selection[0])
        values = item['values']
        
        if not values or values[0] == "No data":
            return
        
        date = values[0]
        
        entries = self.data.get("entries", [])
        entry = next((e for e in entries if e.get("date") == date), None)
        
        if not entry:
            return
        
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        
        tasks = entry.get("tasks", [])
        completed_tasks = entry.get("completed_tasks", [])
        plan_items = entry.get("plan_items", [])
        completed_plan = entry.get("completed_plan_items", [])
        notes = entry.get("notes", "No notes for this day.")
        
        detail = f"""╔══════════════════════════════════════════╗
║         DETAILED VIEW                  ║
╚══════════════════════════════════════════╝

📅 Date: {entry.get('date', 'Unknown')}
🕐 Login Time: {entry.get('login_time', 'N/A')}
✅ Completion Time: {entry.get('completion_time', 'N/A')}
⏱️ Hours Worked: {entry.get('hours_worked', 0):.1f} hours
📊 Status: {'✅ Completed' if entry.get('completed') else '⏳ In Progress'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ALL TASKS:
{chr(10).join(f'  {i+1}. {"✅ " if t["completed"] else "⬜ "}{t["task"]}' for i, t in enumerate(tasks)) if tasks else '  (No tasks)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 COMPLETED TASKS ({len(completed_tasks)}):
{chr(10).join(f'  ✅ {t}' for t in completed_tasks) if completed_tasks else '  (None)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 PLAN POINTS:
{chr(10).join(f'  {i+1}. {"✅ " if p["completed"] else "⬜ "}{p["item"]}' for i, p in enumerate(plan_items)) if plan_items else '  (No plan points)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 COMPLETED PLAN POINTS ({len(completed_plan)}):
{chr(10).join(f'  ✅ {p}' for p in completed_plan) if completed_plan else '  (None)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 NOTES:
{notes}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 SUMMARY:
• Total Tasks: {len(tasks)}
• Completed Tasks: {len(completed_tasks)}
• Task Completion Rate: {int(len(completed_tasks)/len(tasks)*100) if tasks else 0}%

• Total Plan Points: {len(plan_items)}
• Completed Plan Points: {len(completed_plan)}
• Plan Completion Rate: {int(len(completed_plan)/len(plan_items)*100) if plan_items else 0}%

• Overall Productivity: {int((len(completed_tasks) + len(completed_plan)) / ((len(tasks) + len(plan_items)) / 2) * 100) if (tasks or plan_items) else 0}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
© 2026 Abdelrhman Hamed - All Rights Reserved"""
        
        self.detail_text.insert("1.0", detail)
        self.detail_text.config(state=tk.DISABLED)
    
    def auto_review_with_deepseek(self):
        if not self.output_file.exists():
            messagebox.showwarning("Warning", 
                "Please generate weekly report first (Click 'Weekly Report' button)")
            return
        
        webbrowser.open("https://chat.deepseek.com/")
        
        prompt = """I am going to upload a file containing everything I have completed so far regarding [Project Name/Goal]. Please do not critique the past work. Instead, act as a project manager. Based solely on the state of the work I provide, identify the single most critical next action I should take. I need:

1. The name of the action.
2. A brief reason why this is the priority.
3. A list of specific materials/files I need to have ready before starting that action.

I will now upload the file."""
        
        try:
            import pyperclip
            pyperclip.copy(prompt)
            copied = True
        except:
            copied = False
        
        messagebox.showinfo("✅ Ready!", 
            "DeepSeek is open and the prompt is copied!\n\n"
            "📌 Next Steps:\n"
            "1. Click the paperclip 📎 or '+' button\n"
            f"2. Upload: {self.output_file}\n"
            "3. Click in the chat box and press Ctrl+V\n"
            "4. Press Enter to send\n\n"
            "It's that simple!")
    
    def create_backup(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = self.backup_dir / f"backup_{timestamp}"
            backup_folder.mkdir()
            
            for file in [self.data_file, self.review_file, self.output_file, self.temp_file, self.timer_file]:
                if file.exists():
                    shutil.copy2(file, backup_folder / file.name)
            
            messagebox.showinfo("✅ Success!", 
                f"Backup created successfully!\n\n"
                f"Location: {backup_folder}\n"
                f"Files backed up: {len(list(backup_folder.glob('*')))}")
            
            os.startfile(str(backup_folder))
            
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {e}")
    
    def clear_all_data(self):
        if not messagebox.askyesno("⚠️ DANGER!", 
            "This will DELETE ALL data including:\n"
            "• All daily entries\n"
            "• All tasks and plan points\n"
            "• All history\n"
            "• All reviews\n"
            "• Timer state\n\n"
            "This action CANNOT be undone!\n\n"
            "Do you want to continue?"):
            return
        
        if not messagebox.askyesno("⚠️ FINAL WARNING!", 
            "Are you ABSOLUTELY sure?\n\n"
            "All your work data will be permanently deleted.\n"
            "Make sure you have a backup if needed."):
            return
        
        try:
            self.data = {"entries": []}
            self.review_data = {"reviews": []}
            self.tasks = []
            self.completed_tasks = []
            self.plan_items = []
            self.completed_plan_items = []
            self.notes = ""
            self.is_tracking = False
            self.elapsed_seconds = 0
            self.start_time = None
            
            for file in [self.data_file, self.review_file, self.temp_file, self.timer_file]:
                if file.exists():
                    file.unlink()
            
            self.save_data()
            self.save_review_data()
            self.save_temp_data()
            self.save_timer_state()
            
            self.update_task_list()
            self.update_completed_label()
            self.update_plan_list()
            self.update_completed_plan_label()
            self.notes_text.delete("1.0", tk.END)
            self.refresh_history()
            self.review_text.config(state=tk.NORMAL)
            self.review_text.delete("1.0", tk.END)
            self.review_text.config(state=tk.DISABLED)
            self.timer_label.config(text="00:00:00")
            self.time_info_label.config(text="")
            self.status_label.config(text="⏳ Status: Data cleared")
            self.prev_session_label.config(text="No previous sessions")
            
            messagebox.showinfo("✅ Done!", "All data has been cleared successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear data: {e}")
    
    def check_auto_start(self):
        now = datetime.datetime.now()
        if now.hour == 10 and now.minute == 0:
            self.status_label.config(text="⏰ Status: Auto-started at 10 AM")
            self.root.deiconify()
            self.root.lift()
        elif now.hour < 11:
            self.status_label.config(text="⏰ Status: Auto-started (before 11 AM)")
            self.root.deiconify()
            self.root.lift()
    
    def check_end_of_day(self):
        now = datetime.datetime.now()
        if now.hour == 17 and now.minute == 30:
            if self.data["entries"] and not self.data["entries"][-1]["completed"]:
                self.mark_all_completed()
        self.root.after(60000, self.check_end_of_day)
    
    def check_thursday_review(self):
        now = datetime.datetime.now()
        if now.weekday() == 3 and now.hour == 17 and now.minute == 30:
            self.generate_weekly_report()
            self.auto_review_with_deepseek()
        self.root.after(60000, self.check_thursday_review)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkTrackerApp(root)
    root.mainloop()