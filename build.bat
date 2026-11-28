@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === TBH 自动挂机助手 打包 ===

rem —— 找一个真能用的解释器（PATH 里的 python 可能是别的运行时装出来的）
set "PY=py -3"
%PY% -c "import cv2,mss,numpy,win32gui,keyboard,pyautogui,PyInstaller" >nul 2>nul
if errorlevel 1 set "PY=python"
%PY% -c "import cv2,mss,numpy,win32gui,keyboard,pyautogui,PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo [错误] 找不到装好 cv2/mss/pywin32/PyInstaller 的 Python，请先装 Python 3.9+ 并勾选 Add to PATH
    pause & exit /b 1
)
echo [0/3] 解释器：%PY%

echo [1/3] 安装/更新依赖...
%PY% -m pip install -r requirements.txt pyinstaller -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，可换镜像：%PY% -m pip install -r requirements.txt pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause & exit /b 1
)

echo [2/3] 打包 exe...
%PY% -m PyInstaller -F -w -n TBH_AutoBot bot_gui.py ^
  --hidden-import win32timezone --collect-submodules mss --noconfirm
if errorlevel 1 (
    echo [错误] 打包失败，看上面的输出
    pause & exit /b 1
)

echo [3/3] 收尾：拷贝模板图集、清掉中间产物...
copy /y templates.png dist\ >nul
rmdir /s /q build 2>nul

echo 完成：dist\TBH_AutoBot.exe（同目录必须有 templates.png）
pause
