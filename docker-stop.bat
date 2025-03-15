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
echo Removendo contêineres parados...
docker container prune -f

echo.
echo Removendo imagens não utilizadas...
docker image prune -af

echo.
echo Limpando o cache do sistema Docker...
docker system prune -f --volumes

echo.
echo Serviços parados e sistema limpo com sucesso.
echo Todas as imagens, contêineres e cache foram removidos.
echo.
echo Para iniciar novamente, use docker-start.bat ou docker-rebuild.bat 