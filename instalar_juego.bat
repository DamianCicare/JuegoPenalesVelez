@echo off
title Lanzador de Penales Velez
echo Revisando componentes necesarios...

:: 1. Intenta instalar pygame (si ya esta, no hace nada)
python -m pip install pygame --quiet

echo.
echo ¡Todo listo! Iniciando el juego...
echo.

:: 2. Lanza tu juego
python juego.py

pause