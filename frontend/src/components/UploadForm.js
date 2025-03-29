import React from 'react';

export const UploadForm = ({
    loading,
    onFileChange,
    onSubmit,
    onToggleHistory,
    onExportCsv,
    historyOpen
}) => {
    return (
        <form className="upload-section" onSubmit={onSubmit}>
            <input type="file" accept=".pdf" onChange={onFileChange} />
            <button type="submit" disabled={loading}>
                {loading ? "Enviando..." : "Enviar"}
            </button>
            <button type="button" onClick={onToggleHistory}>
                {historyOpen ? "Fechar Histórico" : "Ver Histórico"}
            </button>
            <button type="button" onClick={onExportCsv}>Exportar CSV</button>
        </form>
    );
}; 