# Toggl CLI - Code Documentation

## 📁 File Structure

```
toggl_cli/
├── toggl_cli.bat          # Windows launcher - entry point
├── toggl_cli.py           # Main Python application (1000+ lines)
├── toggl_config.json      # Created at runtime (API token, workspace, cache)
├── toggl_cli_logs.txt           # Created at runtime (activity log)
├── toggl_readme.md        # User guide (how to use)
├── toggl_context_readme.md # Project context (why & what)
└── toggl_code_readme.md   # This file (code documentation)
```

### File Dependency Map

| File | Type | Description |
|------|------|-------------|
| **`toggl_cli.bat`** | Entry Point | Windows launcher that invokes Python to run the CLI |
| **`toggl_cli.py`** | Core Application | Main Python script containing the `TogglCLI` class with all functionality |
| **`toggl_config.json`** | Runtime Config | Stores API token, workspace ID, cached projects, and cached tags |
| **`toggl_cli_logs.txt`** | Activity Log | Timestamped log of all CLI actions (logins, starts, stops, edits, etc.) |
| **`toggl_readme.md`** | Documentation | User guide - comprehensive how-to documentation |
| **`toggl_context_readme.md`** | Documentation | Design philosophy, target users, and project rationale |
| **`toggl_code_readme.md`** | Documentation | Technical documentation - architecture, API, methods |

### Key Constants

Defined in `toggl_cli.py`:

```python
CONFIG_FILE = "toggl_config.json"   # Configuration storage
LOG_FILE = "toggl_cli_logs.txt"           # Activity log
API_BASE = "https://api.track.toggl.com/api/v9"  # Toggl API endpoint
```

---

## 🔄 Execution Flow

### Application Startup

```
toggl_cli.bat
    │
    └──▶ python toggl_cli.py %*
              │
              ├──▶ TogglCLI.__init__()
              │         │
              │         ├──▶ load_config() → Reads toggl_config.json
              │         │
              │         └──▶ _start_session_log() → Adds blank line to toggl_cli_logs.txt
              │
              └──▶ cli.run() → Main menu loop
```

### Runtime Data Flow

```
User Input → Menu Selection
                 │
                 ├──▶ Timer Operations (start/stop/resume)
                 │         │
                 │         ├──▶ api_request() → Toggl API (HTTPS)
                 │         │
                 │         └──▶ log() → toggl_cli_logs.txt
                 │
                 ├──▶ View Operations (entries/summary/search)
                 │         │
                 │         └──▶ api_request() → Toggl API (HTTPS)
                 │
                 └──▶ Config Changes (login/create project/create tag)
                           │
                           ├──▶ api_request() → Toggl API (HTTPS)
                           │
                           ├──▶ save_config() → toggl_config.json
                           │
                           └──▶ log() → toggl_cli_logs.txt
```

---

## 🏗️ Architecture Overview

### Class Structure

```python
class TogglCLI:
    """Main application class - single class design for simplicity"""
    
    # Configuration
    api_token: str          # Toggl API authentication token
    workspace_id: int       # Active workspace ID
    user_data: dict         # User profile data from Toggl
    cached_projects: list   # Cached projects (reduces API calls)
    cached_tags: list       # Cached tags (reduces API calls)
    
    # Core Methods (see below)
```

### Design Pattern

- **Monolithic class**: All functionality in `TogglCLI` class
- **Menu-driven loop**: `run()` method contains main while loop
- **API wrapper**: `api_request()` handles all HTTP calls
- **Local logging**: Every action logged to `toggl_cli_logs.txt`
- **Caching**: Projects and tags cached to reduce API calls

---

## 🔧 Core Methods

### Configuration & Setup

| Method | Purpose |
|--------|---------|
| `__init__()` | Initialize instance, load config, start session log |
| `load_config()` | Load API token & workspace from JSON file |
| `save_config()` | Persist API token & workspace to JSON file |
| `_start_session_log()` | Add blank line separator in log for new session |
| `login()` | Authenticate with Toggl API, select workspace |

### Timer Operations

| Method | Purpose |
|--------|---------|
| `start_timer()` | Start new time entry with description, project, tags |
| `stop_timer()` | Stop currently running timer |
| `resume_last()` | Clone last stopped entry and start new timer |
| `current_timer()` | Display currently running timer details |

### Data Viewing

| Method | Purpose |
|--------|---------|
| `recent_entries()` | Show today's completed entries with totals |
| `weekly_summary()` | 7-day breakdown by project, tag, and day |
| `search_entries()` | Find entries by description, project, tag, or date |
| `list_projects()` | Display/cache projects (uses cache when selecting, API when listing) |
| `list_tags()` | Display/cache tags (uses cache when selecting, API when listing) |

### Data Management

| Method | Purpose |
|--------|---------|
| `edit_entry()` | Modify description, project, tags, or billable status |
| `delete_entry()` | Remove time entry with confirmation |
| `create_project()` | Add new project to workspace (menu option 13) |
| `create_tag()` | Add new tag to workspace (menu option 14) |
| `_quick_create_project()` | On-the-fly project creation during timer start (returns ID) |
| `_quick_create_tag()` | On-the-fly tag creation during timer start (returns ID) |

### Utilities

| Method | Purpose |
|--------|---------|
| `api_request()` | Generic HTTP request wrapper with auth & error handling |
| `log()` | Append timestamped message to toggl_cli_logs.txt |
| `show_menu()` | Render the two-column categorized menu |
| `open_reports()` | Launch Toggl Reports in default browser |
| `run()` | Main application loop |

---

## 🌐 API Integration

### Toggl API v9 Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/me` | GET | Authenticate & get user info |
| `/me/workspaces` | GET | List user's workspaces |
| `/me/projects` | GET | List all projects |
| `/me/tags` | GET | List all tags |
| `/me/time_entries` | GET | Fetch time entries (with date filters) |
| `/me/time_entries/current` | GET | Get currently running timer |
| `/workspaces/{id}/time_entries` | POST | Create new time entry |
| `/workspaces/{id}/time_entries/{id}` | PUT | Update existing entry |
| `/workspaces/{id}/time_entries/{id}` | DELETE | Remove entry |
| `/workspaces/{id}/time_entries/{id}/stop` | PATCH | Stop running timer |
| `/workspaces/{id}/projects` | POST | Create new project |
| `/workspaces/{id}/tags` | POST | Create new tag |

### Authentication

```python
# Basic Auth with API token
auth = b64encode(f"{api_token}:api_token".encode()).decode('ascii')
headers = {'Authorization': f'Basic {auth}'}
```

---

## 📦 Dependencies

### Python Standard Library
- `datetime` - Time handling with timezone awareness
- `json` - Config file read/write
- `sys` - System exit handling
- `os` - File path operations
- `base64` - API token encoding
- `webbrowser` - Open Toggl Reports in browser

### External Package
- `requests` - HTTP client for API calls

### Installation
```bash
pip install requests
```

The batch file auto-installs this if missing.

---

## 🔄 Data Flow

### Starting a Timer

```
User Input → start_timer()
                ↓
         Prompt for description
                ↓
         Prompt for project (optional) → list_projects()
                ↓
         Prompt for tags (optional) → list_tags()
                ↓
         api_request('POST', '/workspaces/.../time_entries')
                ↓
         log() → toggl_cli_logs.txt
                ↓
         Display confirmation
```

### Loading Config

```
__init__() → load_config()
                ↓
         Check if toggl_config.json exists
                ↓
         Parse JSON → set api_token, workspace_id, cached_projects, cached_tags
                ↓
         _start_session_log() → Add blank line to log
```

---

## 📦 Caching System

### Why Caching?

Toggl API has rate limits and each call counts. Caching projects and tags locally:
- Reduces API calls significantly
- Speeds up timer start/edit workflows
- Works offline for project/tag selection

### Cache Storage

Cached data is stored in `toggl_config.json`:

```json
{
  "api_token": "your-token",
  "workspace_id": 12345,
  "cached_projects": [...],
  "cached_tags": [...]
}
```

### Cache Refresh Triggers

| Action | What Happens |
|--------|-------------|
| **Login (Option 1)** | Fetches and caches projects + tags |
| **List Projects (Option 11)** | Fresh API call, updates cache |
| **List Tags (Option 12)** | Fresh API call, updates cache |
| **Create Project (Option 13)** | Creates + refreshes projects cache |
| **Create Tag (Option 14)** | Creates + refreshes tags cache |
| **Start Timer (Option 2)** | Uses cache (no API call for projects/tags) |
| **Edit Entry (Option 9)** | Uses cache (no API call for projects/tags) |
| **Search (Option 8)** | Uses cache (no API call for projects/tags) |

---

## ⏰ Timezone Handling

The code uses timezone-aware datetime objects:

```python
from datetime import datetime, timezone

# UTC timestamps for API
datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# Local time for display and logging
datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

This ensures:
- API receives RFC3339 formatted timestamps
- Local log shows user's actual time
- No deprecation warnings (avoids `datetime.utcnow()`)

---

## 📝 Logging Format

### Log File: `toggl_cli_logs.txt`

```
[2025-01-06 09:00:00] (Login): Logged in as user@example.com
[2025-01-06 09:01:23] (Start): Working on feature → My Project
[2025-01-06 09:45:00] (Stop): Working on feature (43 min)
[2025-01-06 09:45:30] (Resume): Working on feature → My Project

[2025-01-06 14:00:00] (Start): Client meeting → Client Project
```

### Log Entry Types

| Type | When Logged |
|------|-------------|
| `(Login)` | Successful authentication |
| `(Start)` | Timer started |
| `(Stop)` | Timer stopped |
| `(Resume)` | Last timer resumed |
| `(Edit)` | Entry modified |
| `(Delete)` | Entry removed |
| `(Create Project)` | New project added |
| `(Create Tag)` | New tag added |
| `(Open)` | Toggl Reports opened in browser |
| `(Error)` | API or system errors |

---

## 🖥️ Menu Structure

### Two-Column Categorized Layout

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

## 🛡️ Error Handling

### API Errors
```python
if response.status_code in [200, 201]:
    return response.json()
else:
    error_msg = f"API Error {response.status_code}: {response.text}"
    print(f"✗ {error_msg}")
    self.log(f"(Error): {error_msg}")
    return None
```

### Network Errors
```python
except requests.exceptions.RequestException as e:
    error_msg = f"Network error: {e}"
    print(f"✗ {error_msg}")
    self.log(f"(Error): {error_msg}")
    return None
```

### User Input Errors
```python
except ValueError:
    print("✗ Please enter a valid number")
```

---

## 🔐 Security Considerations

| Aspect | Implementation |
|--------|----------------|
| **Token Storage** | Local JSON file (not in code) |
| **API Auth** | HTTPS only, Basic Auth |
| **Logging** | Tokens never logged |
| **Config File** | Should be in `.gitignore` |

### Recommended .gitignore

```gitignore
toggl_config.json
toggl_cli_logs.txt
__pycache__/
*.pyc
```

---

## 🧪 Testing Notes

### Manual Testing Checklist

- [ ] Login with valid API token
- [ ] Login with invalid token (should fail gracefully)
- [ ] Start timer with project and tags
- [ ] Start timer without project/tags
- [ ] Stop running timer
- [ ] Stop when no timer running (should show message)
- [ ] Resume last timer
- [ ] View today's entries
- [ ] View weekly summary
- [ ] Search by each criteria type
- [ ] Edit entry (all 4 options)
- [ ] Delete entry (test "yes" confirmation)
- [ ] Create project
- [ ] Create tag
- [ ] Open Reports in browser
- [ ] Exit gracefully
- [ ] Ctrl+C interrupt handling

---

## 📄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-06 | Initial release with all core features |

---

## 📝 Related Files

| File | Purpose |
|------|---------|
| `toggl_readme.md` | User guide - how to use |
| `toggl_context_readme.md` | Project context - why & what |
| `toggl_cli.py` | Main Python application |
| `toggl_cli.bat` | Windows launcher script |
