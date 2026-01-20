# Release Notes

## v1.1.0 - AI Reviewer Update (January 2026)

### 🤖 AI-Powered Log Reviewer

Analyze your productivity with the new AI Reviewer web interface.

- **Offline-First Web UI**: View your local `toggl_cli_logs.txt` with a beautiful calendar interface.
- **AI Token Integration**: Use Google Gemini to generate daily summaries of your work.
- **Smart Grouping**: View entries by Year, Month, and Date.
- **Dedicated Launcher**: New menu in `toggl_cli.bat` to launch the reviewer on Port 8086.

---

## v1.0.0 - Initial Release (January 2026)

### 🎉 First Public Release

A keyboard-first CLI for Toggl time tracking, designed for developers and power users who prefer staying in the terminal.

---

### ✨ Features

**Core Timer Operations**
- Start timer with description, project, and tags
- Stop running timer with duration display
- Resume last timer with one keystroke
- View current timer status

**On-the-fly Creation** ⭐ NEW
- Press `P` to create new project while starting timer
- Press `T` to create new tag while starting timer
- Works in both timer start and entry editing
- Supports mixed input (e.g., `1,T,3`)

**Reports & Analytics**
- Today's entries with total time
- Weekly summary by project, tag, and day
- Search entries by description, project, tag, or date
- Billable time tracking

**Entry Management**
- Edit description, project, tags, billable status
- Delete entries with confirmation
- Create new projects and tags

**Smart Caching**
- Projects and tags cached locally for speed
- Minimal API calls to respect rate limits
- Cache refresh via Options 11/12

**Logging**
- All actions logged to `toggl_cli_logs.txt`
- Timestamped entries for audit trail
- Session separators for clarity

---

### 📁 Files Included

| File | Purpose |
|------|---------|
| `toggl_cli.py` | Main application |
| `toggl_cli.bat` | Windows launcher |
| `README.md` | User guide |
| `CODE_DOCUMENTATION.md` | Technical docs |
| `DESIGN_PHILOSOPHY.md` | Project rationale |
| `CONTRIBUTING.md` | Contribution guide |

---

### 🔧 Requirements

- Python 3.6+
- `requests` library
- Toggl account (free or paid)

---

### 🚀 Quick Start

```bash
pip install requests
python toggl_cli.py
```

Press `1` to login, `2` to start tracking!
