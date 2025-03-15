@echo off
echo Reconstruindo contêineres do Search-The-Point App...

REM Verificar se o docker-compose está instalado
where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker Compose não encontrado. Tentando usar 'docker compose' diretamente...
    docker compose version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo ERRO: Docker Compose não encontrado.
        goto :EOF
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

echo Parando contêineres existentes...
%COMPOSE_CMD% down

echo Removendo imagens antigas...
%COMPOSE_CMD% rm -f

echo Reconstruindo imagens...
%COMPOSE_CMD% build --no-cache

echo Iniciando os contêineres...
%COMPOSE_CMD% up -d

echo.
echo Serviços reiniciados:
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo.
echo Para acessar de outra máquina, use o endereço IP deste computador.
echo Para ver os logs, execute: %COMPOSE_CMD% logs -f
echo. 