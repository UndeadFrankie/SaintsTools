@echo off
setlocal enabledelayedexpansion

echo Renaming files in %cd%
for %%f in (*.*) do (
    rem Skip this script file
    if /I "%%~nxf"=="%~nx0" (
        echo Skipping script file: %%~nxf
    ) else (
        set "filename=%%~nf"
        set "ext=%%~xf"
        
        rem Only process files with names longer than 6 characters
        if not "!filename!"=="!filename:~0,-6!" (
            set "newname=!filename:~0,-6!!ext!"
            echo Renaming "%%f" to "!newname!"
            ren "%%f" "!newname!"
        )
    )
)
echo Done.
pause
