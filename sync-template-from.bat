@echo off
REM =============================================
REM Pull template updates FROM 独立站详情页 project
REM =============================================
REM If you update template/main.css in 独立站详情页,
REM run this to bring changes into west_catalogue.

set SRC=%~dp0..\独立站详情页\template
set DST=%~dp0assets

echo Pulling template updates from 独立站详情页 ...
copy /Y "%SRC%\main.css" "%DST%\css\main.css" >nul
copy /Y "%SRC%\main.js" "%DST%\js\main.js" >nul

echo Done! west_catalogue now matches 独立站详情页 template.
