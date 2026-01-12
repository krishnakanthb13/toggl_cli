# Toggl CLI - Context & Purpose

## 🎯 Why This Project?

### The Problem

Time tracking is essential for:
- **Freelancers** billing clients accurately
- **Developers** understanding where time goes
- **Remote workers** staying accountable
- **Students** managing study sessions
- **Anyone** wanting better time awareness

However, traditional time tracking has friction:
- 🖱️ Switching to browser tabs breaks flow
- 📱 Mobile apps require context switching
- ⌨️ Existing CLI tools require memorizing complex commands

### The Solution

A **keyboard-first, menu-driven CLI** that:
- Stays in your terminal where you already work
- Uses simple number inputs (no commands to memorize)
- Syncs directly with Toggl's cloud platform
- Logs everything locally for backup

---

## 🧠 Design Philosophy

### 1. Simplicity Over Complexity
- Number-based menu (press `2` to start, `3` to stop)
- No flags, no arguments, no learning curve
- Progressive disclosure (simple first, details when needed)

### 2. Speed Over Polish
- Resume last timer in one keystroke (`4`)
- Skip projects/tags with a quick `n`
- Minimal prompts, maximum efficiency

### 3. Safety Over Risk
- All actions logged to `toggl_cli_logs.txt`
- Deletion requires typing "yes" (not just "y")
- Config saved locally (token never transmitted insecurely)

### 4. Integration Over Isolation
- Full sync with Toggl web/mobile apps
- Opens Toggl Reports in browser (Option `O`)
- Uses Toggl's official API v9

---

## 👥 Target Users

| User Type | Primary Use Case |
|-----------|------------------|
| **Developers** | Track coding sessions without leaving terminal |
| **Freelancers** | Quick client billing with project tracking |
| **Students** | Pomodoro-style study session tracking |
| **Remote Workers** | Accountability and time awareness |
| **CLI Enthusiasts** | Keyboard-first workflow preference |

---

## 🔄 Workflow Integration

### Typical Developer Workflow

```
1. Open terminal for work
2. Run toggl_cli.bat
3. Press 2 → "Implementing feature X"
4. Code, code, code...
5. Meeting? Press 3 (stop), then 2 (new timer)
6. Back to coding? Press 4 (resume)
7. End of day: Press 6 (review), then 0 (exit)
```

### Pomodoro Integration

The local log file (`toggl_cli_logs.txt`) was designed with Pomodoro technique users in mind:
- Automatic timestamping of all starts/stops
- Session separation with blank lines
- Easy to review at day's end

---

## 📊 What This Does NOT Do

To keep the tool focused, these features were intentionally excluded:

| Feature | Reason |
|---------|--------|
| GUI interface | Defeats keyboard-first purpose |
| Automatic time detection | Privacy/complexity concerns |
| Multiple workspace switching | Use web app for admin tasks |
| Detailed reporting | Use Toggl Reports (Option O) |
| Team management | Enterprise feature, use web |

---

## 🛠️ Technology Choices

| Choice | Reason |
|--------|--------|
| **Python** | Cross-platform, readable, widely installed |
| **requests library** | Simple HTTP, auto-installed by batch |
| **JSON config** | Human-readable, easy to backup |
| **Plain text log** | Universal, grep-able, version-controllable |
| **Toggl API v9** | Latest stable API version |

---

## 📈 Future Possibilities

Potential enhancements (not currently planned):
- [ ] Keyboard shortcuts for common projects
- [ ] Timer notifications/reminders
- [ ] Offline mode with sync queue
- [ ] Integration with other tools (Git hooks, etc.)
- [ ] Custom report generation

---

## 📝 Related Files

### Core Files (Execution Chain)

| File | Type | Purpose |
|------|------|---------|
| `toggl_cli.bat` | Entry Point | Windows launcher that invokes Python to run the CLI |
| `toggl_cli.py` | Core Application | Main Python script (1000+ lines) with all functionality |
| `toggl_config.json` | Runtime Config | Auto-created; stores API token, workspace ID, and cached data |
| `toggl_cli_logs.txt` | Activity Log | Auto-created; timestamped log of all CLI actions |

### Documentation Files

| File | Purpose |
|------|---------|
| `toggl_readme.md` | User guide - comprehensive how-to documentation |
| `toggl_context_readme.md` | Design philosophy, target users, and project rationale (this file) |
| `toggl_code_readme.md` | Technical documentation - architecture, API, methods |

### Quick Execution Flow

```
toggl_cli.bat → python toggl_cli.py
                      │
                      ├── Reads/Writes: toggl_config.json
                      ├── Writes: toggl_cli_logs.txt
                      └── Calls: Toggl API (https://api.track.toggl.com/api/v9)
```

**Total Files: 7** (1 batch, 1 Python, 2 runtime data, 3 documentation)
