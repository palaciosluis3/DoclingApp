@echo off
color 0B
echo [SYS] Iniciando configuracion del entorno GPU (CUDA)...

echo [INFO] Creando entorno virtual 'venv_gpu'...
python -m venv venv_gpu
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Fallo la creacion del entorno virtual. Verifica que Python este instalado y en el PATH.
    pause
    exit /b %errorlevel%
)

echo [INFO] Activando el entorno virtual venv_gpu...
call venv_gpu\Scripts\activate

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando PyTorch (CUDA 12.4). 
echo [INFO] Esta version es estable y mantendra total compatibilidad con tus drivers 572.83 y tu RTX 3060Ti...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo [INFO] Instalando dependencias de requirements.txt...
pip install -r requirements.txt

color 0B
echo [OK] Configuracion GPU completada con exito.
pause
