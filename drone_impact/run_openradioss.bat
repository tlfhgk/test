@echo off
REM ---------------------------------------------------------------------------
REM  Drone impact - OpenRadioss run script (Windows)
REM
REM  Set OPENRADIOSS to your OpenRadioss install, then run this file from the
REM  folder that holds main_openradioss.k / building.k / drone.k
REM ---------------------------------------------------------------------------
set OPENRADIOSS=C:\OpenRadioss
set NP=4

set RAD_CFG_PATH=%OPENRADIOSS%\hm_cfg_files
set PATH=%OPENRADIOSS%\exec;%PATH%

echo === STARTER (reads the LS-DYNA .k and writes the restart file) ===
starter_win64.exe -i main_openradioss.k -np %NP%
if errorlevel 1 goto fail

echo.
echo === ENGINE (runs the transient) ===
engine_win64.exe -i main_openradioss_0001.rad -np %NP%
if errorlevel 1 goto fail

echo.
echo === CONVERT ANIMATION FILES TO VTK (open the .vtk series in ParaView) ===
for %%F in (main_openradiossA*) do anim_to_vtk_win64.exe %%F > %%F.vtk

echo.
echo Done.  Open main_openradiossA*.vtk in ParaView.
goto end

:fail
echo.
echo Run failed - read main_openradioss_0000.out for the reason.
echo Unsupported LS-DYNA keywords are listed there as warnings.

:end
pause
