import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export const SavedCoordinatesList = ({ imageId, onNavigate }) => {
    const [coordinates, setCoordinates] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchCoordinates = async () => {
        try {
            const data = await api.fetchSavedCoordinates(imageId);
            setCoordinates(data);
        } catch (error) {
            console.error('Erro ao carregar coordenadas:', error);
        } finally {
            setLoading(false);
        }
    };

    const deleteCoordinate = async (id) => {
        try {
            await api.deleteCoordinate(id);
            setCoordinates(coordinates.filter(coord => coord.id !== id));
        } catch (error) {
            console.error('Erro ao deletar coordenada:', error);
        }
    };

    useEffect(() => {
        if (imageId) {
            fetchCoordinates();
        }
    }, [imageId]);

    if (loading) {
        return <div>Carregando coordenadas...</div>;
    }

    return (
        <div className="saved-coordinates-list">
            <h3>Coordenadas Salvas</h3>
            {coordinates.length === 0 ? (
                <p>Nenhuma coordenada salva para esta imagem.</p>
            ) : (
                <ul>
                    {coordinates.map((coord) => (
                        <li key={coord.id}>
                            <span>{coord.name}</span>
                            <span>X: {coord.x}, Y: {coord.y}</span>
                            <button onClick={() => onNavigate(coord.x, coord.y)}>
                                Navegar
                            </button>
                            <button onClick={() => deleteCoordinate(coord.id)}>
                                Deletar
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}; 