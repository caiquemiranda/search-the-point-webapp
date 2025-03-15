@echo off
echo Iniciando Search-The-Point App com Docker...

REM Verificar se o Docker está instalado
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERRO: Docker não encontrado. Por favor, instale o Docker Desktop antes de continuar.
    echo Você pode baixar Docker em https://www.docker.com/products/docker-desktop
    goto :EOF
)

REM Verificar se o docker-compose está instalado
where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker Compose não encontrado. Tentando usar 'docker compose' diretamente...
    docker compose version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo ERRO: Docker Compose não encontrado. Por favor, instale o Docker Desktop com Compose.
        goto :EOF
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

echo Iniciando os contêineres...
%COMPOSE_CMD% up --build -d

echo.
echo Serviços iniciados:
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo.
echo Para acessar de outra máquina, use o endereço IP deste computador.
echo Para parar os serviços, execute docker-stop.bat
echo.
echo Pressione qualquer tecla para ver os logs (Ctrl+C para sair)...
pause
%COMPOSE_CMD% logs -f 