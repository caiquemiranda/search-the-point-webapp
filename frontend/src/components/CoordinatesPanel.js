import React from 'react';

export const CoordinatesPanel = ({
  coordinates,
  setCoordinates,
  coordinateName,
  setCoordinateName,
  coordinateSource,
  setCoordinateSource,
  onNavigate,
  onSaveCoordinate
}) => {
  return (
    <div className="coordinates-panel">
      <h3>Captura de Coordenadas</h3>
      <div>
        <label>
          X:
          <input
            type="text"
            value={coordinates.x}
            onChange={(e) => setCoordinates({ ...coordinates, x: e.target.value })}
          />
        </label>
        <label>
          Y:
          <input
            type="text"
            value={coordinates.y}
            onChange={(e) => setCoordinates({ ...coordinates, y: e.target.value })}
          />
        </label>
        <button onClick={() => onNavigate()}>Navegar</button>
      </div>
      <div className="coordinate-save">
        <input
          type="text"
          value={coordinateName}
          onChange={(e) => setCoordinateName(e.target.value)}
          placeholder="Nome do ponto"
        />
        <input
          type="text"
          value={coordinateSource}
          onChange={(e) => setCoordinateSource(e.target.value)}
          placeholder="Fonte/origem da imagem"
        />
        <button onClick={onSaveCoordinate}>Salvar Coordenada</button>
      </div>
      <div className="coordinate-info">
        <p>Clique na imagem para obter coordenadas</p>
        <p>Coordenadas atuais: ({coordinates.x}, {coordinates.y})</p>
      </div>
    </div>
  );
}; 