# Security Audit Report - Toggl CLI

**Date of Scan**: 2026-01-25
**Scope**: `toggl_cli.py`, `toggl_cli_review.html`, `.bat` launchers.

## Summary of Findings

| Severity | Issue | Status |
| :--- | :--- | :--- |
| 🔴 **Critical** | Information Exposure via Web Server | ✅ Fixed |
| 🟡 **Warning** | Plain-text API Tokens in Configuration | Risk Acknowledged |
| 🟡 **Warning** | Sensitive Data in LocalStorage | Risk Acknowledged |
| 🟡 **Warning** | XSS Vector via Markdown Rendering | Mitigated (DOMPurify) |
| 🟢 **Passed** | Injection Prevention | No issues found |
| 🟢 **Passed** | Secrets Management (Git) | `.gitignore` properly configured |

---

## Detailed Findings

### 🔴 Critical: Information Exposure via Web Server
- **Description**: The batch files (`toggl_cli.bat` and `toggl_cli_review.bat`) start a web server that serves the entire project directory. By default, these servers listen on all network interfaces (`0.0.0.0`).
- **Impact**: Any file in the project directory, including `toggl_config.json` (which contains your Toggl API token) and `toggl_cli_logs.txt`, can be accessed by anyone on your local network.
- **Affected Files**: `toggl_cli.bat`, `toggl_cli_review.bat`
- **Recommendation**: Bind the server to `127.0.0.1` to ensure it is only accessible from your own machine.
- **Resolution**: ✅ Fixed. Batch files now bind the server to `127.0.0.1` explicitly.

### 🟡 Warning: Plain-text API Tokens in Configuration
- **Description**: `toggl_config.json` stores the Toggl API token in plain text.
- **Impact**: If your local machine is compromised, the token can be easily retrieved.
- **Mitigation**: The file is correctly excluded from version control via `.gitignore`.
- **Recommendation**: For higher security, use a system-level credential manager.

### 🟡 Warning: Sensitive Data in LocalStorage
- **Description**: The Gemini API key used for summaries is stored in the browser's `localStorage`.
- **Impact**: If a malicious script is executed on the page (XSS), it could steal the key.
- **Mitigation**: The app uses `DOMPurify` to sanitize all rendered content.

---

## Vulnerability Remediation

### 1. Fix Web Server Exposure
Modify batch files to use the `--bind` or `-a` flag:
- Python: `python -m http.server 8086 --bind 127.0.0.1`
- http-server: `http-server -a 127.0.0.1 -p 8086`

### 2. Regular Audits
- Periodically check `toggl_cli_logs.txt` for any accidental logging of sensitive info.
- Keep `DOMPurify` up to date in `toggl_cli_review.html`.
