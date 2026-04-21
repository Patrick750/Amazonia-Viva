@echo off
echo === Amazonia Viva: Setup Inicial ===

echo.
echo 1. Instalando dependencias de Python...
pip install -r requirements.txt

echo.
echo 2. Aplicando migraciones de base de datos...
python manage.py migrate

echo.
echo 3. Sembrando datos de prueba (Demo)...
python manage.py setup_demo

echo.
echo 4. Instalando y compilando el Frontend...
cd frontend_project
call npm install
call npm run build
cd ..

echo.
echo === Setup finalizado con exito! ===
pause
