@echo off
setlocal enabledelayedexpansion
REM ===========================================================================
REM  PNG sequence -> mp4  (ffmpeg)
REM
REM  Put this file in the folder where ParaView wrote its PNG frames
REM  (File > Save Animation), then double-click it.
REM
REM  ffmpeg is not bundled with anything else here.  Get a Windows build from
REM  https://www.gyan.dev/ffmpeg/builds/  ("release essentials" zip), unzip it,
REM  and either add its bin folder to PATH or set FFMPEG below to the full path
REM  of ffmpeg.exe.
REM ===========================================================================

REM ---- STEP 1 : edit if you want ---------------------------------------------
set FPS=30
set CRF=18
set OUT=drone_impact.mp4
set FFMPEG=ffmpeg
REM  FPS  : frames per second.  The run writes a frame every 0.25 ms, so 30 fps
REM         turns 35 ms of simulation into 4.7 s of video.  Lower = slower.
REM  CRF  : quality, 0 = lossless, 18 = visually lossless, 23 = default.
REM ---------------------------------------------------------------------------

cd /d "%~dp0"

where %FFMPEG% >nul 2>&1
if errorlevel 1 (
    if not exist "%FFMPEG%" (
        echo.
        echo [X] ffmpeg not found.
        echo     Download a Windows build from https://www.gyan.dev/ffmpeg/builds/
        echo     then set FFMPEG at the top of this file to ...\bin\ffmpeg.exe
        goto end
    )
)

REM ---- find the frame naming ParaView used ------------------------------------
set FIRST=
for %%F in (*.0000.png) do if "!FIRST!"=="" set FIRST=%%~nxF
if "!FIRST!"=="" (
    echo.
    echo [X] No file matching *.0000.png in this folder:
    echo        %~dp0
    echo.
    echo     PNG files here:
    dir /b *.png 2>nul
    echo.
    echo     ParaView names frames ^<basename^>.0000.png, .0001.png and so on.
    echo     Save the animation as PNG into this folder and run again.
    goto end
)

set BASE=!FIRST:.0000.png=!
set /a COUNT=0
for %%F in (!BASE!.*.png) do set /a COUNT+=1

echo.
echo   frames   : !COUNT!   ^(!BASE!.0000.png ...^)
echo   fps      : %FPS%
echo   output   : %OUT%
echo.

%FFMPEG% -y -framerate %FPS% -i "!BASE!.%%04d.png" ^
         -c:v libx264 -pix_fmt yuv420p -crf %CRF% ^
         -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" ^
         "%OUT%"

if errorlevel 1 goto fail

echo.
echo === DONE ===
echo   %~dp0%OUT%
goto end

:fail
echo.
echo === ffmpeg FAILED === read the message above.

:end
echo.
pause
