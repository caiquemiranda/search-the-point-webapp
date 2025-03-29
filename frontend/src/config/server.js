// Configuração do servidor
export const SERVER_URL = (() => {
    // 1. Prioridade: Variável de ambiente definida no Docker/ambiente de produção
    if (process.env.REACT_APP_API_URL) {
        // Substitui "backend" por "localhost" se estiver sendo acessado pelo navegador
        return process.env.REACT_APP_API_URL.replace('http://backend:', 'http://localhost:');
    }

    // 2. Desenvolvimento local sem Docker
    if (window.location.origin.includes('localhost:3000')) {
        return 'http://localhost:8000';
    }

    // 3. Produção (assumindo que backend e frontend estão no mesmo domínio)
    return `${window.location.origin}`;
})();

// Log para debug
console.log('Conectando ao backend em:', SERVER_URL); 