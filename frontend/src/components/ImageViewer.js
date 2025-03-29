import React from 'react';

export const ImageViewer = ({
  viewerRef,
  currentPage,
  totalPages,
  onPrevPage,
  onNextPage
}) => {
  return (
    <div className="viewer-container">
      <div id="openseadragon-viewer" ref={viewerRef}></div>
      <div className="viewer-controls">
        <button id="zoom-in">+</button>
        <button id="zoom-out">-</button>
        <button id="home">⌂</button>
        <button id="full-page">⤢</button>
      </div>
      <div className="pagination">
        <button onClick={onPrevPage} disabled={currentPage === 1}>
          Anterior
        </button>
        <span>Página {currentPage} de {totalPages}</span>
        <button onClick={onNextPage} disabled={currentPage === totalPages}>
          Próxima
        </button>
      </div>
    </div>
  );
}; 