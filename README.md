# Toggl Time Tracker CLI

> **Track time without leaving your terminal.** A keyboard-first CLI for developers who live in the command line.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [Quick Start Guide](#quick-start-guide)
- [Complete Feature Guide](#complete-feature-guide)
- [Log File](#log-file)
- [Tips & Tricks](#tips--tricks)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)

---

## ✨ Features

- ✅ Start/Stop timers with descriptions
- ✅ Track time to projects and tags
- ✅ Resume last timer with one click
- ✅ Edit existing time entries
- ✅ Delete unwanted entries
- ✅ View today's entries
- ✅ Weekly summary with breakdowns
- ✅ Search entries by multiple criteria
- ✅ Billable time tracking
- ✅ **On-the-fly creation** - Press P/T to create projects/tags while starting timer
- ✅ Auto-logging to `toggl_cli_logs.txt`
- ✅ Simple number-based menu (no typing long commands!)

---

## 💻 Requirements

- **Python 3.6 or higher**
- **Internet connection** (to sync with Toggl)
- **Toggl account** (free or paid)

---

## 📥 Installation

### Option A: Clone with Git (Recommended)

```bash
# Clone the repository
git clone https://github.com/krishnakanthb13/toggl-cli.git
cd toggl-cli

# Install dependency
pip install requests

# Run the CLI
python toggl_cli.py
```

### Option B: Download ZIP

1. Click the green **"Code"** button above
2. Select **"Download ZIP"**
3. Extract to your preferred location
4. Open terminal in that folder
5. Run `pip install requests`
6. Run `python toggl_cli.py`

### Requirements

- **Python 3.6 or higher** - [Download here](https://www.python.org/downloads/)
- **requests library** - Installed via `pip install requests`
- **Toggl account** - [Sign up free](https://toggl.com/)

---

## 📁 Project Files

The Toggl CLI consists of the following files:

### Core Files

| File | Description |
|------|-------------|
| `toggl_cli.py` | Main Python application |
| `toggl_cli.bat` | Windows launcher |
| `toggl_config.json` | Auto-created; stores API token and cache |
| `toggl_cli_logs.txt` | Auto-created; timestamped activity log |

### Documentation

| File | Purpose |
|------|--------|
| `README.md` | User guide (this file) |
| `CODE_DOCUMENTATION.md` | Technical documentation |
| `DESIGN_PHILOSOPHY.md` | Project rationale |
| `CONTRIBUTING.md` | Contribution guidelines |
| `RELEASE_NOTES.md` | Version history |

---

## 🚀 First-Time Setup

### Step 1: Get Your Toggl API Token

1. Go to https://track.toggl.com/profile
2. Scroll down to the **"API Token"** section
3. Click to reveal your token
4. Copy it (it looks like: `1a2b3c4d5e6f7g8h9i0j`)

### Step 2: Run the CLI

**Windows:**
```batch
cd C:\Toggl
toggl_cli.bat
```

**Mac/Linux:**
```bash
cd ~/toggl
python3 toggl_cli.py
```

### Step 3: Initial Login

1. You'll see the main menu
2. Press `1` and hit Enter
3. Paste your API token when prompted
4. Select your workspace from the numbered list
5. Done! Your settings are saved to `toggl_config.json`

**Example:**
```
=== TOGGL LOGIN ===
Enter your Toggl API token: 1a2b3c4d5e6f7g8h9i0j
✓ Welcome, John Doe!

=== SELECT WORKSPACE ===
1. Personal Workspace
2. Work Projects
3. Freelance Clients

Select workspace number: 1
✓ Selected workspace: Personal Workspace
✓ Configuration saved to toggl_config.json
```

---

## 🎯 Quick Start Guide

### Your First Timer

1. Run `toggl.bat`
2. Press `2` (Start Timer)
3. Enter description: `Working on website`
4. Track to a project? Press `n` for now
5. Add tags? Press `n` for now
6. Timer starts! ✓

Work for a while...

7. Press `3` (Stop Timer)
8. Done! You've tracked your first time entry.

### View Your Work

Press `6` to see today's entries:
```
=== TODAY'S ENTRIES ===
• Working on website (45 min)
• Team meeting (30 min)

Total today: 1h 15m
```

---

## 📖 Complete Feature Guide

### Menu Overview

```
============================================================
⏱  TOGGL TIME TRACKER
============================================================
  ⚡ ACTIONS                 │  📊 REPORTS & MANAGEMENT
─────────────────────────────┼──────────────────────────────
  1. Login / Setup           │     6. Today's Entries
  2. Start Timer             │     7. Weekly Summary
  3. Stop Timer              │     8. Search Entries
  4. Resume Last Timer       │     9. Edit Entry
  5. Current Timer           │    10. Delete Entry
                             │    11. List Projects
  📁 CREATE                  │    12. List Tags
─────────────────────────────┼──────────────────────────────
 13. Create Project          │  O. Open Reports (Web)
 14. Create Tag              │  0. Exit
============================================================
```

---

## 📝 Feature Details

### 1. Login / Setup

**When to use:** First time, or to switch workspaces

**Steps:**
1. Press `1`
2. Enter API token (first time only)
3. Select workspace

**Tips:**
- Your token is saved securely in `toggl_config.json`
- You only need to login once
- Use this to switch between workspaces

---

### 2. Start Timer

**When to use:** Beginning any task

**Steps:**
1. Press `2`
2. Enter task description (e.g., "Client meeting")
3. Choose project (optional):
   - Press `y` to select from list
   - Enter a number to select existing project
   - Enter `P` to create a new project on-the-fly
   - Press `n` to skip
4. Choose tags (optional):
   - Press `y` to add tags
   - Enter numbers separated by commas (e.g., `1,3,5`)
   - Enter `T` to create a new tag (can mix with numbers: `1,T,3`)
   - Press `n` to skip

**Example Session:**
```
=== START TIMER ===
Enter task description: Writing project proposal
Track to a project? (y/n): y

=== YOUR PROJECTS ===
1. Client A - Website [✓]
2. Client B - App [✓]
P. Create New Project

Select project (number or P): P
New project name: Client C - Redesign
✓ Project created: Client C - Redesign

Add tags? (y/n): y

=== YOUR TAGS ===
1. urgent
2. meeting
3. development
T. Create New Tag

Enter tags (numbers, T for new, comma-separated): 1,T,3
New tag name: documentation
✓ Tag created: documentation
✓ Timer started: Writing project proposal → Client C - Redesign [tags: 3]
```

**Tips:**
- Use clear, searchable descriptions
- Projects help organize work by client/category
- Tags add extra categorization (urgent, meeting, etc.)
- Use `P` and `T` to create items without leaving the timer flow

---

### 3. Stop Timer

**When to use:** Finishing a task

**Steps:**
1. Press `3`
2. Automatic! Timer stops and shows duration

**Example:**
```
✓ Timer stopped: Writing project proposal (47 min)
```

**Tips:**
- Always stop before starting a new timer
- Duration is automatically calculated
- If no timer is running, you'll get a friendly message

---

### 4. Resume Last Timer

**When to use:** Returning to the same task after a break

**Steps:**
1. Press `4`
2. Done! Last timer resumes automatically

**What gets copied:**
- Description
- Project
- Tags
- Billable status

**Example:**
```
✓ Resumed: Writing project proposal → Client A - Website
```

**Perfect for:**
- After lunch breaks
- After meetings
- Switching back to main task
- Interrupted work sessions

**Pro Tip:** This is the fastest way to continue work!

---

### 5. Current Timer

**When to use:** Check what's running and for how long

**Steps:**
1. Press `5`
2. See current timer details

**Example:**
```
⏱ CURRENT TIMER
Task: Writing project proposal
Project: Client A - Website
Duration: 23m 45s
```

**Tips:**
- Use this to verify you're tracking the right thing
- Duration updates in real-time
- If nothing is running, you'll see a message

---

### 6. Today's Entries

**When to use:** Quick daily summary

**Steps:**
1. Press `6`
2. View all entries from today

**Example:**
```
=== TODAY'S ENTRIES ===
• Morning standup → Team Project (15 min)
• Email responses (30 min)
• Writing project proposal → Client A - Website (47 min)
• Code review → Development (25 min)

Total today: 1h 57m
```

**Tips:**
- Shows only completed entries (not running timer)
- Great for end-of-day review
- Helps verify you tracked everything

---

### 7. Weekly Summary

**When to use:** Weekly review, billing, productivity check

**Steps:**
1. Press `7`
2. View comprehensive 7-day breakdown

**Example Output:**
```
=== WEEKLY SUMMARY (Last 7 Days) ===

📊 By Project:
  Client A - Website: 12h 30m
  Client B - App: 8h 15m
  Internal - Marketing: 4h 45m
  No Project: 2h 0m

🏷️  By Tag:
  urgent: 6h 30m
  development: 10h 15m
  meeting: 3h 45m
  documentation: 4h 0m

📅 By Day:
  2025-01-06: 8h 15m
  2025-01-05: 7h 30m
  2025-01-04: 6h 0m
  2025-01-03: 5h 45m
  2025-01-02: 0h 0m
  2025-01-01: 0h 0m
  2024-12-31: 0h 0m

📈 Total Time: 27h 30m
💰 Billable Time: 20h 45m
```

**Best uses:**
- Monday morning reviews
- Client billing
- Personal productivity tracking
- Identifying time sinks
- Weekly planning

---

### 8. Search Entries

**When to use:** Finding specific work, generating reports

**Steps:**
1. Press `8`
2. Choose search type:
   - `1` - Search by description keyword
   - `2` - Search by project
   - `3` - Search by tag
   - `4` - Search by date
3. Enter search criteria
4. View matching entries

**Example 1 - By Description:**
```
=== SEARCH ENTRIES ===
1. Search by description
2. Search by project
3. Search by tag
4. Search by date

Select search type: 1
Enter description keyword: meeting

=== FOUND 5 ENTRIES ===
• Team standup → Team Project (15 min) [2025-01-06]
• Client sync → Client A (30 min) [2025-01-05]
• Sprint planning → Development (60 min) [2025-01-04]
• Weekly review → Team Project (45 min) [2025-01-03]
• Design review → Client B (30 min) [2025-01-02]

Total: 3h 0m
```

**Example 2 - By Project:**
```
Select search type: 2

=== YOUR PROJECTS ===
1. Client A - Website [✓]
2. Client B - App [✓]
3. Team Project [✓]

Select project number: 1

=== FOUND 8 ENTRIES ===
• Homepage design → Client A - Website (120 min) [2025-01-06]
• API integration → Client A - Website (90 min) [2025-01-05]
...

Total: 12h 30m
```

**Best uses:**
- "Show me all time on Client A"
- "Find all my meetings last month"
- "What did I do on January 3rd?"
- Monthly billing reports
- Project time audits

---

### 9. Edit Entry

**When to use:** Fix mistakes, update info, change categorization

**Steps:**
1. Press `9`
2. Select entry from last 10 entries
3. Choose what to edit:
   - `1` - Description
   - `2` - Project (supports `P` to create new)
   - `3` - Tags (supports `T` to create new)
   - `4` - Billable status
4. Make your change

**Example:**
```
=== SELECT ENTRY TO EDIT ===
1. Writing proposal → Client A - Website (47 min) [2025-01-06]
2. Team standup → Team Project (15 min) [2025-01-06]
3. Email responses → No project (30 min) [2025-01-06]

Select entry number: 3

=== WHAT TO EDIT? ===
1. Description
2. Project
3. Tags
4. Mark as Billable/Non-billable

Select what to edit: 2

=== YOUR PROJECTS ===
1. Client A - Website [✓]
2. Client B - App [✓]
P. Create New Project

Select project (number, P for new, 0 for none): P
New project name: Internal - Admin
✓ Project created: Internal - Admin
✓ Entry updated successfully
```

**Common uses:**
- Fix typos in descriptions
- Move entry to correct project (or create new with `P`)
- Add forgotten tags (or create new with `T`)
- Mark work as billable
- Correct categorization mistakes

---

### 10. Delete Entry

**When to use:** Remove duplicates, test entries, mistakes

**Steps:**
1. Press `10`
2. Select entry from last 10 entries
3. Type `yes` to confirm

**Example:**
```
=== SELECT ENTRY TO DELETE ===
1. Test entry → No project (1 min) [2025-01-06]
2. Writing proposal → Client A (47 min) [2025-01-06]

Select entry number to delete (0 to cancel): 1
⚠️  Delete 'Test entry'? (yes/no): yes
✓ Entry deleted: Test entry
```

**Safety features:**
- Shows last 7 days only (prevents old data deletion)
- Requires typing "yes" (not just "y")
- Logs all deletions

**Best uses:**
- Remove duplicate timers
- Clean up test entries
- Delete accidental starts
- Remove personal entries from work workspace

---

### 11. List Projects

**When to use:** View available projects

**Steps:**
1. Press `11`
2. View all projects

**Example:**
```
=== YOUR PROJECTS ===
1. Client A - Website [✓]
2. Client B - Mobile App [✓]
3. Internal - Marketing [✓]
4. Old Project [✗]
```

**Legend:**
- `[✓]` = Active project
- `[✗]` = Archived project

---

### 12. List Tags

**When to use:** View available tags

**Steps:**
1. Press `12`
2. View all tags

**Example:**
```
=== YOUR TAGS ===
1. urgent
2. meeting
3. development
4. documentation
5. bug-fix
6. research
```

---

### 13. Create Project

**When to use:** Starting new client work or category

**Steps:**
1. Press `13`
2. Enter project name
3. Choose if private (y/n)

**Example:**
```
=== CREATE PROJECT ===
Project name: Client C - Redesign
Private project? (y/n): n
✓ Project created: Client C - Redesign
```

**Tips:**
- Use clear, descriptive names
- Include client name for easy identification
- Private projects are hidden from other workspace members

---

### 14. Create Tag

**When to use:** Need new categorization

**Steps:**
1. Press `14`
2. Enter tag name

**Example:**
```
=== CREATE TAG ===
Tag name: client-call
✓ Tag created: client-call
```

**Useful tags:**
- `urgent`, `low-priority`
- `meeting`, `planning`, `development`
- `billable`, `internal`
- `research`, `bug-fix`, `feature`
- Client names for cross-project tracking

---

### O. Open Reports (Web)

**When to use:** View detailed reports, charts, and analytics

**Steps:**
1. Press `O` or `o`
2. Toggl Reports opens in your default browser

**Example:**
```
✓ Opening Toggl Reports in browser...
```

**What you'll see:**
- Detailed time reports with charts
- Filter by date range, project, client, tag
- Export options (PDF, CSV)
- Billable vs non-billable breakdown

**Best for:**
- Client invoicing
- Monthly reviews
- Detailed analytics beyond CLI capabilities

---

## 📄 Log File

All actions are logged to `toggl_cli_logs.txt` in the same folder as the script.

**Format:**
```
[YYYY-MM-DD HH:MM:SS] (Action): Details
```

**Example log:**
```
[2025-01-06 09:15:23] (Login): Logged in as john@example.com
[2025-01-06 09:16:45] (Start): Morning standup → Team Project
[2025-01-06 09:31:20] (Stop): Morning standup (15 min)
[2025-01-06 10:20:15] (Resume): Writing proposal → Client A - Website
[2025-01-06 14:30:00] (Edit): Updated entry #123456
[2025-01-06 15:00:00] (Create Project): Client C - Redesign
```

**Uses:**
- Audit trail of all actions
- Backup of your activity
- Debugging if something goes wrong
- Personal time journal

> ⚠️ **Note:** This file is in `.gitignore` and won't be committed to version control.

---

## 💡 Tips & Tricks

### For Maximum Productivity

1. **Use Resume (Option 4) liberally**
   - After bathroom breaks
   - After quick coffee
   - When returning to main task

2. **Establish naming conventions**
   - Good: "Client A - Homepage redesign"
   - Bad: "work stuff"

3. **Use tags consistently**
   - Create a standard set (urgent, meeting, development, etc.)
   - Apply them every time

4. **Weekly review habit**
   - Every Monday: Press `7` for weekly summary
   - Review what took most time
   - Plan accordingly

5. **Project organization**
   - One project per client
   - Use tags for task types
   - Keep descriptions specific

### Keyboard Shortcuts

While the CLI doesn't have traditional shortcuts, you can speed up your workflow:

1. **Keep it running in a terminal window**
   - Pin to taskbar (Windows)
   - Keep in dock (Mac)

2. **Quick actions**
   - Alt+Tab to CLI → `2` → Description → Enter → `n` → `n`
   - Practice the sequence!

3. **Create aliases (Advanced)**
   ```bash
   # Add to .bashrc or .bash_profile
   alias tt='cd ~/toggl && python3 toggl_cli.py'
   ```

### Common Workflows

**Morning Routine:**
```
1. Run toggl.bat
2. Press 7 → Review last week
3. Press 2 → Start first task
```

**Task Switching:**
```
1. Press 3 → Stop current
2. Press 2 → Start new task
```

**End of Day:**
```
1. Press 3 → Stop timer
2. Press 6 → Review today
3. Exit
```

**Fixing Mistakes:**
```
1. Press 10 → Delete wrong entry
2. Press 2 → Start correct entry
```

---

## 🔧 Troubleshooting

### "Python not found" or "command not found"

**Problem:** Python not installed or not in PATH

**Solution:**
1. Reinstall Python
2. Check "Add Python to PATH" during installation
3. Restart terminal/command prompt

**Test:**
```bash
python --version
```

### "Login failed. Please check your API token"

**Problem:** Invalid or expired API token

**Solution:**
1. Go to https://track.toggl.com/profile
2. Get a fresh API token
3. Run option `1` (Login) again
4. Paste the new token

### "Module 'requests' not found"

**Problem:** Required library not installed

**Solution:**
```bash
pip install requests
```

### "No timer is currently running"

**Problem:** Trying to stop when nothing is running

**Solution:**
- Check option `5` (Current Timer) to verify
- Start a timer with option `2` first

### Timer shows wrong time zone

**Problem:** Time entries appear off by hours

**Solution:**
- Toggl uses UTC internally, displays in your account timezone
- Check your timezone in Toggl web settings
- CLI will match your web interface

### Changes not showing in Toggl web interface

**Problem:** Entries made in CLI don't appear online

**Solution:**
1. Check internet connection
2. Verify you're in correct workspace
3. Refresh Toggl website (Ctrl+F5)
4. Wait 5-10 seconds for sync

### "Config file error" on startup

**Problem:** Corrupted toggl_config.json

**Solution:**
1. Delete `toggl_config.json`
2. Run option `1` (Login) to recreate
3. Select workspace again

---

## ❓ FAQ

### How do I switch workspaces?

Press `1` (Login), your workspaces will be listed. Select the new one.

### Can I track time to multiple projects simultaneously?

No, Toggl only supports one timer at a time. Stop the current timer before starting a new one.

### What happens if I close the terminal while a timer is running?

The timer keeps running on Toggl's servers. Restart the CLI and press `3` to stop it.

### Can I edit entries from more than 7 days ago?

The Edit and Delete features show recent entries only. Use the Toggl website for older entries.

### Is my data secure?

Yes! Your API token is stored locally in `toggl_config.json`. Never share this file. The CLI uses Toggl's official API with secure HTTPS.

### Can I use this on multiple computers?

Yes! Install on each computer and login with the same API token. Data syncs across all devices.

### Do I need to keep the CLI open for timers to run?

No. Once you start a timer, it runs on Toggl's servers. You can close the CLI.

### Can I use this offline?

No. The CLI requires internet to sync with Toggl. Toggl doesn't support offline time tracking.

### How do I uninstall?

Simply delete the folder containing the files. No registry entries or system files are created.

### Can I customize the menu?

The script is open source! Edit `toggl_cli.py` to add features or change behavior.

### What's the difference between projects and tags?

- **Projects**: Major categories (clients, work areas) - one per entry
- **Tags**: Multiple labels for categorization - many per entry

### How do I track billable hours?

1. When editing entries (option `9`), mark as billable
2. Or set projects as billable by default in Toggl web
3. View billable totals in Weekly Summary (option `7`)

---

## 🎓 Best Practices

### Time Tracking Discipline

1. **Track in real-time** - Don't reconstruct your day later
2. **Be specific** - "Client email" is better than "email"
3. **Track everything** - Meetings, breaks, admin work
4. **Review daily** - Press `6` each day
5. **Fix mistakes immediately** - Use Edit (9) right away

### Organization Tips

1. **Consistent naming**
   - Client work: "Client Name - Task description"
   - Internal: "Category - Task description"

2. **Tag hierarchy**
   - Type: meeting, development, admin
   - Priority: urgent, normal, low
   - Status: in-progress, blocked, review

3. **Project structure**
   - One project per client/major initiative
   - Archive completed projects
   - Use tags for task types within projects

### Privacy & Security

1. **Protect your API token** - It's like a password
2. **Don't share toggl_config.json** - Contains your token
3. **Use private projects** for sensitive work
4. **Review toggl_cli_logs.txt** - Delete if contains sensitive info
5. **Logout on shared computers** - Delete config file

---

## 📞 Support

### Need Help?

1. **Check this README** - Most questions are answered here
2. **Toggl Support** - https://support.toggl.com
3. **Toggl API Docs** - https://engineering.toggl.com/docs/

### Found a Bug?

1. Check toggl_cli_logs.txt for error messages
2. Note what you were doing when it occurred
3. Try deleting toggl_config.json and re-logging in

### Feature Requests?

This is an open-source project! Feel free to:
1. Modify the script for your needs
2. Share improvements with others
3. Keep it simple - that's the goal!

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

### What this means:

- ✅ **Free to use** - Use it for any purpose
- ✅ **Free to modify** - Customize it for your needs
- ✅ **Free to distribute** - Share it with others
- ✅ **Free to contribute** - Submit improvements
- ⚠️ **Copyleft** - Derivative works must also be GPL-3.0
- ⚠️ **Share source** - If you distribute, include source code

For the full license text, see the [LICENSE](LICENSE) file or visit [gnu.org/licenses/gpl-3.0](https://www.gnu.org/licenses/gpl-3.0).

---

## 🎉 You're Ready!

Start tracking your time like a pro. Remember:
- **Press 2** to start
- **Press 3** to stop  
- **Press 4** to resume
- **Press 7** for weekly insights

Happy time tracking! ⏱️
