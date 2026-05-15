@echo off
REM =============================================
REM Sync shared template assets between projects
REM =============================================
REM Runs from west_catalogue root
REM Copies assets/ to the 独立站详情页 template/ folder
REM so both projects stay visually consistent.

set SRC=%~dp0assets
set DST=%~dp0..\独立站详情页\template

echo Copying assets to 独立站详情页/template/ ...
copy /Y "%SRC%\css\main.css" "%DST%\main.css" >nul
copy /Y "%SRC%\js\main.js" "%DST%\main.js" >nul

echo Done! Both projects now share the same template.
