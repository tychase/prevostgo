Write-Host "Git Push Helper for PrevostGo" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (!(Test-Path .git)) {
    Write-Host "Error: Not in a git repository!" -ForegroundColor Red
    exit 1
}

# Show current branch
Write-Host "Current branch:" -ForegroundColor Yellow
git branch --show-current
Write-Host ""

# Show current status
Write-Host "Current Git status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Do you want to add all changes and commit? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Add all changes
Write-Host "Adding all changes..." -ForegroundColor Green
git add .

# Get commit message
$defaultMessage = "Update: Push latest changes for external review - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
$commitMessage = Read-Host "Enter commit message (or press Enter for default: '$defaultMessage')"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = $defaultMessage
}

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Green
git commit -m $commitMessage

# Show remote info
Write-Host ""
Write-Host "Remote repositories:" -ForegroundColor Yellow
git remote -v
Write-Host ""

# Ask which branch to push to
$branch = Read-Host "Enter branch name to push to (or press Enter for 'main')"
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
}

# Push changes
Write-Host "Pushing to origin/$branch..." -ForegroundColor Green
git push origin $branch

Write-Host ""
Write-Host "Done! Your changes have been pushed to Git." -ForegroundColor Green
Write-Host ""
Write-Host "You can now share the repository URL with others for review." -ForegroundColor Cyan
