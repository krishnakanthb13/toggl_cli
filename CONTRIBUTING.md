# Contributing to Toggl CLI

Thank you for your interest in contributing to Toggl CLI! 🎉

## Ways to Contribute

### 🐛 Report Bugs
- Check if the issue already exists
- Include steps to reproduce
- Share relevant log entries from `toggl_cli_logs.txt`

### 💡 Suggest Features
- Open an issue with `[Feature Request]` prefix
- Describe the use case
- Keep it aligned with the CLI's simplicity goals

### 🔧 Submit Code
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and create a Pull Request

## Code Guidelines

- **Keep it simple** - This is a CLI tool, not a framework
- **One feature per PR** - Easier to review
- **Test manually** - Use the testing checklist in `CODE_DOCUMENTATION.md`
- **Update docs** - If you change behavior, update README.md

## Development Setup

```bash
# Clone the repo
git clone https://github.com/krishnakanthb13/toggl-cli.git
cd toggl-cli

# Install dependency
pip install requests

# Run the CLI
python toggl_cli.py
```

## Testing Checklist

Before submitting, verify:
- [ ] Login works with valid API token
- [ ] Start/Stop timer functions correctly
- [ ] Projects and tags display properly
- [ ] On-the-fly creation (P/T) works
- [ ] Cache updates are saved
- [ ] No crashes on invalid input

## Questions?

Open an issue or reach out. Happy coding! ⏱️
