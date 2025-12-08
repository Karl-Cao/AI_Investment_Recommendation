@echo off
echo ========================================
echo   GitHub Push Script
echo   AI Investment Recommendation System
echo ========================================
echo.

echo Checking for sensitive files...
git check-ignore -v .streamlit/secrets.toml
if %errorlevel% neq 0 (
    echo WARNING: secrets.toml might not be ignored!
    echo Please check .gitignore before continuing.
    pause
    exit /b 1
)
echo ✓ secrets.toml is properly ignored
echo.

echo Files to be committed:
git status --short
echo.

echo Adding all files to git...
git add .
echo.

echo Current status:
git status
echo.

set /p CONFIRM="Do you want to commit and push these changes? (y/n): "
if /i "%CONFIRM%" neq "y" (
    echo Aborted.
    pause
    exit /b 0
)

echo.
set /p MESSAGE="Enter commit message (or press Enter for default): "
if "%MESSAGE%"=="" (
    set MESSAGE=Update: Add streaming chat, backtest feature, and documentation
)

echo.
echo Committing with message: %MESSAGE%
git commit -m "%MESSAGE%"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   Push completed!
echo ========================================
echo.
pause
