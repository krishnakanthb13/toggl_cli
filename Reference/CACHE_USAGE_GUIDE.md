# Cache Usage Guide - Toggl CLI

## 🔍 **When Does the CLI Use Cache?**

### **Automatic Cache Usage:**

The CLI automatically uses cached data in these scenarios:

1. **Second Use Onwards**
   - First time you use a feature → Fetches from API and caches
   - Second time onwards → Uses cached data (instant, no API call)

2. **Across Sessions**
   - Cache persists even after closing the app
   - When you reopen the app, cached data is still there
   - No need to refetch every time you start the app

3. **Which Features Use Cache:**
   - ✅ **Option 1**: View Organizations (+ workspaces)
   - ✅ **Option 2**: View Clients
   - ✅ **Option 3**: View Tasks
   - ✅ **Option 4**: List Projects (Paginated)
   - ❌ **Option 5**: Update Profile (always fresh)
   - ⚡ **Option 6**: Check API Quota (quota fresh, orgs cached)

---

## 🔄 **How to Refresh Cache**

### **Option 7: Refresh Cache** (in Settings Menu)

Access: **Main Menu → S (Settings) → 7 (Refresh Cache)**

### **Refresh Options:**

```
=== REFRESH CACHE ===
Current cache status:
  Organizations: ✓ Cached
  Clients: ✓ Cached
  Tasks: ✓ Cached
  Workspaces: ✓ Cached
  Projects: ✓ Cached
  Tags: ✓ Cached

=== REFRESH OPTIONS ===
  1. Refresh All Cache
  2. Refresh Organizations
  3. Refresh Clients
  4. Refresh Tasks
  5. Refresh Workspaces
  6. Refresh Projects
  7. Refresh Tags
  8. Clear All Cache (without refetching)
  0. Cancel
```

---

## 📋 **Detailed Refresh Options**

### **1. Refresh All Cache**
- Clears ALL cached data
- Fetches fresh data for everything
- **API Calls**: 6 calls (orgs, clients, tasks, workspaces, projects, tags)
- **Use when**: You want to update everything at once

### **2-7. Refresh Individual Items**
- Clears and refetches only the selected item
- **API Calls**: 1 call per item
- **Use when**: You only need to update specific data (e.g., new client added)

### **8. Clear All Cache**
- Clears all cached data WITHOUT refetching
- **API Calls**: 0 calls
- **Use when**: You want to force fresh fetches on next use
- **Requires confirmation**: Type "yes" to confirm

---

## 💡 **When to Refresh Cache**

### **Refresh When:**

1. **New Data Added**
   - Created a new client → Refresh Clients (Option 3)
   - Created a new project → Refresh Projects (Option 6)
   - Created a new task → Refresh Tasks (Option 4)

2. **Data Changed**
   - Renamed an organization → Refresh Organizations (Option 2)
   - Updated project details → Refresh Projects (Option 6)
   - Changed workspace settings → Refresh Workspaces (Option 5)

3. **Periodic Updates**
   - Once a day/week → Refresh All Cache (Option 1)
   - Before important operations → Refresh relevant cache

4. **Troubleshooting**
   - Data looks outdated → Refresh All Cache (Option 1)
   - Missing new items → Refresh specific cache

### **Don't Need to Refresh:**
- ✅ Just viewing data you've seen before
- ✅ No changes made in Toggl web/mobile
- ✅ Cache is recent (same day)

---

## 🎯 **Cache Behavior Examples**

### **Example 1: First Time User**

```
Day 1, First Use:
  Settings → 1 (View Organizations)
  → ⏳ Fetching organizations... (API call)
  → ⏳ Fetching workspaces... (API call)
  → ✓ Organizations cached
  → ✓ Workspaces cached

Day 1, Second Use:
  Settings → 1 (View Organizations)
  → ⚡ Using cached organizations data... (NO API call)
  → ⚡ Using cached workspaces data... (NO API call)

Day 2, After Restart:
  Settings → 1 (View Organizations)
  → ⚡ Using cached organizations data... (Still cached!)
  → ⚡ Using cached workspaces data... (Still cached!)
```

### **Example 2: After Adding New Client**

```
1. Add client in Toggl web interface
2. Open Toggl CLI
3. Settings → 2 (View Clients)
   → ⚡ Using cached clients data... (OLD DATA - missing new client)
4. Settings → 7 (Refresh Cache) → 3 (Refresh Clients)
   → ⏳ Refreshing clients... (API call)
   → ✓ Clients cache refreshed
5. Settings → 2 (View Clients)
   → ⚡ Using cached clients data... (NEW DATA - includes new client)
```

### **Example 3: Weekly Refresh Routine**

```
Every Monday Morning:
  Settings → 7 (Refresh Cache) → 1 (Refresh All Cache)
  → Fetches fresh data for everything
  → Rest of the week uses cached data
  → Saves API quota throughout the week
```

---

## 📊 **Cache Status Indicators**

### **When Viewing Cache Status:**
```
Current cache status:
  Organizations: ✓ Cached    ← Has data
  Clients: ✗ Empty           ← No data (will fetch on first use)
  Tasks: ✓ Cached
  Workspaces: ✓ Cached
  Projects: ✓ Cached
  Tags: ✓ Cached
```

### **When Using Features:**
```
⚡ Using cached [data] data...    ← Using cache (fast, no API call)
⏳ Fetching [data] from Toggl...  ← Fetching from API (slower, uses quota)
✓ [Data] cached for future use   ← Data now cached for next time
```

---

## 🎓 **Best Practices**

### **For Regular Users:**
1. Let cache work automatically
2. Refresh weekly or when you add new data
3. Use "Refresh All Cache" (Option 1) for simplicity

### **For Power Users:**
1. Refresh only what changed (Options 2-7)
2. Monitor API quota (Settings → 6)
3. Refresh before important operations

### **For Developers:**
1. Clear cache when testing (Option 8)
2. Refresh specific items when debugging
3. Check `toggl_config.json` for cache contents

---

## 📁 **Cache Storage**

### **Location:**
`toggl_config.json` (same folder as the CLI)

### **Contents:**
```json
{
  "api_token": "...",
  "workspace_id": 123456,
  "cached_projects": [...],
  "cached_tags": [...],
  "cached_organizations": [...],
  "cached_clients": [...],
  "cached_tasks": [...],
  "cached_workspaces": [...]
}
```

### **Manual Cache Management:**
- **View cache**: Open `toggl_config.json` in text editor
- **Clear cache**: Delete `toggl_config.json` (will recreate on next login)
- **Backup cache**: Copy `toggl_config.json` to safe location

---

## ⚠️ **Important Notes**

1. **Cache Never Expires**
   - Cache persists until manually refreshed
   - No automatic expiration or age limit
   - You control when to refresh

2. **API Quota Savings**
   - First use: Uses API quota
   - Cached use: No API quota used
   - Refresh: Uses API quota

3. **Data Accuracy**
   - Cache shows data from last fetch
   - May be outdated if changes made elsewhere
   - Refresh to get latest data

4. **Cross-Device**
   - Cache is local to each device
   - Not synced across devices
   - Each device has its own cache

---

## 🚀 **Quick Reference**

| Action | Command |
|--------|---------|
| View cache status | Settings → 7 → (see status) |
| Refresh everything | Settings → 7 → 1 |
| Refresh organizations | Settings → 7 → 2 |
| Refresh clients | Settings → 7 → 3 |
| Refresh tasks | Settings → 7 → 4 |
| Refresh workspaces | Settings → 7 → 5 |
| Refresh projects | Settings → 7 → 6 |
| Refresh tags | Settings → 7 → 7 |
| Clear all cache | Settings → 7 → 8 → yes |

---

**Remember:** Cache is your friend! It saves API quota and makes the CLI faster. Just refresh when you need fresh data! 🎉
