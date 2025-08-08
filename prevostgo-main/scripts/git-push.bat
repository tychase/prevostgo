@echo off
echo Checking Git status...
git status

echo.
echo Adding all changes...
git add .

echo.
echo Creating commit...
git commit -m "Update: Push latest changes for external review"

echo.
echo Pushing to remote repository...
git push origin main

echo.
echo Done! Your changes have been pushed to Git.
pause
