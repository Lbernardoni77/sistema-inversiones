@echo off
echo ========================================
echo    SUBIENDO PROYECTO A GITHUB
echo ========================================
echo.

echo 1. Inicializando repositorio Git...
git init

echo.
echo 2. Agregando todos los archivos...
git add .

echo.
echo 3. Haciendo primer commit...
git commit -m "Primer commit: Sistema de inversiones completo"

echo.
echo 4. Configurando repositorio remoto...
echo Por favor, ingresa tu nombre de usuario de GitHub:
set /p username=
git remote add origin https://github.com/%username%/sistema-inversiones.git

echo.
echo 5. Subiendo a GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo    ¡PROYECTO SUBIDO EXITOSAMENTE!
echo ========================================
echo.
echo Tu repositorio está disponible en:
echo https://github.com/%username%/sistema-inversiones
echo.
echo Ahora puedes proceder con el despliegue en Render.
echo.
pause 