@echo off
setlocal enabledelayedexpansion
REM ===========================================================================
REM  Drone impact - OpenRadioss run script (Windows, SMP)
REM
REM  The OpenRadioss LS-DYNA reader parses .k files that merely sit in the run
REM  directory, whether or not anything includes them.  main.k and the blast
REM  deck therefore have to be out of reach.  This script solves that by
REM  copying only the three files OpenRadioss needs into a clean subfolder
REM  (_run_openradioss) and running there, so the source folder can hold
REM  anything at all.
REM ===========================================================================

REM ---- STEP 1 : edit these two ----------------------------------------------
set OPENRADIOSS_PATH=C:\OpenRadioss
set OMP_NUM_THREADS=4
REM ---------------------------------------------------------------------------

REM ---- locate the install ----------------------------------------------------
set STARTER=
if exist "%OPENRADIOSS_PATH%\exec\starter_win64.exe" goto found

echo [i] starter_win64.exe not directly under %OPENRADIOSS_PATH%\exec
echo [i] searching subfolders...
for /f "delims=" %%F in ('dir /b /s "%OPENRADIOSS_PATH%\starter_win64.exe" 2^>nul') do set STARTER=%%F
if "!STARTER!"=="" goto notfound

for %%F in ("!STARTER!") do set EXECDIR=%%~dpF
set EXECDIR=!EXECDIR:~0,-1!
for %%P in ("!EXECDIR!") do set OPENRADIOSS_PATH=%%~dpP
set OPENRADIOSS_PATH=!OPENRADIOSS_PATH:~0,-1!
echo [i] found -^> !OPENRADIOSS_PATH!
goto found

:notfound
echo.
echo [X] starter_win64.exe was not found anywhere under:
echo        %OPENRADIOSS_PATH%
echo.
echo     What is actually in there:
dir /b "%OPENRADIOSS_PATH%" 2>nul
echo.
echo     Search the whole drive with:
echo        where /r C:\ starter_win64.exe
echo     then set OPENRADIOSS_PATH to the folder that CONTAINS "exec".
goto end

:found
set RAD_CFG_PATH=%OPENRADIOSS_PATH%\hm_cfg_files
set RAD_H3D_PATH=%OPENRADIOSS_PATH%\extlib\h3d\lib\win64
set KMP_STACKSIZE=400m
set PATH=%OPENRADIOSS_PATH%\extlib\hm_reader\win64;%PATH%
set PATH=%OPENRADIOSS_PATH%\extlib\intelOneAPI_runtime\win64;%PATH%
set PATH=%OPENRADIOSS_PATH%\exec;%PATH%

if not exist "%RAD_CFG_PATH%" echo [!] warning: hm_cfg_files not found at %RAD_CFG_PATH%

REM ---- check the three inputs are here --------------------------------------
set SRC=%~dp0
set MISSING=
for %%F in (main_openradioss.k building.k drone.k) do (
    if not exist "%SRC%%%F" set MISSING=!MISSING! %%F
)
if not "!MISSING!"=="" (
    echo.
    echo [X] missing next to this script:!MISSING!
    echo     folder: %SRC%
    dir /b "%SRC%*.k" 2>nul
    goto end
)

REM ---- build a clean run directory -------------------------------------------
REM  Only these three files go in.  main.k / blast.inc must never be visible to
REM  the reader or it aborts on *LOAD_BLAST_ENHANCED.
set RUNDIR=%SRC%_run_openradioss
if not exist "%RUNDIR%" mkdir "%RUNDIR%"
del /q "%RUNDIR%\*.k" >nul 2>&1
del /q "%RUNDIR%\*.rad" >nul 2>&1
copy /y "%SRC%main_openradioss.k" "%RUNDIR%\" >nul
copy /y "%SRC%building.k"         "%RUNDIR%\" >nul
copy /y "%SRC%drone.k"            "%RUNDIR%\" >nul

cd /d "%RUNDIR%"
echo.
echo [i] run directory : %RUNDIR%
echo [i] contains      :
dir /b *.k

echo.
echo ============================================================
echo  1/3  STARTER   reads main_openradioss.k, writes the restart
echo ============================================================
starter_win64.exe -i main_openradioss.k -np 1
if errorlevel 1 goto fail

set ENGINE_IN=
for %%F in (*_0001.rad) do set ENGINE_IN=%%F
if "!ENGINE_IN!"=="" (
    echo.
    echo [X] Starter produced no engine file ^(*_0001.rad^).
    goto fail
)

echo.
echo ============================================================
echo  2/3  ENGINE    running the transient : !ENGINE_IN!
echo ============================================================
engine_win64.exe -i !ENGINE_IN!
if errorlevel 1 goto fail

echo.
echo ============================================================
echo  3/3  ANIMATION -^> VTK  (for ParaView)
echo ============================================================
set CONV=
for %%C in (anim_to_vtk_win64.exe anim_to_vtk.exe) do (
    where %%C >nul 2>&1 && set CONV=%%C
)
if "!CONV!"=="" (
    echo     Converter not found on PATH - skipping.
    echo     Look for anim_to_vtk* in %OPENRADIOSS_PATH%\exec and run:
    echo         anim_to_vtk_win64.exe ^<animfile^> ^> ^<animfile^>.vtk
) else (
    for %%F in (*A0??) do (
        echo     %%F  -^>  %%F.vtk
        !CONV! %%F > %%F.vtk
    )
    echo.
    echo     Open the *.vtk series in ParaView, from:
    echo         %RUNDIR%
)

echo.
echo === DONE ===
goto end

:fail
echo.
echo === RUN FAILED ===
echo Open this file and read the ERROR / WARNING lines:
echo    %RUNDIR%\main_openradioss_0000.out

:end
echo.
pause
