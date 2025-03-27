#!/bin/bash

echo "===== DIAGNÓSTICO COMPLETO SEARCH-THE-POINT APP =====" | tee debug-report.log
echo "Data e hora: $(date)" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Verificar status dos contêineres
echo "===== STATUS DOS CONTÊINERES =====" | tee -a debug-report.log
docker ps -a | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Coletar variáveis de ambiente do frontend
echo "===== VARIÁVEIS DE AMBIENTE DO FRONTEND =====" | tee -a debug-report.log
docker exec search-the-point-frontend env | grep REACT | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Coletar logs dos contêineres
echo "===== LOGS DO BACKEND (últimas 50 linhas) =====" | tee -a debug-report.log
docker logs search-the-point-backend --tail 50 | tee -a debug-report.log
echo "" | tee -a debug-report.log

echo "===== LOGS DO FRONTEND (últimas 50 linhas) =====" | tee -a debug-report.log
docker logs search-the-point-frontend --tail 50 | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Verificar configuração de rede
echo "===== CONFIGURAÇÃO DE REDE DOS CONTÊINERES =====" | tee -a debug-report.log
echo "--- Frontend ---" | tee -a debug-report.log
docker exec search-the-point-frontend sh -c "ip addr" 2>/dev/null || docker exec search-the-point-frontend sh -c "ifconfig" 2>/dev/null || echo "Comandos de rede não disponíveis" | tee -a debug-report.log
echo "" | tee -a debug-report.log

echo "--- Backend ---" | tee -a debug-report.log
docker exec search-the-point-backend sh -c "ip addr" 2>/dev/null || docker exec search-the-point-backend sh -c "ifconfig" 2>/dev/null || echo "Comandos de rede não disponíveis" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Testar conectividade entre contêineres
echo "===== TESTE DE CONECTIVIDADE =====" | tee -a debug-report.log
echo "--- Frontend -> Backend ---" | tee -a debug-report.log
docker exec search-the-point-frontend wget -O- -q backend:8000/health || docker exec search-the-point-frontend curl -s backend:8000/health || echo "Falha no teste de conectividade" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Verificar código fonte relacionado a fetch no frontend
echo "===== CÓDIGO FRONTEND PARA FETCH =====" | tee -a debug-report.log
docker exec search-the-point-frontend grep -r "fetch(" /app/src --include="*.js" --include="*.jsx" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Verificar rotas da API no backend
echo "===== ROTAS API BACKEND =====" | tee -a debug-report.log
docker exec search-the-point-backend grep -r "@app\." /app --include="*.py" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Testar o endpoint de upload diretamente
echo "===== TESTE DIRETO DO ENDPOINT DE UPLOAD =====" | tee -a debug-report.log
curl -v -X POST "http://localhost:8000/upload-pdf/" -F "file=@sample.pdf" 2>&1 | tee -a debug-report.log || echo "Falha no teste direto do endpoint (você precisa ter um arquivo sample.pdf no diretório atual)" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Informações do ambiente Codespace
echo "===== INFORMAÇÕES DO AMBIENTE CODESPACE =====" | tee -a debug-report.log
echo "URL do Codespace: $CODESPACE_NAME" | tee -a debug-report.log
echo "Portas encaminhadas:" | tee -a debug-report.log
curl -s http://localhost:3000 > /dev/null && echo "- Porto 3000 (frontend): Acessível" || echo "- Porto 3000 (frontend): Não acessível" | tee -a debug-report.log
curl -s http://localhost:8000 > /dev/null && echo "- Porto 8000 (backend): Acessível" || echo "- Porto 8000 (backend): Não acessível" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Verificar CORS no backend
echo "===== CONFIGURAÇÃO CORS NO BACKEND =====" | tee -a debug-report.log
docker exec search-the-point-backend grep -r "CORS" /app --include="*.py" | tee -a debug-report.log
echo "" | tee -a debug-report.log

# Verificar console do navegador
echo "===== COMO CAPTURAR LOGS DO CONSOLE DO NAVEGADOR =====" | tee -a debug-report.log
echo "1. Abra a aplicação no navegador" | tee -a debug-report.log
echo "2. Pressione F12 para abrir as ferramentas de desenvolvedor" | tee -a debug-report.log
echo "3. Vá para a aba 'Console'" | tee -a debug-report.log
echo "4. Tente fazer o upload do PDF que está falhando" | tee -a debug-report.log
echo "5. Copie os erros/avisos que aparecerem no console" | tee -a debug-report.log
echo "" | tee -a debug-report.log

echo "===== RECOMENDAÇÕES PARA CODESPACES =====" | tee -a debug-report.log
echo "1. Verifique se as portas estão sendo encaminhadas corretamente no Codespace" | tee -a debug-report.log
echo "2. No Codespace, a URL pode ser diferente. Tente ajustar REACT_APP_API_URL para a URL pública do Codespace" | tee -a debug-report.log
echo "   Exemplo: https://seu-nome-codespace-xxxx-8000.preview.app.github.dev" | tee -a debug-report.log
echo "" | tee -a debug-report.log

echo "Diagnóstico concluído! Consulte o arquivo debug-report.log para análise detalhada." 