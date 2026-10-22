@echo off
echo =====================================================================
echo  UBER R*-TREE: PUSH COMMIT HISTORY TO GITHUB REPOSITORY
echo =====================================================================
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/miriyaladhanwinn/uber-rstar-tree-dispatch.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Aborting.
    pause
    exit /b
)

echo.
echo Adding remote origin: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Pushing all commits and branch history to GitHub...
git push -u origin main

echo.
echo =====================================================================
echo  SUCCESS! Visit your GitHub repository to verify the commit history.
echo  All 4 team members will be linked via their emails!
echo =====================================================================
pause
