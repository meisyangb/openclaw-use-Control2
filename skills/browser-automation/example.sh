#!/bin/bash

# Browser Automation Example Script
# Demonstrates basic browser automation capabilities

echo "=== Browser Automation Demo ==="
echo

# Check if browser control is available
if command -v browser >/dev/null 2>&1; then
    echo "✅ Browser control is available"
else
    echo "❌ Browser control not found - please start OpenClaw browser service"
    exit 1
fi

echo
echo "Opening example.com..."
browser act --action=open --targetUrl="https://example.com" 2>/dev/null

echo "Waiting for page to load..."
sleep 3

echo "Taking screenshot..."
browser act --action=screenshot --ref="page" 2>/dev/null

echo "Taking page snapshot for element analysis..."
browser act --action=snapshot --refs="aria" 2>/dev/null

echo "Extracting page title..."
title=$(browser act --action=act --kind=evaluate --fn="document.title" 2>/dev/null | grep -o '"[^"]*"' | tr -d '"')
echo "Page title: $title"

echo
echo "=== Testing Form Interaction ==="
echo

# Try to interact with a simple form (if available)
echo "Attempting to interact with form elements..."

# Focus on main content area
browser act --action=act --kind=hover --ref="main" 2>/dev/null

echo "Browser automation demo completed!"
echo "Check screenshots in browser session for visual confirmation."

else
    echo "❌ Browser control not working - browser service may not be started"
fi

echo
echo "=== Demo Complete ==="