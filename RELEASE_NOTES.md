# Release Notes

## v1.2.0 - Reliability, UX & Robustness Update (July 2026)

### 🐛 Bug Fixes
- **Timezone consistency**: All API date queries now use UTC properly
- **Summary cache key**: HTML reviewer uses ISO dates (YYYY-MM-DD) instead of localized format
- **API timeouts**: 30-second timeout on all requests prevents infinite hangs
- **HTTP 204 handling**: DELETE/PATCH operations no longer show as errors
- **Atomic config writes**: Crash-safe saves using temp file + rename
- **Corrupt config recovery**: Automatically renames bad config to `.corrupt.json`
- **Multi-click guard**: Prevents duplicate AI summary generation
- **Duplicate prevention**: Case-insensitive check prevents creating duplicate projects/tags

### ⚡ Performance
- **Recent project cache**: 5-minute cache for recent project IDs reduces API calls
- **API retry**: Automatic single retry on transient network timeouts

### ✨ UX Improvements
- **Fuzzy search**: Type partial names instead of numbers for project/tag selection
- **Recent projects**: Most-used projects shown at top of selection list
- **CLI aliases**: Quick shortcuts (`st`=start, `sp`=stop, `rt`=resume, `ct`=current, `te`=today, `ws`=weekly, `se`=search)
- **Server detection**: Python checked before http-server in .bat launchers
- **Clear Cache button**: One-click reset of all cached data in HTML reviewer

### 🔧 Code Quality
- **Unicode support**: `ensure_ascii=False` preserves non-ASCII names in config
- **Config versioning**: Version field added for future migrations
- **Consistent UTC**: Log timestamps match API timestamps

---

## v1.1.2 - Settings & Performance Update (January 2026)

### ⚙️ Enhanced Toggl Settings
Manage your account with a dedicated settings menu (Option `S`).
- **Organization Management**: View all organizations and workspace counts.
- **Client & Task Support**: Deep dive into your data without leaving the CLI.
- **UserProfile Updates**: Real-time updates for your email, name, and regional settings.

### ⚡ Smart Caching 2.0
Significant performance boost through persistent local storage.
- **70% API Reduction**: Minimizes network latency and preserves your Toggl rate limits.
- **Granular Refresh**: Manually refresh specific data points (clients, tasks, tags) via the submenu.
- **Subtle UI Symbols**: Visual indicators (📡, ⚡, 🔄) keep you informed about data origin.

### 📊 Quota & Safety
- **Real-Time Monitoring**: New `Check API Quota` feature shows your exact rate limit status.
- **Critical Alerts**: Automatic warnings when your remaining API quota drops below 5.

---

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
