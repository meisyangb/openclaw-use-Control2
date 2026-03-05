---
name: basic-system
description: "Basic system management and monitoring skills. Use for system checks, file operations, and basic administrative tasks. NOT for complex system administration or security-sensitive operations."
homepage: https://docs.openclaw.ai/skills
metadata: { "openclaw": { "emoji": "🛠️", "requires": { "bins": ["ls", "cat", "pwd", "cd", "whoami", "df", "free", "ps", "grep"] } } }
---

# Basic System Skill

Provides fundamental system management and monitoring capabilities for everyday administrative tasks.

## When to Use

✅ **USE this skill when:**

- "Check system status"
- "What files are in this directory?"
- "Show me running processes"
- "Check disk space"
- "List users"
- "Basic system information"
- Simple file operations

## When NOT to Use

❌ **DON'T use this skill when:**

- Complex system administration → use specialized admin tools
- Security-sensitive operations → use security-focused skills
- Network configuration → use network management skills
- Database administration → use database skills
- Application deployment → use deployment skills

## Basic Commands

### System Information

```bash
# Current working directory
pwd

# Current user
whoami

# System uptime
uptime

# Disk usage
df -h

# Memory usage
free -h

# Process list
ps aux | head -20

# System load
uptime
```

### File Operations

```bash
# List files
ls -la

# List files with details
ls -lh

# List files by size (largest first)
ls -lS

# List files by date
ls -lt

# Count files
ls -1 | wc -l
```

### Directory Navigation

```bash
# Change to home directory
cd ~

# Go up one directory
cd ..

# Go to parent directory
cd ../..

# List recent directories
dirs -v

# Push directory
pushd /path/to/dir
```

### System Monitoring

```bash
# Disk space
df -h

# Memory usage
free -h

# Load average
uptime

# Running processes
ps aux | grep 'pattern'

# CPU usage (top processes)
top -o cpu | head -10
```

## Quick Responses

**"Check system status"**

```bash
echo "=== System Status ==="
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo "Uptime: $(uptime)"
echo "Disk: $(df -h / | tail -1 | awk '{print $5" used"}')"
echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2" used"}')"
```

**"Show running processes"**

```bash
ps aux | grep -E '(nginx|apache|mysql)' || echo "No web services found"
```

**"Check disk space"**

```bash
df -h | grep -E '(Filesystem|/dev/)'
```

## Notes

- Only basic commands that are safe to execute
- No destructive operations (rm -rf, etc.)
- No system configuration changes
- Only reads user-accessible information
- Safe for regular monitoring and basic operations

## Examples

**"Show me what's in the current directory"**

```bash
ls -la
```

**"Check how much memory is being used"**

```bash
free -h
```

**"Check if any web services are running"**

```bash
if pgrep nginx > /dev/null; then echo "Nginx is running"; else echo "Nginx is not running"; fi
```