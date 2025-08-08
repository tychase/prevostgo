#!/bin/bash
# Git push script for PrevostGo patches

echo "=== PrevostGo Git Push Script ==="
echo ""

# Navigate to project directory
cd "C:\Users\tmcha\Dev\prevostgo" || exit 1

# Check current status
echo "=== Checking Git Status ==="
git status --short

# Add all changes
echo ""
echo "=== Adding all changes ==="
git add -A

# Commit with descriptive message
echo ""
echo "=== Committing changes ==="
git commit -m "Add specs normalization and improved search/card components

- Add backend utils for normalizing coach specifications
- Add database migration for new spec columns (model, chassis_type, mileage, slide_count, price_contact)
- Add new SearchBar component with buy/sell tabs and debounced search
- Add improved CoachCard component with normalized specs display
- Add Claude configuration files (.claude/config.json, .vscode/settings.json)
- Add patch application summary documentation"

# Push to origin
echo ""
echo "=== Pushing to GitHub ==="
git push origin main

echo ""
echo "=== Push completed! ==="
echo "Check your GitHub repository at: https://github.com/tychase/prevostgo"