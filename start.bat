@echo off
echo ========================================
echo   TransLive 智译通 - 启动脚本
echo ========================================
echo.

echo [1/3] 启动 LibreTranslate (Docker)...
docker compose up -d
if %errorlevel% neq 0 (
    echo Docker 启动失败，请确认 Docker Desktop 已运行
    pause
    exit /b 1
)

echo.
echo [2/3] 等待翻译引擎就绪（首次启动需下载模型，约 2-5 分钟）...
timeout /t 30 /nobreak > nul

echo.
echo [3/3] 请在新终端中分别启动后端和前端:
echo   后端: cd backend ^&^& pip install -r requirements.txt ^&^& python main.py
echo   前端: cd frontend ^&^& npm install ^&^& npm run dev
echo.
echo 访问 http://localhost:5173 使用系统
pause
