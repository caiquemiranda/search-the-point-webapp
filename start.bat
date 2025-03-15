@echo off
echo Iniciando Search-The-Point App...

REM Configurar o endereço IP do servidor (substitua pelo seu IP se necessário)
set SERVER_IP=0.0.0.0
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

REM Verificar se o Python está instalado e obter o caminho correto
where python3 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

echo ERRO: Python não encontrado. Por favor, instale o Python antes de continuar.
echo Você pode baixar Python em https://www.python.org/downloads/
goto :EOF

:python_found
echo Python encontrado: %PYTHON_CMD%

REM Verificar se o Node.js está instalado
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERRO: Node.js não encontrado. Por favor, instale o Node.js antes de continuar.
    echo Você pode baixar Node.js em https://nodejs.org/
    goto :EOF
)

echo Verificando dependências do Python...
%PYTHON_CMD% -m pip install fastapi uvicorn python-multipart pymupdf sqlalchemy pydantic -q

REM Salvar o diretório atual
set CURRENT_DIR=%CD%

echo Verificando dependências do Node.js...
cd "%CURRENT_DIR%\app5\frontend"
if not exist node_modules (
    echo Instalando pacotes npm (isso pode demorar um pouco)...
    call npm install
)

echo Iniciando o backend...
start cmd /k "cd "%CURRENT_DIR%\app5\backend" && %PYTHON_CMD% -m uvicorn app:app --host %SERVER_IP% --port %BACKEND_PORT% --reload"

echo Aguardando o backend iniciar...
timeout /t 5 /nobreak

echo Iniciando o frontend...
start cmd /k "cd "%CURRENT_DIR%\app5\frontend" && npm start"

echo.
echo Serviços iniciados:
echo - Backend: http://%SERVER_IP%:%BACKEND_PORT%
echo - Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo Para acessar de outra máquina, use o endereço IP deste computador.
echo Pressione qualquer tecla para encerrar todos os serviços...
pause

REM Encerrar processos ao fechar
taskkill /f /im node.exe
taskkill /f /im python.exe
taskkill /f /im python3.exe 