@echo off
setlocal enabledelayedexpansion
REM ===========================================================================
REM  Drone impact - OpenRadioss run script (Windows, SMP)
REM
REM  Only the two settings in STEP 1 need touching.  Double-click this file, or
REM  run it from a cmd window; it always works in its own folder, so the
REM  *INCLUDE paths in the deck resolve.
REM
REM  Environment variables follow OpenRadioss INSTALL.md.
REM ===========================================================================

REM ---- STEP 1 : edit these two ----------------------------------------------
set OPENRADIOSS_PATH=C:\OpenRadioss
set OMP_NUM_THREADS=4
REM ---------------------------------------------------------------------------

if not exist "%OPENRADIOSS_PATH%\exec" (
    echo.
    echo [X] OpenRadioss not found at: %OPENRADIOSS_PATH%
    echo     Edit OPENRADIOSS_PATH at the top of this file.
    goto end
)

set RAD_CFG_PATH=%OPENRADIOSS_PATH%\hm_cfg_files
set RAD_H3D_PATH=%OPENRADIOSS_PATH%\extlib\h3d\lib\win64
set KMP_STACKSIZE=400m
set PATH=%OPENRADIOSS_PATH%\extlib\hm_reader\win64;%PATH%
set PATH=%OPENRADIOSS_PATH%\extlib\intelOneAPI_runtime\win64;%PATH%
set PATH=%OPENRADIOSS_PATH%\exec;%PATH%

cd /d "%~dp0"

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
    echo     Look for anim_to_vtk* in %OPENRADIOSS_PATH%\exec and run it as:
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
