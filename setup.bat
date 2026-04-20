@echo off
color 0A
echo [SYS] Iniciando configuracion del entorno...

echo [INFO] Creando entorno virtual 'venv'...
python -m venv venv
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Fallo la creacion del entorno virtual. Verifica que Python este instalado y en el PATH.
    pause
    exit /b %errorlevel%
)

echo [INFO] Activando el entorno virtual...
call venv\Scripts\activate

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando PyTorch versiOn CPU (para evitar descargas pesadas de CUDA)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo [INFO] Instalando dependencias de requirements.txt...
pip install -r requirements.txt

color 0A
echo [OK] Configuracion completada con exito.
pause
