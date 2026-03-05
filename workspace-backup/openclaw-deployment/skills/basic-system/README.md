# Basic System Skill

This skill provides fundamental system management and monitoring capabilities for everyday administrative tasks.

## Features

- **System Information**: Current user, working directory, uptime
- **File Operations**: List files, directories, and basic file management
- **System Monitoring**: Disk usage, memory usage, process monitoring
- **Quick Checks**: Essential system status information

## Usage

### Basic System Checks

```bash
# Run the example script
./example.sh

# Check current directory
pwd && ls -la

# Check system resources
df -h && free -h
```

### Process Monitoring

```bash
# Count processes
ps aux | wc -l

# Find specific processes
ps aux | grep nginx
ps aux | grep mysql
```

### File System Checks

```bash
# List files by size
ls -lS

# List files by modification date
ls -lt

# Count files in directory
ls -1 | wc -l
```

## Safety Notes

This skill is designed to be safe for regular use:
- **No destructive operations** (rm -rf, format, etc.)
- **No system configuration changes**
- **Only reads user-accessible information**
- **Safe for monitoring and basic operations**

## Example Output

```
=== Basic System Information ===

Current user: root
Working directory: /root

System uptime:
 18:30:15 up 5 days, 12:34,  2 users,  load average: 0.05, 0.10, 0.15

Disk usage (mounted filesystems):
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda2        40G   9G   29G  26% /
tmpfs           1.9G   24K  1.9G   1% /dev/shm

Memory usage:
              total        used        free      shared  buff/cache   available
Mem:           3.6G       1.5G       247Mi       2.9Mi       2.1G       2.0G
Swap:          1.9G        15Mi      1.9G

Running processes:
Total processes: 156

Top 5 CPU-consuming processes:
root      1234  5.2  0.1  1024  512 ?        Sl   10:30  1:23 /usr/bin/process1
user      5678  2.1  0.3  2048  768 ?        S    10:35  0:45 /usr/bin/process2

=== System Check Complete ===
```

## Integration

This skill can be used with other OpenClaw skills for comprehensive system management.