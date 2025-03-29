import React from 'react';

export const ImageHistory = ({
    historyOpen,
    imageHistory,
    selectedImage,
    onImageSelect,
    onToggleHistory
}) => {
    if (!historyOpen) return null;

    return (
        <div className="image-history">
            <div className="history-header">
                <h3>Histórico de Imagens</h3>
                <button onClick={onToggleHistory}>Fechar</button>
            </div>
            <div className="history-list">
                {imageHistory.length === 0 ? (
                    <p>Nenhum histórico disponível.</p>
                ) : (
                    <ul>
                        {imageHistory.map((image) => (
                            <li
                                key={image.id}
                                className={selectedImage?.id === image.id ? 'selected' : ''}
                                onClick={() => onImageSelect(image)}
                            >
                                <span>{image.filename}</span>
                                <span>{new Date(image.upload_date).toLocaleString()}</span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}; 