Set WshShell = CreateObject("WScript.Shell")
' Define a pasta raiz do projeto
WshShell.CurrentDirectory = "C:\Users\AICOM-PC\Desktop\ver"
' Executa o start_widget.py usando o ambiente virtual (sem terminal)
WshShell.Run """C:\Users\AICOM-PC\Desktop\ver\venv\Scripts\pythonw.exe"" ""C:\Users\AICOM-PC\Desktop\ver\start_widget.py""", 0, False