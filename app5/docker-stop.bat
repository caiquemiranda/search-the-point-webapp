@echo off
echo Parando Search-The-Point App...

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

echo Parando os contêineres...
%COMPOSE_CMD% down

echo.
echo Serviços parados com sucesso.
echo. 