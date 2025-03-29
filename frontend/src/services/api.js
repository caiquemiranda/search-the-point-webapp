import { SERVER_URL } from '../config/server';

export const api = {
    // Buscar histórico de imagens
    async fetchImageHistory() {
        const response = await fetch(`${SERVER_URL}/history`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }
        return response.json();
    },

    // Buscar todas as coordenadas salvas
    async fetchAllSavedCoordinates() {
        const response = await fetch(`${SERVER_URL}/all-coordinates`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }
        return response.json();
    },

    // Buscar coordenadas de uma imagem específica
    async fetchSavedCoordinates(imageId) {
        const response = await fetch(`${SERVER_URL}/coordinates/${imageId}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }
        return response.json();
    },

    // Salvar uma nova coordenada
    async saveCoordinate(coordinateData) {
        const response = await fetch(`${SERVER_URL}/coordinates`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(coordinateData),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }
        return response.json();
    },

    // Exportar coordenadas para CSV
    async exportCoordinatesCsv() {
        const response = await fetch(`${SERVER_URL}/export-coordinates`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }
        return response.blob();
    },

    // Deletar uma coordenada
    async deleteCoordinate(id) {
        const response = await fetch(`${SERVER_URL}/coordinates/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }
        return response.json();
    }
}; 