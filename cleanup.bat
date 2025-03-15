@echo off
echo Removendo aplicativos antigos...

REM Confirmar com o usuário
set /p CONFIRM=Tem certeza que deseja remover os aplicativos antigos (app1, app2, app3, app4)? (S/N): 

if /i "%CONFIRM%" neq "S" (
    echo Operação cancelada pelo usuário.
    goto :EOF
)

REM Remover pastas antigas
if exist app1 (
    echo Removendo app1...
    rmdir /s /q app1
)

if exist app2 (
    echo Removendo app2...
    rmdir /s /q app2
)

if exist app3 (
    echo Removendo app3...
    rmdir /s /q app3
)

if exist app4 (
    echo Removendo app4...
    rmdir /s /q app4
)

REM Remover arquivo .streamlit se existir
if exist .streamlit (
    echo Removendo pasta .streamlit...
    rmdir /s /q .streamlit
)

echo.
echo Limpeza concluída. Apenas o app5 permanece no projeto.
echo. 