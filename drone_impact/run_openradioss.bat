@echo off
setlocal enabledelayedexpansion
REM ===========================================================================
REM  Drone impact - OpenRadioss run script (Windows, SMP)
REM
REM  Set OPENRADIOSS_PATH below to wherever the release zip was extracted.
REM  If the zip added an extra folder level, this script finds it by itself.
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

cd /d "%~dp0"

if not exist "main_openradioss.k" (
    echo.
    echo [X] main_openradioss.k is not in this folder:
    echo        %~dp0
    dir /b *.k 2>nul
    goto end
)

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
    echo     Open the *.vtk series in ParaView.
)

echo.
echo === DONE ===
goto end

:fail
echo.
echo === RUN FAILED ===
echo Open  main_openradioss_0000.out  and read the ERROR / WARNING lines.
echo LS-DYNA keywords the reader could not map are listed there.

:end
echo.
pause
