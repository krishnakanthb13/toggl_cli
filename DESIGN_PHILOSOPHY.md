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
- **Progressive disclosure**: Core features are front-and-center; advanced "Settings" are tucked into a dedicated menu (`S`) for power users.

### 2. Speed & Efficiency
- Resume last timer in one keystroke (`4`)
- Skip projects/tags with a quick `n`
- **Smart Caching**: 70% reduction in API latency by caching projects, tags, orgs, and clients locally.
- Minimal prompts, maximum productivity.

### 3. Safety & Performance
- All actions logged to `toggl_cli_logs.txt`
- Deletion requires typing "yes" (not just "y")
- Config saved locally (token never transmitted insecurely)
- **Quota Awareness**: Real-time monitoring of API limits to prevent account throttling.

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
| Enterprise automation | Too complex for a lightweight CLI |
| Advanced Visualizations | Use AI Reviewer (HTML) or Web Reports (Option O) |
| Detailed Team management | Use official Toggl web interface |

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

Potential enhancements:
- [ ] Keyboard shortcuts for common projects (e.g., press `F1` for `Project A`)
- [ ] Timer notifications/reminders (desktop alerts)
- [ ] Offline mode with sync queue
- [ ] Integration with other tools (Git commit hooks, CI/CD signals)
- [ ] Task selection integration (assign tasks to time entries)
- [ ] Custom CLI report generator (lightweight daily stats)

---

## 📝 Related Files

### Core Files (Execution Chain)

| File | Type | Purpose |
|------|------|---------|
| `toggl_cli.bat` | Entry Point | Windows launcher that invokes Python to run the CLI |
| `toggl_cli.py` | Core Application | Main Python script containing the `TogglCLI` class |
| `toggl_config.json` | Runtime Config | Stores API token, workspace ID, and all cached entities |
| `toggl_cli_logs.txt` | Activity Log | Auto-created; timestamped log of all CLI actions |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | User guide - comprehensive how-to documentation |
| `DESIGN_PHILOSOPHY.md` | Project rationale, target users, and ideology (this file) |
| `CODE_DOCUMENTATION.md` | Technical documentation - architecture, API, implementation |
| `Reference/CACHE_USAGE_GUIDE.md` | Detailed guide on caching behavior and manual refreshes |
| `Reference/API_CACHING_SUMMARY.md` | Performance analysis showing API call reductions |
| `Reference/SETTINGS_QUICK_REFERENCE.md` | Practical guide for the Toggl Settings submenu |
| `Reference/FEATURE_IMPLEMENTATION_SUMMARY.md` | Complete inventory of implemented Toggl features |

### Quick Execution Flow

```
toggl_cli.bat → python toggl_cli.py
                      │
                      ├── Reads/Writes: toggl_config.json
                      ├── Writes: toggl_cli_logs.txt
                      └── Calls: Toggl API (https://api.track.toggl.com/api/v9)
```

**Total Documentation Files: 7**
**Total Project Files: 11** (1 batch, 1 Python, 2 runtime data, 7 documentation)
