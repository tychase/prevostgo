@echo off
REM Git push script for PrevostGo patches

echo === PrevostGo Git Push Script ===
echo.

REM Navigate to project directory
cd /d "C:\Users\tmcha\Dev\prevostgo"

REM Check current status
echo === Checking Git Status ===
git status --short
echo.

REM Add all changes
echo === Adding all changes ===
git add -A
echo.

REM Commit with descriptive message
echo === Committing changes ===
git commit -m "Add specs normalization and improved search/card components" -m "" -m "- Add backend utils for normalizing coach specifications" -m "- Add database migration for new spec columns (model, chassis_type, mileage, slide_count, price_contact)" -m "- Add new SearchBar component with buy/sell tabs and debounced search" -m "- Add improved CoachCard component with normalized specs display" -m "- Add Claude configuration files (.claude/config.json, .vscode/settings.json)" -m "- Add patch application summary documentation"
echo.

REM Push to origin
echo === Pushing to GitHub ===
git push origin main
echo.

echo === Push completed! ===
echo Check your GitHub repository at: https://github.com/tychase/prevostgo
pause