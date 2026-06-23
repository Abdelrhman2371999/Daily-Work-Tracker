# 📋 Daily Work Tracker

## 🚀 By Abdelrhman Hamed

---

## 📖 Overview

A powerful desktop app to track daily tasks, plan points, work hours, and get AI-powered reviews. **Boost your productivity!**

### ✨ Features

| Feature | Description |
|---------|-------------|
| ✅ **Tasks** | Create, complete, and track daily tasks |
| 📝 **Plan Points** | Organize your daily plan points |
| ⏱️ **Timer** | Auto-tracks work hours |
| 📊 **Reviews** | End-of-day reflection & weekly reports |
| 📂 **History** | View all past days with stats |
| 🤖 **DeepSeek** | Auto-AI review for next actions |
| 💾 **Backup** | One-click data backup |
| 🖥️ **Full Screen** | Responsive design with mouse scroll |

---

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.7+
- **RAM**: 2GB+ (4GB recommended)
- **Storage**: 50MB+

### Required Packages
```bash
# Core (already in Python)
tkinter, json, datetime, pathlib, shutil, webbrowser, os

# Optional but recommended
pyperclip  # For DeepSeek clipboard
```

---

## 🚀 Quick Installation

### Step 1: Install Python
```bash
# Windows - Download from python.org
# Linux
sudo apt install python3 python3-pip
# macOS
brew install python3
```

### Step 2: Create Directory
```bash
mkdir "D:\Python Automation\WorkTracker"
cd "D:\Python Automation\WorkTracker"
```

### Step 3: Install Package
```bash
pip install pyperclip
```

### Step 4: Create App File
Create `work_tracker.py` and paste the code from the main application.

### Step 5: Run
```bash
python work_tracker.py
```

---

## 📁 File Structure
```
D:\Python Automation\WorkTracker\
├── work_tracker.py      # Main app
├── work_data.json       # Daily data
├── review_data.json     # Reviews
├── weekly_report.txt    # Weekly reports
├── temp_data.json       # Session data
└── backups\             # Backups folder
```

---

## 📖 How To Use

### 🌅 Morning (Check-in)
1. App opens automatically at **10 AM** (or before 11 AM)
2. Add **Tasks** (left column)
3. Add **Plan Points** (right column)
4. Set **Login Time**
5. Click **"Start Check-in"**

### 📈 During The Day
- Click **"Complete"** on finished tasks
- Timer tracks your hours
- All data auto-saves

### 🌇 Evening (5:30 PM)
- Click **"Complete Day"**
- Review your progress
- Answer reflection questions

### 📊 Weekly (Thursday 5:30 PM)
- Click **"Weekly Report"**
- Click **"Auto Review with DeepSeek"**
- Upload report & paste prompt
- Get AI-powered action plan

### 📂 History
- View all completed days
- Click any day for details
- Filter by date
- See productivity stats

### ⚙️ Settings
- **Create Backup** - One-click backup
- **Clear All Data** - Delete everything (with confirmation)
- **File Locations** - See where data is stored
- **About** - App info

---

## ⌨️ Shortcuts

| Action | Shortcut |
|--------|----------|
| Add Task | `Enter` in task input |
| Add Plan Point | `Enter` in plan input |
| Switch Tabs | `Ctrl+Tab` |
| Scroll | Mouse wheel |

---

## 🔧 Customization

### Change Data Directory
```python
# In __init__ method
self.work_dir = Path("D:/Python Automation/WorkTracker")  # Change path
```

### Change Auto-Start Times
```python
def check_auto_start(self):
    if now.hour == 10 and now.minute == 0:  # Change hours

def check_end_of_day(self):
    if now.hour == 17 and now.minute == 30:  # Change to your time

def check_thursday_review(self):
    if now.weekday() == 3:  # 0=Monday, 6=Sunday
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Module not found** | `pip install pyperclip` |
| **Python not recognized** | Reinstall Python → Check ✅ "Add to PATH" |
| **Not full screen** | Check `root.state('zoomed')` |
| **DeepSeek not opening** | Check default browser |
| **Data not saving** | Run as administrator |

---

## 🎯 Tips

1. **Add tasks immediately** - Don't wait
2. **Complete tasks promptly** - Mark done when finished
3. **Use plan points** - Break down big goals
4. **Review daily** - 5 minutes at end of day
5. **Backup weekly** - Use backup feature
6. **Use DeepSeek** - Get AI-powered insights

---

## 🔒 Privacy

- ✅ **All data is local** - No external servers
- ✅ **No internet required** - Except DeepSeek
- ✅ **JSON storage** - Human-readable, easy backup
- ✅ **No tracking** - No analytics

---

## 📞 Contact

<div class="contact-item"><i class="fas fa-envelope"></i><a href="mailto:abdelrhmanhamedmousaa@gmail.com">abdelrhmanhamedmousaa@gmail.com</a></div>
<div class="contact-item"><i class="fab fa-linkedin"></i><a href="https://linkedin.com/in/abdelrhmanhamed" target="_blank">linkedin.com/in/abdelrhmanhamed</a></div>
<div class="contact-item"><i class="fab fa-github"></i><a href="https://github.com/Abdelrhman2371999" target="_blank">github.com/Abdelrhman2371999</a></div>

---

## 📝 License

© 2026 **Abdelrhman Hamed** - All Rights Reserved

---

## ✅ Installation Checklist

- [ ] Install Python 3.7+
- [ ] Create `WorkTracker` folder
- [ ] Run `pip install pyperclip`
- [ ] Create `work_tracker.py` file
- [ ] Paste code into file
- [ ] Test run application
- [ ] Create desktop shortcut
- [ ] Setup auto-start (optional)

---

## 📊 Quick Commands

```bash
# Run app
cd "D:\Python Automation\WorkTracker"
python work_tracker.py

# Install dependencies
pip install pyperclip

# Create backup (in app)
Settings → Create Backup

# Clear data (in app)
Settings → Clear All Data
```

---

**🚀 Start tracking your productivity today!**

**© 2026 Abdelrhman Hamed - All Rights Reserved**
