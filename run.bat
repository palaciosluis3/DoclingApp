@echo off
color 0A
echo [SYS] Optimizando variables de entorno para CPU...
set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set MKL_NUM_THREADS=%NUMBER_OF_PROCESSORS%

echo [INFO] Activando entorno...
call venv\Scripts\activate

echo [INFO] Lanzando aplicacion...
:: pythonw se usa para no mantener la terminal abierta en el fondo. Si requieres ver errores de consola, cambialo a python.
start pythonw app.py
