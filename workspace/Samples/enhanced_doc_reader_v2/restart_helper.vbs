' restart_helper.vbs - kills the running doc_reader_onefile.py process and relaunches it silently.
' Spawned by the app's own /restart endpoint, runs independently so it survives the parent exiting.

Dim objWMIService, colProcesses, objProcess, WshShell, scriptFolder

scriptFolder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set colProcesses = objWMIService.ExecQuery( _
    "Select * from Win32_Process Where (Name = 'python.exe' or Name = 'pythonw.exe')")

For Each objProcess in colProcesses
    If InStr(objProcess.CommandLine, "doc_reader_onefile.py") > 0 Then
        objProcess.Terminate()
    End If
Next

' Give the OS a moment to fully release the port before rebinding.
WScript.Sleep 1500

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """wscript.exe"" """ & scriptFolder & "\start_silent.vbs""", 0, False
