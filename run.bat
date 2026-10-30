@echo off
setlocal

:: Guarantee the working directory is the project directory where run.bat is located
cd /d "%~dp0"

:: Ensure Windows system utilities and Python are prioritized in PATH to avoid truncation/not found errors
set "PATH=%SystemRoot%\System32;%SystemRoot%;%SystemRoot%\System32\Wbem;%LocalAppData%\Programs\Python\Python313;%LocalAppData%\Programs\Python\Python313\Scripts;%PATH%"

echo ========================================================
echo         Student Portal - Launch Script
echo ========================================================

:: Detect Python executable path
set "PY_CMD="

:: 1. Check direct Python 3.13 install path
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python313\python.exe"
)

:: 2. Fall back to where python in PATH
if not defined PY_CMD (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if not defined PY_CMD (
            echo %%i | findstr /i "WindowsApps" >nul
            if errorlevel 1 set "PY_CMD=%%i"
        )
    )
)

:: 3. Fall back to py launcher
if not defined PY_CMD (
    where py >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3"
)

:: 4. Fall back to plain python
if not defined PY_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo [ERROR] Python was not found on your system.
    echo Please install Python 3.10+ and make sure it is added to your PATH.
    echo.
    pause
    exit /b 1
)

echo [INFO] Using Python: "%PY_CMD%"

:: Check if MySQL (port 3306) is listening
netstat -ano | findstr ":3306" >nul
if errorlevel 1 (
    echo [INFO] MySQL is not running on port 3306. Attempting to start MySQL...

    :: Try starting WAMP MySQL service
    net start wampmysqld >nul 2>&1

    :: Check again; if still down, try direct mysqld binary
    netstat -ano | findstr ":3306" >nul
    if errorlevel 1 (
        if exist "C:\wamp\bin\mysql\mysql5.6.12\bin\mysqld.exe" (
            start "" /B "C:\wamp\bin\mysql\mysql5.6.12\bin\mysqld.exe" --defaults-file="C:\wamp\bin\mysql\mysql5.6.12\my.ini"
            ping -n 4 127.0.0.1 >nul
        ) else if exist "C:\xampp\mysql\bin\mysqld.exe" (
            start "" /B "C:\xampp\mysql\bin\mysqld.exe" --defaults-file="C:\xampp\mysql\bin\my.ini"
            ping -n 4 127.0.0.1 >nul
        )
    )

    :: Verify MySQL status after start attempts
    netstat -ano | findstr ":3306" >nul
    if not errorlevel 1 (
        echo [INFO] MySQL server started successfully.
    ) else (
        echo [WARNING] MySQL service could not be started automatically.
        echo           Please start WAMP/XAMPP or MySQL service manually.
    )
) else (
    echo [INFO] MySQL service is active on port 3306.
)

:: Test MySQL database connectivity to portal_db
"%PY_CMD%" -c "import pymysql; conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',password='',database='portal_db'); conn.close(); print('[INFO] Connected to MySQL portal_db successfully.')" 2>nul
if errorlevel 1 (
    echo [WARNING] Could not connect to MySQL database 'portal_db'.
    echo           Please ensure MySQL is running with database 'portal_db'.
)

:: Schedule opening default browser to the Student Portal URL
start "" /B cmd /c "ping -n 3 127.0.0.1 >nul & start http://127.0.0.1:8000/"

echo [INFO] Starting Django server at http://127.0.0.1:8000/
echo [INFO] Open http://127.0.0.1:8000/ in your browser.
echo [INFO] Press Ctrl+C in this window to stop the server.
echo ========================================================

"%PY_CMD%" manage.py runserver 127.0.0.1:8000

pause
