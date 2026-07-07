#!/usr/bin/env python3
"""
Toggl Time Tracker CLI
A simple command-line interface for tracking time with Toggl
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
from base64 import b64encode
import os
import webbrowser

# Configuration
CONFIG_FILE = "toggl_config.json"
LOG_FILE = "toggl_cli_logs.txt"
API_BASE = "https://api.track.toggl.com/api/v9"


class TogglCLI:
    def __init__(self):
        self.api_token = None
        self.workspace_id = None
        self.user_data = None
        self.cached_projects = []  # Cached projects list
        self.cached_tags = []      # Cached tags list
        self.cached_organizations = []  # Cached organizations
        self.cached_clients = []   # Cached clients
        self.cached_tasks = []     # Cached tasks
        self.cached_workspaces = []  # Cached workspaces
        self._recent_project_ids = None  # Cached recent project IDs
        self._recent_project_ids_ts = 0  # Timestamp of last refresh
        self.load_config()
        self._start_session_log()

    def load_config(self):
        """Load configuration and cached data from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.api_token = config.get('api_token')
                    self.workspace_id = config.get('workspace_id')
                    self.cached_projects = config.get('cached_projects', [])
                    self.cached_tags = config.get('cached_tags', [])
                    self.cached_organizations = config.get('cached_organizations', [])
                    self.cached_clients = config.get('cached_clients', [])
                    self.cached_tasks = config.get('cached_tasks', [])
                    self.cached_workspaces = config.get('cached_workspaces', [])
            except Exception as e:
                corrupt_path = CONFIG_FILE + '.corrupt.json'
                try:
                    os.replace(CONFIG_FILE, corrupt_path)
                    print(f"⚠️  Config corrupted — saved as {corrupt_path}, starting fresh")
                except Exception:
                    print(f"⚠️  Config corrupted — could not rename: {e}")
                self.log(f"Error loading config (renamed to .corrupt): {e}")

    def _start_session_log(self):
        """Add a blank line to separate sessions in the log file"""
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write("\n")
        except Exception:
            pass  # Silently ignore if log file can't be written

    def save_config(self, silent=False):
        """Save configuration and cached data to file (atomic write)"""
        try:
            config = {
                'version': 1,
                'api_token': self.api_token,
                'workspace_id': self.workspace_id,
                'cached_projects': self.cached_projects,
                'cached_tags': self.cached_tags,
                'cached_organizations': self.cached_organizations,
                'cached_clients': self.cached_clients,
                'cached_tasks': self.cached_tasks,
                'cached_workspaces': self.cached_workspaces
            }
            tmp_path = CONFIG_FILE + '.tmp'
            with open(tmp_path, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, CONFIG_FILE)
            if not silent:
                print(f"✓ Configuration saved to {CONFIG_FILE}")
        except Exception as e:
            print(f"✗ Error saving config: {e}")

    def log(self, message):
        """Append log entry to toggl_cli_logs.txt"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")

    def _get_project_name(self, project_id):
        """Look up project name from cache by ID"""
        if not project_id:
            return "No project"
        for proj in self.cached_projects:
            if proj.get('id') == project_id:
                return proj.get('name', 'Unknown project')
        return f"Project #{project_id}"  # Fallback if not in cache

    def _get_tag_names(self, tag_ids):
        """Look up tag names from cache by IDs"""
        if not tag_ids:
            return []
        names = []
        for tag in self.cached_tags:
            if tag.get('id') in tag_ids:
                names.append(tag.get('name', 'Unknown tag'))
        return names

    def api_request(self, method, endpoint, data=None):
        """Make API request to Toggl with single retry on timeout."""
        if not self.api_token:
            print("✗ Error: Not logged in. Please login first (Option 1)")
            return None

        url = f"{API_BASE}{endpoint}"
        auth = b64encode(f"{self.api_token}:api_token".encode()).decode('ascii')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth}'
        }

        for attempt in range(2):
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=30)
                elif method == 'POST':
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                elif method == 'PATCH':
                    response = requests.patch(url, headers=headers, json=data, timeout=30)
                elif method == 'PUT':
                    response = requests.put(url, headers=headers, json=data, timeout=30)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=headers, timeout=30)
                else:
                    return None

                if response.status_code in (200, 201):
                    return response.json()
                if response.status_code == 204:
                    return {}
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    print(f"✗ {error_msg}")
                    self.log(f"(Error): {error_msg}")
                    return None

            except requests.exceptions.Timeout:
                if attempt == 0:
                    print("⏱ Timeout, retrying...")
                    continue
                error_msg = "Network error: Request timed out after retry"
                print(f"✗ {error_msg}")
                self.log(f"(Error): {error_msg}")
                return None
            except requests.exceptions.RequestException as e:
                error_msg = f"Network error: {e}"
                print(f"✗ {error_msg}")
                self.log(f"(Error): {error_msg}")
                return None

    def login(self):
        """Login and setup workspace"""
        print("\n=== TOGGL LOGIN ===")
        api_token = input("Enter your Toggl API token: ").strip()
        
        if not api_token:
            print("✗ API token cannot be empty")
            return

        # Test the token
        self.api_token = api_token
        user_data = self.api_request('GET', '/me')
        
        if not user_data:
            print("✗ Login failed. Please check your API token.")
            self.api_token = None
            return

        self.user_data = user_data
        print(f"✓ Welcome, {user_data.get('fullname', 'User')}!")
        self.log(f"(Login): Logged in as {user_data.get('email')}")

        # Get workspaces
        workspaces = self.api_request('GET', '/me/workspaces')
        
        if not workspaces:
            print("✗ Could not fetch workspaces")
            return

        print("\n=== SELECT WORKSPACE ===")
        for idx, ws in enumerate(workspaces, 1):
            print(f"{idx}. {ws['name']}")

        try:
            choice = int(input("\nSelect workspace number: "))
            if 1 <= choice <= len(workspaces):
                self.workspace_id = workspaces[choice - 1]['id']
                print(f"✓ Selected workspace: {workspaces[choice - 1]['name']}")
                
                # Fetch and cache projects and tags
                print("\n⏳ Fetching projects and tags for cache...")
                projects = self.api_request('GET', '/me/projects')
                tags = self.api_request('GET', '/me/tags')
                
                if projects:
                    self.cached_projects = projects
                    print(f"✓ Cached {len(projects)} projects")
                if tags:
                    self.cached_tags = tags
                    print(f"✓ Cached {len(tags)} tags")
                
                self.save_config()
            else:
                print("✗ Invalid selection")
        except ValueError:
            print("✗ Please enter a valid number")

    def start_timer(self):
        """Start a new time entry"""
        if not self.workspace_id:
            print("✗ Please login and select a workspace first")
            return

        print("\n=== START TIMER ===")
        description = input("Enter task description: ").strip()
        
        if not description:
            print("✗ Description cannot be empty")
            return

        # Ask for project (optional)
        use_project = input("Track to a project? (y/n) [n]: ").strip().lower()
        project_id = None
        project_name = None

        if use_project in ['y', 'yes']:
            projects = self.list_projects(return_data=True)
            if projects:
                recent_ids = self._get_recent_project_ids()
                recent = [p for p in projects if p['id'] in recent_ids]
                if recent:
                    print("\n=== RECENT PROJECTS ===")
                    for idx, project in enumerate(recent, 1):
                        active = "✓" if project.get('active', True) else "✗"
                        print(f"{idx}. {project['name']} [{active}]")

                print("\n=== ALL PROJECTS ===")
                for idx, project in enumerate(projects, 1):
                    active = "✓" if project.get('active', True) else "✗"
                    print(f"{idx}. {project['name']} [{active}]")
                print("P. Create New Project")

                choice = input("\nSelect project (number, name, or P): ").strip()

                if choice.lower() == 'p':
                    project_id, project_name = self._quick_create_project()
                else:
                    selected = self._fuzzy_select(projects, "")
                    if selected:
                        project_id = selected['id']
                        project_name = selected['name']
                    else:
                        print("✗ No project assigned")
            else:
                # No projects exist, offer to create one
                print("\nℹ No projects found.")
                create_new = input("Create a new project? (y/n) [n]: ").strip().lower()
                if create_new in ['y', 'yes']:
                    project_id, project_name = self._quick_create_project()
        elif use_project and use_project not in ['n', 'no', '']:
            print(f"✗ '{use_project}' is not valid. Enter 'y' or 'n'. Skipping project.")

        # Ask for tags (optional)
        use_tags = input("Add tags? (y/n) [n]: ").strip().lower()
        tag_ids = []

        if use_tags in ['y', 'yes']:
            tags = self.list_tags(return_data=True)
            if tags:
                print("\n=== YOUR TAGS ===")
                for idx, tag in enumerate(tags, 1):
                    print(f"{idx}. {tag['name']}")
                print("T. Create New Tag")

                tag_input = input("\nEnter tags (numbers, names, T for new, comma-separated): ").strip()

                # Process mixed input (e.g., "1,T,3" or "1,urgent,3")
                for item in tag_input.split(','):
                    item = item.strip()
                    if item.lower() == 't':
                        new_tag_id = self._quick_create_tag()
                        if new_tag_id:
                            tag_ids.append(new_tag_id)
                            tags = self.cached_tags
                    else:
                        # Try number first
                        try:
                            choice_num = int(item)
                            if 1 <= choice_num <= len(tags):
                                tag_ids.append(tags[choice_num - 1]['id'])
                                continue
                        except ValueError:
                            pass
                        # Fuzzy match by name
                        choice_lower = item.lower()
                        matches = [t for t in tags if choice_lower in t.get('name', '').lower()]
                        if len(matches) == 1:
                            tag_ids.append(matches[0]['id'])
                        elif len(matches) > 1:
                            print(f"  ⚠ Ambiguous tag '{item}' — {len(matches)} matches, skipping")
                
                if not tag_ids:
                    print("✗ No valid tags selected")
            else:
                # No tags exist, offer to create one
                print("\nℹ No tags found.")
                create_new = input("Create a new tag? (y/n) [n]: ").strip().lower()
                if create_new in ['y', 'yes']:
                    new_tag_id = self._quick_create_tag()
                    if new_tag_id:
                        tag_ids.append(new_tag_id)
        elif use_tags and use_tags not in ['n', 'no', '']:
            print(f"✗ '{use_tags}' is not valid. Enter 'y' or 'n'. Skipping tags.")

        # Start the timer
        data = {
            "description": description,
            "workspace_id": self.workspace_id,
            "duration": -1,
            "start": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "created_with": "toggl-cli"
        }

        if project_id:
            data["project_id"] = project_id

        if tag_ids:
            data["tag_ids"] = tag_ids

        result = self.api_request('POST', f'/workspaces/{self.workspace_id}/time_entries', data)

        if result:
            project_info = f" → {project_name}" if project_name else " (no project)"
            tags_info = f" [tags: {len(tag_ids)}]" if tag_ids else ""
            print(f"✓ Timer started: {description}{project_info}{tags_info}")
            self.log(f"(Start): {description}{project_info}{tags_info}")
        else:
            print("✗ Failed to start timer")

    def stop_timer(self):
        """Stop the current running timer"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        current = self.api_request('GET', f'/me/time_entries/current')
        
        if not current or not current.get('id'):
            print("✗ No timer is currently running")
            return

        entry_id = current['id']
        result = self.api_request('PATCH', f'/workspaces/{self.workspace_id}/time_entries/{entry_id}/stop', {})

        if result:
            description = current.get('description', 'Untitled')
            duration = result.get('duration', 0)
            minutes = duration // 60
            print(f"✓ Timer stopped: {description} ({minutes} min)")
            self.log(f"(Stop): {description} ({minutes} min)")
        else:
            print("✗ Failed to stop timer")

    def current_timer(self):
        """Show current running timer"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        current = self.api_request('GET', f'/me/time_entries/current')
        
        if not current or not current.get('id'):
            print("ℹ No timer is currently running")
            return

        description = current.get('description', 'Untitled')
        start_time = current.get('start', '')
        project_id = current.get('project_id')
        
        # Look up project and tags from cache
        project_name = self._get_project_name(project_id)
        tag_names = self._get_tag_names(current.get('tag_ids', []))
        
        # Calculate duration
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            duration = (datetime.now(start.tzinfo) - start).total_seconds()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            time_str = f"{minutes}m {seconds}s"
        except:
            time_str = "Unknown"

        print(f"\n⏱ CURRENT TIMER")
        print(f"Task: {description}")
        print(f"Project: {project_name}")
        if tag_names:
            print(f"Tags: {', '.join(tag_names)}")
        print(f"Duration: {time_str}")

    def list_projects(self, return_data=False):
        """List all projects. Uses cache when return_data=True, fetches from API otherwise."""
        if not self.workspace_id:
            print("✗ Please login first")
            return []

        # If return_data=True (selecting for timer), use cache if available
        if return_data:
            if self.cached_projects:
                return self.cached_projects
            # No cache, need to fetch
            projects = self.api_request('GET', '/me/projects')
            if projects:
                self.cached_projects = projects
                self.save_config(silent=True)
                return projects
            return []

        # Called from menu (option 11) - always fetch fresh and update cache
        print("\n⏳ Fetching projects from Toggl...")
        projects = self.api_request('GET', '/me/projects')
        
        if not projects:
            print("ℹ No projects found")
            return []

        # Update cache
        self.cached_projects = projects
        self.save_config(silent=True)

        print("\n=== YOUR PROJECTS (Updated) ===")
        for idx, project in enumerate(projects, 1):
            active = "✓" if project.get('active', True) else "✗"
            print(f"{idx}. {project['name']} [{active}]")
        
        print(f"\n✓ Cache updated with {len(projects)} projects")
        return []

    def list_tags(self, return_data=False):
        """List all tags. Uses cache when return_data=True, fetches from API otherwise."""
        if not self.workspace_id:
            print("✗ Please login first")
            return []

        # If return_data=True (selecting for timer), use cache if available
        if return_data:
            if self.cached_tags:
                return self.cached_tags
            # No cache, need to fetch
            tags = self.api_request('GET', '/me/tags')
            if tags:
                self.cached_tags = tags
                self.save_config(silent=True)
                return tags
            return []

        # Called from menu (option 12) - always fetch fresh and update cache
        print("\n⏳ Fetching tags from Toggl...")
        tags = self.api_request('GET', '/me/tags')
        
        if not tags:
            print("ℹ No tags found")
            return []

        # Update cache
        self.cached_tags = tags
        self.save_config(silent=True)

        print("\n=== YOUR TAGS (Updated) ===")
        for idx, tag in enumerate(tags, 1):
            print(f"{idx}. {tag['name']}")
        
        print(f"\n✓ Cache updated with {len(tags)} tags")
        return []

    def _quick_create_project(self):
        """Quick project creation for on-the-fly use during timer start.
        Returns (project_id, project_name) on success, (None, None) on failure."""
        name = input("New project name: ").strip()

        if not name:
            print("✗ Project name cannot be empty")
            return None, None

        for p in self.cached_projects:
            if p.get('name', '').strip().casefold() == name.strip().casefold():
                print(f"✗ Project '{name}' already exists (use option 11 to see all)")
                return None, None

        data = {
            "name": name,
            "is_private": False,  # Default to non-private for speed
            "active": True
        }

        result = self.api_request('POST', f'/workspaces/{self.workspace_id}/projects', data)

        if result:
            print(f"✓ Project created: {name}")
            self.log(f"(Create Project): {name}")
            # Add to cache directly (no extra API call)
            self.cached_projects.append(result)
            self._recent_project_ids = None  # Invalidate recent project cache
            self.save_config(silent=True)
            return result.get('id'), name
        else:
            print("✗ Failed to create project")
            return None, None

    def _quick_create_tag(self):
        """Quick tag creation for on-the-fly use during timer start.
        Returns tag_id on success, None on failure."""
        name = input("New tag name: ").strip()

        if not name:
            print("✗ Tag name cannot be empty")
            return None

        for t in self.cached_tags:
            if t.get('name', '').strip().casefold() == name.strip().casefold():
                print(f"✗ Tag '{name}' already exists (use option 12 to see all)")
                return None

        data = {"name": name}

        result = self.api_request('POST', f'/workspaces/{self.workspace_id}/tags', data)

        if result:
            print(f"✓ Tag created: {name}")
            self.log(f"(Create Tag): {name}")
            # Add to cache directly (no extra API call)
            self.cached_tags.append(result)
            self.save_config(silent=True)
            return result.get('id')
        else:
            print("✗ Failed to create tag")
            return None

    def _fuzzy_select(self, items, prompt_text="Select"):
        """Let user type a number OR partial name to select from a list."""
        choice = input(prompt_text).strip()
        # Try as number first
        try:
            idx = int(choice)
            if 1 <= idx <= len(items):
                return items[idx - 1]
            print(f"✗ Number out of range (1-{len(items)})")
            return None
        except ValueError:
            pass
        # Fuzzy match by name
        choice_lower = choice.lower()
        matches = [i for i in items if choice_lower in i.get('name', '').lower()]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"✗ Ambiguous — {len(matches)} matches. Be more specific.")
        else:
            print(f"✗ No match for '{choice}'")
        return None

    def _get_recent_project_ids(self, limit=5):
        """Get project IDs from today's most recent entries (cached for 5 min)."""
        import time
        now = time.time()
        if self._recent_project_ids is not None and (now - self._recent_project_ids_ts) < 300:
            return self._recent_project_ids

        if not self.workspace_id:
            return set()
        start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', 'Z')
        end_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entries = self.api_request('GET', f'/me/time_entries?start_date={start_date}&end_date={end_date}')
        if not entries:
            return set()
        recent_ids = set()
        for e in reversed(entries[-10:]):
            pid = e.get('project_id')
            if pid:
                recent_ids.add(pid)
                if len(recent_ids) >= limit:
                    break

        self._recent_project_ids = recent_ids
        self._recent_project_ids_ts = now
        return recent_ids

    def create_project(self):
        """Create a new project"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        print("\n=== CREATE PROJECT ===")
        name = input("Project name: ").strip()
        
        if not name:
            print("✗ Project name cannot be empty")
            return

        is_private = input("Private project? (y/n): ").strip().lower() == 'y'

        data = {
            "name": name,
            "is_private": is_private,
            "active": True
        }

        result = self.api_request('POST', f'/workspaces/{self.workspace_id}/projects', data)

        if result:
            print(f"✓ Project created: {name}")
            self.log(f"(Create Project): {name}")
            # Refresh projects cache
            print("⏳ Updating projects cache...")
            projects = self.api_request('GET', '/me/projects')
            if projects:
                self.cached_projects = projects
                self.save_config(silent=True)
                print(f"✓ Cache updated with {len(projects)} projects")
        else:
            print("✗ Failed to create project")

    def create_tag(self):
        """Create a new tag"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        print("\n=== CREATE TAG ===")
        name = input("Tag name: ").strip()
        
        if not name:
            print("✗ Tag name cannot be empty")
            return

        data = {"name": name}

        result = self.api_request('POST', f'/workspaces/{self.workspace_id}/tags', data)

        if result:
            print(f"✓ Tag created: {name}")
            self.log(f"(Create Tag): {name}")
            # Refresh tags cache
            print("⏳ Updating tags cache...")
            tags = self.api_request('GET', '/me/tags')
            if tags:
                self.cached_tags = tags
                self.save_config(silent=True)
                print(f"✓ Cache updated with {len(tags)} tags")
        else:
            print("✗ Failed to create tag")

    def recent_entries(self):
        """Show recent time entries"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Get entries from today
        start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', 'Z')
        end_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        entries = self.api_request('GET', f'/me/time_entries?start_date={start_date}&end_date={end_date}')

        if not entries:
            print("ℹ No entries today")
            return

        print("\n=== TODAY'S ENTRIES ===")
        total_duration = 0
        
        for entry in reversed(entries):  # Show newest first
            description = entry.get('description', 'Untitled')
            duration = entry.get('duration', 0)
            if duration > 0:
                minutes = duration // 60
                total_duration += duration
                project_name = self._get_project_name(entry.get('project_id'))
                project_str = f" → {project_name}" if entry.get('project_id') else ""
                print(f"• {description}{project_str} ({minutes} min)")

        total_hours = total_duration // 3600
        total_mins = (total_duration % 3600) // 60
        print(f"\nTotal today: {total_hours}h {total_mins}m")

    def weekly_summary(self):
        """Show weekly time summary"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Get entries from the past 7 days
        from datetime import timedelta
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        start_str = start_date.isoformat().replace("+00:00", "Z")
        end_str = end_date.isoformat().replace("+00:00", "Z")

        entries = self.api_request('GET', f'/me/time_entries?start_date={start_str}&end_date={end_str}')

        if not entries:
            print("ℹ No entries in the past 7 days")
            return

        print("\n=== WEEKLY SUMMARY (Last 7 Days) ===")
        
        # Organize by project
        project_times = {}
        tag_times = {}
        daily_times = {}
        total_duration = 0
        total_billable = 0

        for entry in entries:
            duration = entry.get('duration', 0)
            if duration > 0:
                total_duration += duration
                
                # By project
                project_name = self._get_project_name(entry.get('project_id'))
                project_times[project_name] = project_times.get(project_name, 0) + duration
                
                # By tag
                tags = entry.get('tags', [])
                for tag in tags:
                    tag_times[tag] = tag_times.get(tag, 0) + duration
                
                # By day
                start = entry.get('start', '')
                if start:
                    day = start[:10]  # YYYY-MM-DD
                    daily_times[day] = daily_times.get(day, 0) + duration
                
                # Billable tracking
                if entry.get('billable', False):
                    total_billable += duration

        # Display project breakdown
        print("\n📊 By Project:")
        for project, duration in sorted(project_times.items(), key=lambda x: -x[1]):
            hours = duration // 3600
            mins = (duration % 3600) // 60
            print(f"  {project}: {hours}h {mins}m")

        # Display tag breakdown
        if tag_times:
            print("\n🏷️  By Tag:")
            for tag, duration in sorted(tag_times.items(), key=lambda x: -x[1]):
                hours = duration // 3600
                mins = (duration % 3600) // 60
                print(f"  {tag}: {hours}h {mins}m")

        # Display daily breakdown
        print("\n📅 By Day:")
        for day in sorted(daily_times.keys(), reverse=True):
            duration = daily_times[day]
            hours = duration // 3600
            mins = (duration % 3600) // 60
            print(f"  {day}: {hours}h {mins}m")

        # Totals
        total_hours = total_duration // 3600
        total_mins = (total_duration % 3600) // 60
        billable_hours = total_billable // 3600
        billable_mins = (total_billable % 3600) // 60
        
        print(f"\n📈 Total Time: {total_hours}h {total_mins}m")
        if total_billable > 0:
            print(f"💰 Billable Time: {billable_hours}h {billable_mins}m")

    def edit_entry(self):
        """Edit a time entry"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Get recent entries
        start_date = (datetime.now(timezone.utc) - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', 'Z')
        end_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entries = self.api_request('GET', f'/me/time_entries?start_date={start_date}&end_date={end_date}')

        if not entries:
            print("ℹ No recent entries to edit")
            return

        print("\n=== SELECT ENTRY TO EDIT ===")
        valid_entries = [e for e in reversed(entries) if e.get('duration', 0) > 0][:10]  # Last 10 entries
        
        for idx, entry in enumerate(valid_entries, 1):
            description = entry.get('description', 'Untitled')
            project = self._get_project_name(entry.get('project_id'))
            duration = entry.get('duration', 0)
            minutes = duration // 60
            start = entry.get('start', '')[:10]  # Date only
            print(f"{idx}. {description} → {project} ({minutes} min) [{start}]")

        try:
            choice = int(input("\nSelect entry number (0 to cancel): "))
            if choice == 0:
                return
            if not (1 <= choice <= len(valid_entries)):
                print("✗ Invalid selection")
                return

            entry = valid_entries[choice - 1]
            entry_id = entry['id']

            # Show edit options
            print("\n=== WHAT TO EDIT? ===")
            print("1. Description")
            print("2. Project")
            print("3. Tags")
            print("4. Mark as Billable/Non-billable")
            
            edit_choice = input("\nSelect what to edit: ").strip()

            update_data = {}

            if edit_choice == '1':
                new_desc = input("New description: ").strip()
                if new_desc:
                    update_data['description'] = new_desc

            elif edit_choice == '2':
                projects = self.list_projects(return_data=True)
                if projects:
                    print("\n=== YOUR PROJECTS ===")
                    for idx, project in enumerate(projects, 1):
                        active = "✓" if project.get('active', True) else "✗"
                        print(f"{idx}. {project['name']} [{active}]")
                    print("P. Create New Project  |  0. No Project")

                    proj_choice = input("\nSelect project (number, name, P, or 0): ").strip()

                    if proj_choice == '0':
                        update_data['project_id'] = None
                    elif proj_choice.lower() == 'p':
                        new_project_id, _ = self._quick_create_project()
                        if new_project_id:
                            update_data['project_id'] = new_project_id
                    else:
                        selected = self._fuzzy_select(projects, "")
                        if selected:
                            update_data['project_id'] = selected['id']
                        else:
                            print("Invalid selection")
                            return
                else:
                    # No projects exist, offer to create one
                    print("\nℹ No projects found.")
                    create_new = input("Create a new project? (y/n) [n]: ").strip().lower()
                    if create_new in ['y', 'yes']:
                        new_project_id, _ = self._quick_create_project()
                        if new_project_id:
                            update_data['project_id'] = new_project_id

            elif edit_choice == '3':
                tags = self.list_tags(return_data=True)
                if tags:
                    print("\n=== YOUR TAGS ===")
                    for idx, tag in enumerate(tags, 1):
                        print(f"{idx}. {tag['name']}")
                    print("T. Create New Tag  |  0. No Tags")

                    tag_input = input("\nEnter tags (numbers, names, T for new, comma-separated): ").strip()

                    if tag_input == '0':
                        update_data['tag_ids'] = []
                    else:
                        tag_ids = []
                        for item in tag_input.split(','):
                            item = item.strip()
                            if item.lower() == 't':
                                new_tag_id = self._quick_create_tag()
                                if new_tag_id:
                                    tag_ids.append(new_tag_id)
                                    tags = self.cached_tags
                            else:
                                try:
                                    choice_num = int(item)
                                    if 1 <= choice_num <= len(tags):
                                        tag_ids.append(tags[choice_num - 1]['id'])
                                        continue
                                except ValueError:
                                    pass
                                choice_lower = item.lower()
                                matches = [t for t in tags if choice_lower in t.get('name', '').lower()]
                                if len(matches) == 1:
                                    tag_ids.append(matches[0]['id'])
                                elif len(matches) > 1:
                                    print(f"  ⚠ Ambiguous tag '{item}' — {len(matches)} matches, skipping")
                        
                        if tag_ids:
                            update_data['tag_ids'] = tag_ids
                        else:
                            print("✗ No valid tags selected")
                            return
                else:
                    # No tags exist, offer to create one
                    print("\nℹ No tags found.")
                    create_new = input("Create a new tag? (y/n) [n]: ").strip().lower()
                    if create_new in ['y', 'yes']:
                        new_tag_id = self._quick_create_tag()
                        if new_tag_id:
                            update_data['tag_ids'] = [new_tag_id]

            elif edit_choice == '4':
                billable = input("Billable? (y/n): ").strip().lower() == 'y'
                update_data['billable'] = billable

            else:
                print("✗ Invalid option")
                return

            if not update_data:
                print("✗ No changes made")
                return

            # Keep existing required fields
            update_data['start'] = entry['start']
            update_data['duration'] = entry['duration']
            update_data['workspace_id'] = self.workspace_id

            result = self.api_request('PUT', f'/workspaces/{self.workspace_id}/time_entries/{entry_id}', update_data)

            if result:
                print(f"✓ Entry updated successfully")
                self.log(f"(Edit): Updated entry #{entry_id}")
            else:
                print("✗ Failed to update entry")

        except ValueError:
            print("✗ Please enter a valid number")
        except Exception as e:
            print(f"✗ Error: {e}")

    def delete_entry(self):
        """Delete a time entry"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Get recent entries
        from datetime import timedelta
        start_date = (datetime.now(timezone.utc) - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', 'Z')
        end_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entries = self.api_request('GET', f'/me/time_entries?start_date={start_date}&end_date={end_date}')

        if not entries:
            print("ℹ No recent entries to delete")
            return

        print("\n=== SELECT ENTRY TO DELETE ===")
        valid_entries = [e for e in reversed(entries) if e.get('duration', 0) > 0][:10]
        
        for idx, entry in enumerate(valid_entries, 1):
            description = entry.get('description', 'Untitled')
            project = self._get_project_name(entry.get('project_id'))
            duration = entry.get('duration', 0)
            minutes = duration // 60
            start = entry.get('start', '')[:10]
            print(f"{idx}. {description} → {project} ({minutes} min) [{start}]")

        try:
            choice = int(input("\nSelect entry number to delete (0 to cancel): "))
            if choice == 0:
                return
            if not (1 <= choice <= len(valid_entries)):
                print("✗ Invalid selection")
                return

            entry = valid_entries[choice - 1]
            entry_id = entry['id']
            description = entry.get('description', 'Untitled')

            confirm = input(f"⚠️  Delete '{description}'? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Cancelled")
                return

            result = self.api_request('DELETE', f'/workspaces/{self.workspace_id}/time_entries/{entry_id}')

            if result is not None:  # DELETE returns empty response on success
                print(f"✓ Entry deleted: {description}")
                self.log(f"(Delete): {description}")
            else:
                print("✗ Failed to delete entry")

        except ValueError:
            print("✗ Please enter a valid number")

    def resume_last(self):
        """Resume the last stopped timer"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Check if there's already a running timer
        current = self.api_request('GET', f'/me/time_entries/current')
        if current and current.get('id'):
            print("✗ Timer is already running. Stop it first.")
            return

        # Get the most recent stopped entry
        entries = self.api_request('GET', '/me/time_entries')
        
        if not entries:
            print("ℹ No previous entries to resume")
            return

        # Find the last stopped entry
        last_entry = None
        for entry in reversed(entries):
            if entry.get('duration', 0) > 0:  # Stopped entry
                last_entry = entry
                break

        if not last_entry:
            print("ℹ No previous entries to resume")
            return

        # Create new entry with same details
        description = last_entry.get('description', 'Untitled')
        project_id = last_entry.get('project_id')
        tag_ids = last_entry.get('tag_ids', [])
        billable = last_entry.get('billable', False)

        data = {
            "description": description,
            "workspace_id": self.workspace_id,
            "duration": -1,
            "start": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "billable": billable,
            "created_with": "toggl-cli"
        }

        if project_id:
            data["project_id"] = project_id

        if tag_ids:
            data["tag_ids"] = tag_ids

        result = self.api_request('POST', f'/workspaces/{self.workspace_id}/time_entries', data)

        if result:
            project_name = self._get_project_name(last_entry.get('project_id'))
            project_str = f" → {project_name}" if last_entry.get('project_id') else ""
            print(f"✓ Resumed: {description}{project_str}")
            self.log(f"(Resume): {description}{project_str}")
        else:
            print("✗ Failed to resume timer")

    def search_entries(self):
        """Search time entries"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        print("\n=== SEARCH ENTRIES ===")
        print("1. Search by description")
        print("2. Search by project")
        print("3. Search by tag")
        print("4. Search by date range")
        
        choice = input("\nSelect search type: ").strip()

        # Get entries from last 30 days
        from datetime import timedelta
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', 'Z')
        end_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entries = self.api_request('GET', f'/me/time_entries?start_date={start_date}&end_date={end_date}')

        if not entries:
            print("ℹ No entries found")
            return

        filtered = []

        if choice == '1':
            keyword = input("Enter description keyword: ").strip().lower()
            filtered = [e for e in entries if keyword in e.get('description', '').lower() and e.get('duration', 0) > 0]

        elif choice == '2':
            projects = self.list_projects(return_data=True)
            if not projects:
                return
            print("\n=== YOUR PROJECTS ===")
            for idx, project in enumerate(projects, 1):
                active = "✓" if project.get('active', True) else "✗"
                print(f"{idx}. {project['name']} [{active}]")
            selected = self._fuzzy_select(projects, "\nSelect project: ")
            if selected:
                project_id = selected['id']
                filtered = [e for e in entries if e.get('project_id') == project_id and e.get('duration', 0) > 0]
            else:
                print("✗ No project selected")
                return

        elif choice == '3':
            tags = self.list_tags(return_data=True)
            if not tags:
                return
            print("\n=== YOUR TAGS ===")
            for idx, tag in enumerate(tags, 1):
                print(f"{idx}. {tag['name']}")
            selected = self._fuzzy_select(tags, "\nSelect tag: ")
            if selected:
                tag_id = selected['id']
                filtered = [e for e in entries if tag_id in e.get('tag_ids', []) and e.get('duration', 0) > 0]
            else:
                print("✗ No tag selected")
                return

        elif choice == '4':
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                filtered = [e for e in entries if e.get('start', '').startswith(date_str) and e.get('duration', 0) > 0]
            except:
                print("✗ Invalid date format")
                return

        else:
            print("✗ Invalid option")
            return

        if not filtered:
            print("\nℹ No matching entries found")
            return

        print(f"\n=== FOUND {len(filtered)} ENTRIES ===")
        total_duration = 0
        
        for entry in reversed(filtered):
            description = entry.get('description', 'Untitled')
            project = self._get_project_name(entry.get('project_id'))
            duration = entry.get('duration', 0)
            minutes = duration // 60
            total_duration += duration
            date = entry.get('start', '')[:10]
            print(f"• {description} → {project} ({minutes} min) [{date}]")

        total_hours = total_duration // 3600
        total_mins = (total_duration % 3600) // 60
        print(f"\nTotal: {total_hours}h {total_mins}m")

    def list_tasks(self):
        """List all tasks from projects user participates in"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Check if we have cached tasks
        if self.cached_tasks:
            print("\n⚡ Using cached tasks data...")
            tasks = self.cached_tasks
        else:
            print("\n⏳ Fetching tasks from Toggl...")
            tasks = self.api_request('GET', '/me/tasks')
            
            if tasks:
                # Cache the tasks
                self.cached_tasks = tasks
                self.save_config(silent=True)
                print("✓ Tasks cached for future use")
        
        if not tasks:
            print("ℹ No tasks found")
            return

        print("\n=== YOUR TASKS ===")
        # Group tasks by project
        tasks_by_project = {}
        for task in tasks:
            project_id = task.get('project_id')
            project_name = self._get_project_name(project_id)
            if project_name not in tasks_by_project:
                tasks_by_project[project_name] = []
            tasks_by_project[project_name].append(task)
        
        for project_name, project_tasks in sorted(tasks_by_project.items()):
            print(f"\n📁 {project_name}:")
            for task in project_tasks:
                active = "✓" if task.get('active', True) else "✗"
                estimated = f" (est: {task.get('estimated_seconds', 0) // 3600}h)" if task.get('estimated_seconds') else ""
                print(f"  • {task['name']} [{active}]{estimated}")
        
        print(f"\n✓ Total tasks: {len(tasks)}")
        print("💡 Tip: Use option 7 in Settings to refresh cache")

    def list_clients(self):
        """List all clients"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        # Check if we have cached clients
        if self.cached_clients:
            print("\n⚡ Using cached clients data...")
            clients = self.cached_clients
        else:
            print("\n⏳ Fetching clients from Toggl...")
            clients = self.api_request('GET', '/me/clients')
            
            if clients:
                # Cache the clients
                self.cached_clients = clients
                self.save_config(silent=True)
                print("✓ Clients cached for future use")
        
        if not clients:
            print("ℹ No clients found")
            return

        print("\n=== YOUR CLIENTS ===")
        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client['name']}")
        
        print(f"\n✓ Total clients: {len(clients)}")
        self.log(f"(List): {len(clients)} clients")
        print("💡 Tip: Use option 7 in Settings to refresh cache")

    def check_api_quota(self):
        """Display API quota status"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        print("\n⏳ Checking API quota...")
        quota_data = self.api_request('GET', '/me/quota')
        
        if not quota_data:
            print("✗ Could not fetch API quota information")
            return

        # Use cached organizations if available
        if self.cached_organizations:
            print("⚡ Using cached organizations data...")
            orgs = self.cached_organizations
        else:
            print("⏳ Fetching organizations...")
            orgs = self.api_request('GET', '/me/organizations')
            
            if orgs:
                # Cache the organizations
                self.cached_organizations = orgs
                self.save_config(silent=True)
        
        # Create a mapping of organization_id to name
        org_names = {}
        if orgs:
            for org in orgs:
                org_id = org.get('id')
                org_name = org.get('name', 'Unknown')
                if org_id:
                    org_names[org_id] = org_name

        print("\n=== API QUOTA STATUS ===")
        
        # The API returns quota info per organization
        if isinstance(quota_data, list):
            for quota_item in quota_data:
                org_id = quota_item.get('organization_id')
                
                # Determine the display name
                if org_id is None:
                    display_name = "User Specific Requests Quota"
                elif org_id in org_names:
                    display_name = org_names[org_id]
                else:
                    display_name = f"Organization ID: {org_id}"
                
                # Get quota values
                remaining = quota_item.get('remaining', 0)
                total = quota_item.get('total', 0)
                used = total - remaining
                resets_in_secs = quota_item.get('resets_in_secs', 0)
                
                # Display quota information
                print(f"\n📊 {display_name}")
                print(f"   Used: {used} / {total} requests")
                print(f"   Remaining: {remaining}")
                
                # Convert reset time to human-readable format
                if resets_in_secs > 0:
                    hours = resets_in_secs // 3600
                    minutes = (resets_in_secs % 3600) // 60
                    seconds = resets_in_secs % 60
                    
                    if hours > 0:
                        reset_str = f"{hours}h {minutes}m"
                    elif minutes > 0:
                        reset_str = f"{minutes}m {seconds}s"
                    else:
                        reset_str = f"{seconds}s"
                    
                    print(f"   Resets in: {reset_str}")
                
                # Warning if low
                if remaining < 5:
                    print("   ⚠️  Warning: Low quota remaining!")
        else:
            # Handle non-list response
            print("\n📊 Quota Information:")
            if isinstance(quota_data, dict):
                for key, value in quota_data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {quota_data}")
        
        self.log("(Check): API quota")

    def list_projects_paginated(self):
        """List projects with pagination support (better for large project lists)"""
        if not self.workspace_id:
            print("✗ Please login first")
            return

        print("\n⏳ Fetching projects (paginated)...")
        
        # Start with first page
        page = 1
        per_page = 50
        all_projects = []
        
        while True:
            endpoint = f'/me/projects/paginated?page={page}&per_page={per_page}'
            response = self.api_request('GET', endpoint)
            
            if not response:
                break
            
            # The paginated endpoint returns projects in a different format
            projects = response if isinstance(response, list) else response.get('data', [])
            
            if not projects:
                break
            
            all_projects.extend(projects)
            
            # Check if there are more pages
            if len(projects) < per_page:
                break
            
            page += 1
        
        if not all_projects:
            print("ℹ No projects found")
            return

        print("\n=== YOUR PROJECTS (Paginated) ===")
        for idx, project in enumerate(all_projects, 1):
            active = "✓" if project.get('active', True) else "✗"
            client_name = f" (Client: {project.get('client_name', 'None')})" if project.get('client_name') else ""
            print(f"{idx}. {project['name']} [{active}]{client_name}")
        
        print(f"\n✓ Total projects: {len(all_projects)} (loaded across {page} page(s))")
        
        # Update cache
        self.cached_projects = all_projects
        self.save_config(silent=True)
        print("✓ Cache updated")

    def update_user_profile(self):
        """Update user profile settings"""
        if not self.api_token:
            print("✗ Please login first")
            return

        print("\n=== UPDATE USER PROFILE ===")
        print("Leave blank to keep current value\n")
        
        # Get current user data
        current_user = self.api_request('GET', '/me')
        if not current_user:
            print("✗ Could not fetch current user data")
            return
        
        print(f"Current name: {current_user.get('fullname', 'N/A')}")
        print(f"Current email: {current_user.get('email', 'N/A')}")
        print(f"Current timezone: {current_user.get('timezone', 'N/A')}")
        print(f"Current week start: {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][current_user.get('beginning_of_week', 0)]}")
        
        print("\n=== WHAT TO UPDATE? ===")
        print("  1. Full Name")
        print("  2. Email")
        print("  3. Timezone")
        print("  4. Week Start Day")
        print("  5. Default Workspace")
        print("  0. Cancel")
        
        choice = input("\nSelect option: ").strip()
        
        update_data = {}
        
        if choice == '1':
            new_name = input("New full name: ").strip()
            if new_name:
                update_data['fullname'] = new_name
        
        elif choice == '2':
            new_email = input("New email: ").strip()
            if new_email:
                update_data['email'] = new_email
                print("⚠️  Note: You may need to verify the new email")
        
        elif choice == '3':
            print("\nCommon timezones:")
            print("  - America/New_York")
            print("  - America/Los_Angeles")
            print("  - Europe/London")
            print("  - Europe/Paris")
            print("  - Asia/Tokyo")
            print("  - Australia/Sydney")
            new_tz = input("\nNew timezone: ").strip()
            if new_tz:
                update_data['timezone'] = new_tz
        
        elif choice == '4':
            print("\n0. Sunday")
            print("1. Monday")
            print("2. Tuesday")
            print("3. Wednesday")
            print("4. Thursday")
            print("5. Friday")
            print("6. Saturday")
            day_choice = input("\nSelect day (0-6): ").strip()
            try:
                day_num = int(day_choice)
                if 0 <= day_num <= 6:
                    update_data['beginning_of_week'] = day_num
                else:
                    print("✗ Invalid day number")
                    return
            except ValueError:
                print("✗ Please enter a number")
                return
        
        elif choice == '5':
            # Get workspaces
            workspaces = self.api_request('GET', '/me/workspaces')
            if workspaces:
                print("\n=== SELECT DEFAULT WORKSPACE ===")
                for idx, ws in enumerate(workspaces, 1):
                    current = " (current)" if ws['id'] == current_user.get('default_workspace_id') else ""
                    print(f"{idx}. {ws['name']}{current}")
                
                try:
                    ws_choice = int(input("\nSelect workspace number: "))
                    if 1 <= ws_choice <= len(workspaces):
                        update_data['default_workspace_id'] = workspaces[ws_choice - 1]['id']
                    else:
                        print("✗ Invalid selection")
                        return
                except ValueError:
                    print("✗ Please enter a valid number")
                    return
        
        elif choice == '0':
            return
        
        else:
            print("✗ Invalid option")
            return
        
        if not update_data:
            print("ℹ No changes made")
            return
        
        # Update profile
        result = self.api_request('PUT', '/me', update_data)
        
        if result:
            print("✓ Profile updated successfully")
            self.log(f"(Update Profile): {', '.join(update_data.keys())}")
            # Update cached user data
            self.user_data = result
        else:
            print("✗ Failed to update profile")

    def view_organizations(self):
        """View organizations user is part of"""
        if not self.api_token:
            print("✗ Please login first")
            return

        # Check if we have cached organizations
        if self.cached_organizations:
            print("\n⚡ Using cached organizations data...")
            orgs = self.cached_organizations
        else:
            print("\n⏳ Fetching organizations...")
            orgs = self.api_request('GET', '/me/organizations')
            
            if orgs:
                # Cache the organizations
                self.cached_organizations = orgs
                self.save_config(silent=True)
                print("✓ Organizations cached for future use")
        
        if not orgs:
            print("ℹ You are not part of any organizations")
            return

        # Check if we have cached workspaces
        if self.cached_workspaces:
            print("⚡ Using cached workspaces data...")
            workspaces = self.cached_workspaces
        else:
            print("⏳ Fetching workspaces...")
            workspaces = self.api_request('GET', '/me/workspaces')
            
            if workspaces:
                # Cache the workspaces
                self.cached_workspaces = workspaces
                self.save_config(silent=True)
                print("✓ Workspaces cached for future use")
        
        # Count workspaces per organization
        org_workspace_count = {}
        if workspaces:
            for ws in workspaces:
                org_id = ws.get('organization_id')
                if org_id:
                    org_workspace_count[org_id] = org_workspace_count.get(org_id, 0) + 1

        print("\n=== YOUR ORGANIZATIONS ===")
        for idx, org in enumerate(orgs, 1):
            admin = " (Admin)" if org.get('admin', False) else ""
            owner = " (Owner)" if org.get('owner', False) else ""
            org_id = org.get('id')
            
            print(f"{idx}. {org.get('name', 'Unknown')}{admin}{owner}")
            print(f"   ID: {org_id}")
            
            # Use counted workspaces or try API fields
            workspace_count = org_workspace_count.get(org_id)
            if workspace_count is None:
                workspace_count = (org.get('workspace_count') or 
                                 org.get('workspaces_count') or 
                                 org.get('workspaces') or
                                 len(org.get('workspace_ids', [])) if org.get('workspace_ids') else None)
            
            if workspace_count is not None:
                print(f"   Workspaces: {workspace_count}")
            
            # Show pricing plan if available
            if org.get('pricing_plan_id'):
                print(f"   Plan ID: {org.get('pricing_plan_id')}")
            
            print()
        
        print(f"✓ Total organizations: {len(orgs)}")
        self.log(f"(List): {len(orgs)} organizations")
        print("💡 Tip: Use option 7 in Settings to refresh cache")

    def refresh_cache(self):
        """Refresh cached data"""
        print("\n" + "="*60)
        print("                   🔄 REFRESH CACHE")
        print("="*60)
        print("Current cache status:")
        print(f"  Organizations: {'✓ Cached' if self.cached_organizations else '✗ Empty'}")
        print(f"  Clients: {'✓ Cached' if self.cached_clients else '✗ Empty'}")
        print(f"  Tasks: {'✓ Cached' if self.cached_tasks else '✗ Empty'}")
        print(f"  Workspaces: {'✓ Cached' if self.cached_workspaces else '✗ Empty'}")
        print(f"  Projects: {'✓ Cached' if self.cached_projects else '✗ Empty'}")
        print(f"  Tags: {'✓ Cached' if self.cached_tags else '✗ Empty'}")
        
        print("\n" + "="*60)
        print("                   🔄 REFRESH CACHE")
        print("="*60)
        print("  1. Refresh All Cache       [6🔄]")
        print("  2. Refresh Organizations   [1🔄]")
        print("  3. Refresh Clients         [1🔄]")
        print("  4. Refresh Tasks           [1🔄]")
        print("  5. Refresh Workspaces      [1🔄]")
        print("  6. Refresh Projects        [1🔄]")
        print("  7. Refresh Tags            [1🔄]")
        print("  8. Clear All Cache         [0⚡]")
        print("  0. Cancel")
        print("\n  Legend: 🔄 Refresh (API calls)  ⚡ No calls")
        print("="*60)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            # Refresh all
            print("\n⏳ Refreshing all cached data...")
            self.cached_organizations = []
            self.cached_clients = []
            self.cached_tasks = []
            self.cached_workspaces = []
            self.cached_projects = []
            self.cached_tags = []
            
            # Fetch fresh data
            orgs = self.api_request('GET', '/me/organizations')
            if orgs:
                self.cached_organizations = orgs
            
            clients = self.api_request('GET', '/me/clients')
            if clients:
                self.cached_clients = clients
            
            tasks = self.api_request('GET', '/me/tasks')
            if tasks:
                self.cached_tasks = tasks
            
            workspaces = self.api_request('GET', '/me/workspaces')
            if workspaces:
                self.cached_workspaces = workspaces
            
            projects = self.api_request('GET', '/me/projects')
            if projects:
                self.cached_projects = projects
            
            tags = self.api_request('GET', '/me/tags')
            if tags:
                self.cached_tags = tags
            
            self.save_config(silent=True)
            print("✓ All cache refreshed successfully")
            self.log("(Refresh): All cache")
            
        elif choice == '2':
            print("\n⏳ Refreshing organizations...")
            self.cached_organizations = []
            orgs = self.api_request('GET', '/me/organizations')
            if orgs:
                self.cached_organizations = orgs
                self.save_config(silent=True)
                print("✓ Organizations cache refreshed")
                self.log("(Refresh): Organizations cache")
            
        elif choice == '3':
            print("\n⏳ Refreshing clients...")
            self.cached_clients = []
            clients = self.api_request('GET', '/me/clients')
            if clients:
                self.cached_clients = clients
                self.save_config(silent=True)
                print("✓ Clients cache refreshed")
                self.log("(Refresh): Clients cache")
            
        elif choice == '4':
            print("\n⏳ Refreshing tasks...")
            self.cached_tasks = []
            tasks = self.api_request('GET', '/me/tasks')
            if tasks:
                self.cached_tasks = tasks
                self.save_config(silent=True)
                print("✓ Tasks cache refreshed")
                self.log("(Refresh): Tasks cache")
            
        elif choice == '5':
            print("\n⏳ Refreshing workspaces...")
            self.cached_workspaces = []
            workspaces = self.api_request('GET', '/me/workspaces')
            if workspaces:
                self.cached_workspaces = workspaces
                self.save_config(silent=True)
                print("✓ Workspaces cache refreshed")
                self.log("(Refresh): Workspaces cache")
            
        elif choice == '6':
            print("\n⏳ Refreshing projects...")
            self.cached_projects = []
            projects = self.api_request('GET', '/me/projects')
            if projects:
                self.cached_projects = projects
                self.save_config(silent=True)
                print("✓ Projects cache refreshed")
                self.log("(Refresh): Projects cache")
            
        elif choice == '7':
            print("\n⏳ Refreshing tags...")
            self.cached_tags = []
            tags = self.api_request('GET', '/me/tags')
            if tags:
                self.cached_tags = tags
                self.save_config(silent=True)
                print("✓ Tags cache refreshed")
                self.log("(Refresh): Tags cache")
            
        elif choice == '8':
            # Clear all cache without refetching
            confirm = input("\n⚠️  Clear all cache? This will not refetch data. (yes/no): ").strip().lower()
            if confirm == 'yes':
                self.cached_organizations = []
                self.cached_clients = []
                self.cached_tasks = []
                self.cached_workspaces = []
                self.cached_projects = []
                self.cached_tags = []
                self.save_config(silent=True)
                print("✓ All cache cleared")
                self.log("(Clear): All cache")
            else:
                print("✗ Cancelled")
        
        elif choice == '0':
            return
        
        else:
            print("✗ Invalid option")

    def toggl_settings_menu(self):
        """Display and handle Toggl Settings submenu"""
        while True:
            print("\n" + "="*60)
            print("                   ⚙️  TOGGL SETTINGS")
            print("="*60)
            print("  1. View Organizations  [2📡 0⚡]")
            print("  2. View Clients        [1📡 0⚡]")
            print("  3. View Tasks          [1📡 0⚡]")
            print("  4. List Projects       [1📡+ 0⚡]")
            print("  5. Update User Profile [2-3📡]")
            print("  6. Check API Quota     [2📡 1⚡]")
            print("  7. Refresh Cache       [🔄 see submenu]")
            print("  0. Back to Main Menu")
            print("\n  Legend: 📡 API calls  ⚡ Cached  🔄 Refresh")
            print("="*60)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.view_organizations()
            elif choice == '2':
                self.list_clients()
            elif choice == '3':
                self.list_tasks()
            elif choice == '4':
                self.list_projects_paginated()
            elif choice == '5':
                self.update_user_profile()
            elif choice == '6':
                self.check_api_quota()
            elif choice == '7':
                self.refresh_cache()
            elif choice == '0':
                break
            else:
                print("✗ Invalid option. Please try again.")

    def open_reports(self):
        """Open Toggl Reports in default browser"""
        reports_url = "https://track.toggl.com/reports/"
        try:
            webbrowser.open(reports_url)
            print(f"✓ Opening Toggl Reports in browser...")
            self.log("(Open): Toggl Reports in browser")
        except Exception as e:
            print(f"✗ Failed to open browser: {e}")

    # CLI aliases for power users
    ALIASES = {
        'st': '2',   # Start Timer
        'sp': '3',   # Stop Timer
        'rt': '4',   # Resume Timer
        'ct': '5',   # Current Timer
        'te': '6',   # Today's Entries
        'ws': '7',   # Weekly Summary
        'se': '8',   # Search
        'quit': '0',
        'exit': '0',
    }

    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("                   ⏱  TOGGL TIME TRACKER")
        print("="*60)
        print("  ⚡ ACTIONS                 │  📊 REPORTS & MANAGEMENT")
        print("─"*29 + "┼" + "─"*30)
        print("  1. 🛠  Login / Setup        │     6. 📅 Today's Entries")
        print("  2. ▶  Start Timer  (st)    │     7. 📅 Weekly Summary (ws)")
        print("  3. ⏹  Stop Timer   (sp)    │     8. 📅 Search Entries (se)")
        print("  4. ⏯  Resume Timer (rt)    │     9. 📅 Edit Entry")
        print("  5. ⏱  Current Timer(ct)    │    10. 📅 Delete Entry")
        print("                             │    11. 📅 List Projects")
        print("  📁 CREATE | 0. Exit        │    12. 📅 List Tags")
        print("─"*29 + "┼" + "─"*30)
        print("  13. 📝 Create Project      │     O. 🌐 Open Reports (Web)")
        print("  14. 📝 Create Tag          │     S. ⚙️ Toggl Settings")
        print("="*60)

    def run(self):
        """Main application loop"""
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option: ").strip()
                choice = self.ALIASES.get(choice.lower(), choice)

                if choice == '1':
                    self.login()
                elif choice == '2':
                    self.start_timer()
                elif choice == '3':
                    self.stop_timer()
                elif choice == '4':
                    self.resume_last()
                elif choice == '5':
                    self.current_timer()
                elif choice == '6':
                    self.recent_entries()
                elif choice == '7':
                    self.weekly_summary()
                elif choice == '8':
                    self.search_entries()
                elif choice == '9':
                    self.edit_entry()
                elif choice == '10':
                    self.delete_entry()
                elif choice == '11':
                    self.list_projects()
                elif choice == '12':
                    self.list_tags()
                elif choice == '13':
                    self.create_project()
                elif choice == '14':
                    self.create_tag()
                elif choice.lower() == 'o':
                    self.open_reports()
                elif choice.lower() == 's':
                    self.toggl_settings_menu()
                elif choice == '0':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("✗ Invalid option. Please try again.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
                self.log(f"(Error): {e}")


if __name__ == "__main__":
    cli = TogglCLI()
    cli.run()
