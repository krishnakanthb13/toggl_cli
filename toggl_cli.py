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
            except Exception as e:
                self.log(f"Error loading config: {e}")

    def _start_session_log(self):
        """Add a blank line to separate sessions in the log file"""
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write("\n")
        except Exception:
            pass  # Silently ignore if log file can't be written

    def save_config(self, silent=False):
        """Save configuration and cached data to file"""
        try:
            config = {
                'api_token': self.api_token,
                'workspace_id': self.workspace_id,
                'cached_projects': self.cached_projects,
                'cached_tags': self.cached_tags
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            if not silent:
                print(f"✓ Configuration saved to {CONFIG_FILE}")
        except Exception as e:
            print(f"✗ Error saving config: {e}")

    def log(self, message):
        """Append log entry to toggl_cli_logs.txt"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        """Make API request to Toggl"""
        if not self.api_token:
            print("✗ Error: Not logged in. Please login first (Option 1)")
            return None

        url = f"{API_BASE}{endpoint}"
        auth = b64encode(f"{self.api_token}:api_token".encode()).decode('ascii')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth}'
        }

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return None

            if response.status_code in [200, 201]:
                return response.json()
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
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
                print("\n=== YOUR PROJECTS ===")
                for idx, project in enumerate(projects, 1):
                    active = "✓" if project.get('active', True) else "✗"
                    print(f"{idx}. {project['name']} [{active}]")
                print("P. Create New Project")
                
                choice = input("\nSelect project (number or P): ").strip()
                
                if choice.lower() == 'p':
                    # Create new project on-the-fly
                    project_id, project_name = self._quick_create_project()
                else:
                    try:
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(projects):
                            project_id = projects[choice_num - 1]['id']
                            project_name = projects[choice_num - 1]['name']
                        else:
                            print("✗ Invalid selection, no project assigned")
                    except ValueError:
                        print("✗ Invalid selection, no project assigned")
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
                
                tag_input = input("\nEnter tags (numbers, T for new, comma-separated): ").strip()
                
                # Process mixed input (e.g., "1,T,3")
                for item in tag_input.split(','):
                    item = item.strip()
                    if item.lower() == 't':
                        # Create new tag on-the-fly
                        new_tag_id = self._quick_create_tag()
                        if new_tag_id:
                            tag_ids.append(new_tag_id)
                            # Update tags list for future reference in this session
                            tags = self.cached_tags
                    else:
                        try:
                            choice_num = int(item)
                            if 1 <= choice_num <= len(tags):
                                tag_ids.append(tags[choice_num - 1]['id'])
                        except ValueError:
                            pass  # Skip invalid entries
                
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
        start_date = datetime.now().replace(hour=0, minute=0, second=0).isoformat() + "Z"
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
        start_date = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0).isoformat() + "Z"
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
                    print("P. Create New Project")
                    
                    proj_choice = input("\nSelect project (number, P for new, 0 for none): ").strip()
                    
                    if proj_choice == '0':
                        update_data['project_id'] = None
                    elif proj_choice.lower() == 'p':
                        # Create new project on-the-fly
                        new_project_id, _ = self._quick_create_project()
                        if new_project_id:
                            update_data['project_id'] = new_project_id
                    else:
                        try:
                            choice_num = int(proj_choice)
                            if 1 <= choice_num <= len(projects):
                                update_data['project_id'] = projects[choice_num - 1]['id']
                            else:
                                print("Invalid selection")
                                return
                        except ValueError:
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
                    print("T. Create New Tag")
                    
                    tag_input = input("\nEnter tags (numbers, T for new, 0 for none): ").strip()
                    
                    if tag_input == '0':
                        update_data['tag_ids'] = []
                    else:
                        tag_ids = []
                        # Process mixed input (e.g., "1,T,3")
                        for item in tag_input.split(','):
                            item = item.strip()
                            if item.lower() == 't':
                                # Create new tag on-the-fly
                                new_tag_id = self._quick_create_tag()
                                if new_tag_id:
                                    tag_ids.append(new_tag_id)
                                    tags = self.cached_tags
                            else:
                                try:
                                    choice_num = int(item)
                                    if 1 <= choice_num <= len(tags):
                                        tag_ids.append(tags[choice_num - 1]['id'])
                                except ValueError:
                                    pass  # Skip invalid entries
                        
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
        start_date = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0).isoformat() + "Z"
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
        start_date = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
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
            try:
                proj_choice = int(input("\nSelect project number: "))
                if 1 <= proj_choice <= len(projects):
                    project_id = projects[proj_choice - 1]['id']
                    filtered = [e for e in entries if e.get('project_id') == project_id and e.get('duration', 0) > 0]
            except ValueError:
                print("✗ Invalid selection")
                return

        elif choice == '3':
            tags = self.list_tags(return_data=True)
            if not tags:
                return
            print("\n=== YOUR TAGS ===")
            for idx, tag in enumerate(tags, 1):
                print(f"{idx}. {tag['name']}")
            try:
                tag_choice = int(input("\nSelect tag number: "))
                if 1 <= tag_choice <= len(tags):
                    tag_id = tags[tag_choice - 1]['id']
                    filtered = [e for e in entries if tag_id in e.get('tag_ids', []) and e.get('duration', 0) > 0]
            except ValueError:
                print("✗ Invalid selection")
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

    def open_reports(self):
        """Open Toggl Reports in default browser"""
        reports_url = "https://track.toggl.com/reports/"
        try:
            webbrowser.open(reports_url)
            print(f"✓ Opening Toggl Reports in browser...")
            self.log("(Open): Toggl Reports in browser")
        except Exception as e:
            print(f"✗ Failed to open browser: {e}")

    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("⏱  TOGGL TIME TRACKER")
        print("="*60)
        print("  ⚡ ACTIONS                 │  📊 REPORTS & MANAGEMENT")
        print("─"*29 + "┼" + "─"*30)
        print("  1. Login / Setup           │     6. Today's Entries")
        print("  2. Start Timer             │     7. Weekly Summary")
        print("  3. Stop Timer              │     8. Search Entries")
        print("  4. Resume Last Timer       │     9. Edit Entry")
        print("  5. Current Timer           │    10. Delete Entry")
        print("                             │    11. List Projects")
        print("  📁 CREATE                  │    12. List Tags")
        print("─"*29 + "┼" + "─"*30)
        print(" 13. Create Project          │  O. Open Reports (Web)")
        print(" 14. Create Tag              │  0. Exit")
        print("="*60)

    def run(self):
        """Main application loop"""
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option: ").strip()

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
