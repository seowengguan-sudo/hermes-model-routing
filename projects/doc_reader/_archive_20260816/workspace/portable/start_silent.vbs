Set WshShell = CreateObject("WScript.Shell")

' OAKAI Document Reader v2.2 - Silent Launcher
' Launches server without console window for clean Windows operation
' Place in same folder as doc_reader_onefile.py

strScriptDir = Left(WScript.ScriptFullName, Len(WScript.ScriptFullName) - Len(WScript.ScriptName))
strScriptPath = strScriptDir & "doc_reader_onefile.py"

Set objFSO = CreateObject("Scripting.FileSystemObject")
strUser = WshShell.ExpandEnvironmentStrings("%USERNAME%")

' Try common Python locations for pythonw.exe (no console window)
pythonwPaths = Array( _
    "C:\Users\" & strUser & "\AppData\Local\Programs\Python\Python312\pythonw.exe", _
    "C:\Users\" & strUser & "\AppData\Local\Programs\Python\Python311\pythonw.exe", _
    "C:\Users\" & strUser & "\AppData\Local\Programs\Python\Python310\pythonw.exe", _
    "C:\Python312\pythonw.exe", _
    "C:\Python311\pythonw.exe" _
)

strPython = "pythonw.exe"  ' Default: rely on PATH

For Each py In pythonwPaths
    If objFSO.FileExists(py) Then
        strPython = py
        Exit For
    End If
Next

' Launch server silently
WshShell.CurrentDirectory = strScriptDir
WshShell.Run """" & strPython & """ """ & strScriptPath & """", 0, False
