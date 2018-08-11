@ECHO off

REM User Guide
REM ==============================================
REM Use only with latest version of auto_rip!
REM autorip.bat != auto_rip
REM 
REM This batch file should be placed in Regripper
REM folder that also contains auto_rip.
REM
REM SAM, SECURITY, SOFTWARE, SYSTEM should be
REM 1 level above Regripper folder
REM
REM Create a Users folder 1 level above Regripper
REM folder as well.
REM
REM In Users folder, create a folder for each user,
REM and place their NTUSER.DAT & UsrClass.DAT in it.
REM ==============================================

FOR /f "delims=" %%i IN ('dir /b ..\Users') DO auto_rip64^
 -s ..\ -n "..\Users\%%i" -u "..\Users\%%i" -r "..\Users\%%i" -c all
