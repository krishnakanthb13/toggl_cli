# Toggl Settings - Quick Reference Guide

## 🎯 Access Settings Menu
From main menu, press: **S**

---

## 🔥 HIGH PRIORITY FEATURES

### 1️⃣ View Tasks
**What it does**: Shows all tasks from your projects  
**When to use**: Check task list, see estimated hours  
**Output**: Tasks grouped by project with status

### 2️⃣ View Clients  
**What it does**: Lists all clients in workspace  
**When to use**: See all clients, check client names  
**Output**: Numbered list of clients

### 3️⃣ Check API Quota
**What it does**: Shows API rate limit status  
**When to use**: Before bulk operations, check remaining calls  
**Output**: Requests made/remaining per organization  
**⚠️ Warning**: Shows alert if < 100 requests remaining

### 4️⃣ List Projects (Paginated)
**What it does**: Efficiently loads large project lists  
**When to use**: You have 50+ projects  
**Output**: All projects with client info, updates cache  
**Benefit**: Faster than regular project list for power users

---

## ⭐ ADDITIONAL FEATURES

### 5️⃣ Update User Profile
**What it does**: Change account settings  
**Options**:
- Full Name
- Email (requires verification)
- Timezone
- Week Start Day (Sun-Sat)
- Default Workspace

**Common Use Cases**:
- After moving to new timezone
- Changing work schedule
- Switching primary workspace

### 6️⃣ View Organizations
**What it does**: Shows all organizations you're in  
**When to use**: Check org memberships, see roles  
**Output**: Org name, role (Admin/Owner), workspace count

---

## 🎮 Navigation

```
Main Menu
    ↓
Press 'S'
    ↓
Settings Menu (Options 1-6)
    ↓
Press '0' to return
    ↓
Back to Main Menu
```

---

## 💡 Pro Tips

1. **Check Quota First**: Before doing bulk operations, check API quota (Option 3)

2. **Use Paginated Projects**: If you have many projects, use Option 4 instead of regular project list

3. **Update Timezone**: Traveling? Update timezone in Profile (Option 5 → 3)

4. **View Tasks**: See all project tasks at once (Option 1) instead of checking each project

5. **Client Overview**: Quickly see all clients (Option 2) before creating new projects

---

## 🔍 Quick Comparison

| Feature | Regular Menu | Settings Menu |
|---------|--------------|---------------|
| List Projects | Option 11 (all at once) | Option 4 (paginated, faster) |
| View Tasks | ❌ Not available | ✅ Option 1 |
| View Clients | ❌ Not available | ✅ Option 2 |
| Check Quota | ❌ Not available | ✅ Option 3 |
| Update Profile | ❌ Not available | ✅ Option 5 |
| View Orgs | ❌ Not available | ✅ Option 6 |

---

## 📊 When to Use Each Feature

### Daily Use
- **View Tasks** (1): Start of day to see what's on your plate
- **Check API Quota** (3): If you're a power user making many API calls

### Weekly Use
- **View Clients** (2): Weekly review of client work
- **View Organizations** (6): Check org memberships

### As Needed
- **Update Profile** (5): When changing settings (timezone, workspace, etc.)
- **Paginated Projects** (4): When regular project list is slow

---

## 🚨 Important Notes

- All features require login (Option 1 from main menu)
- Changes to profile are immediate
- API quota resets every hour
- Paginated projects automatically update cache
- All actions are logged to `toggl_cli_logs.txt`

---

## 🎓 Examples

### Example 1: Checking Tasks Before Starting Work
```
Main Menu → S → 1 → Review tasks → 0 → Start timer with task in mind
```

### Example 2: Monitoring API Usage
```
Main Menu → S → 3 → Check remaining quota → Plan operations accordingly
```

### Example 3: Updating Timezone After Travel
```
Main Menu → S → 5 → 3 → Enter new timezone → Confirm
```

### Example 4: Loading Many Projects Efficiently
```
Main Menu → S → 4 → View all projects paginated → Cache updated
```

---

## ❓ FAQ

**Q: Why use paginated projects instead of regular list?**  
A: Faster for 50+ projects, loads in chunks, better performance

**Q: What happens if I run out of API quota?**  
A: You'll get errors. Check quota (Option 3) and wait for hourly reset

**Q: Can I update multiple profile settings at once?**  
A: No, one at a time. Run Option 5 multiple times if needed

**Q: Do tasks show in timer start?**  
A: Not yet - this is a future enhancement. For now, view tasks separately

**Q: What's the difference between Admin and Owner?**  
A: Owner created the org, Admin has management permissions

---

## 🔗 Related Features

- **Main Menu Option 11**: List Projects (non-paginated)
- **Main Menu Option 12**: List Tags
- **Main Menu Option 1**: Login/Setup (required for all settings features)

---

**Last Updated**: 2026-01-24  
**Version**: 1.2.0 (with Settings Menu)
