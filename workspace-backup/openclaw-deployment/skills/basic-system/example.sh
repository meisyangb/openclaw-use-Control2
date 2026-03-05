#!/bin/bash

# Basic System Information Example Script
# This demonstrates the capabilities of the basic-system skill

echo "=== Basic System Information ==="
echo

# Current user and directory
echo "Current user: $(whoami)"
echo "Working directory: $(pwd)"
echo

# System uptime
echo "System uptime:"
uptime
echo

# Disk usage
echo "Disk usage (mounted filesystems):"
df -h | grep -E '^Filesystem|^/dev/'
echo

# Memory usage
echo "Memory usage:"
free -h | grep -E '^Mem|^Swap'
echo

# Process count
echo "Running processes:"
ps aux | wc -l | sed 's/^/Total processes: /'
echo

# Show top 5 CPU consuming processes
echo "Top 5 CPU-consuming processes:"
ps aux --sort=-%cpu | head -6 | tail -5
echo

echo "=== System Check Complete ==="