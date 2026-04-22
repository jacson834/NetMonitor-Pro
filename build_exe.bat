@echo off
echo Compilando Widget Desktop...
pyinstaller --noconfirm --onedir --windowed --name "NetWidget" "widget/app.py"

echo Compilando Backend...
pyinstaller --noconfirm --onedir --console --name "NetBackend" "start_backend.py"
echo Build concluido em /dist/