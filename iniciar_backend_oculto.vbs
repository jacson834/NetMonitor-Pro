Set WshShell = CreateObject("WScript.Shell")
' Define a pasta raiz do projeto
WshShell.CurrentDirectory = "C:\Users\AICOM-PC\Desktop\ver"
' Executa o pythonw.exe (que não abre janela) usando o ambiente virtual
WshShell.Run """C:\Users\AICOM-PC\Desktop\ver\venv\Scripts\pythonw.exe"" ""C:\Users\AICOM-PC\Desktop\ver\start_backend.py""", 0, False