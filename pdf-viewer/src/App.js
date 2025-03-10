// App.js
import React, { useState, useRef, useEffect } from 'react';
import OpenSeadragon from 'openseadragon';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfData, setPdfData] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [coordinates, setCoordinates] = useState({ x: '', y: '' });
  const [savedCoordinates, setSavedCoordinates] = useState([]);
  const [coordinateName, setCoordinateName] = useState('');
  const [overlay, setOverlay] = useState(null);

  const viewerRef = useRef(null);
  const viewerInstance = useRef(null);

  // Inicializa ou atualiza o visualizador OpenSeadragon
  useEffect(() => {
    if (pdfData && pdfData.pages.length > 0) {
      const currentPageData = pdfData.pages.find(p => p.page_num === currentPage);

      if (!currentPageData) return;

      if (viewerInstance.current) {
        viewerInstance.current.destroy();
      }

      viewerInstance.current = OpenSeadragon({
        id: "openseadragon-viewer",
        tileSources: {
          type: 'image',
          url: `http://localhost:8000${currentPageData.path}`,
          buildPyramid: false
        },
        showNavigationControl: true,
        navigatorPosition: "BOTTOM_RIGHT",
        zoomInButton: "zoom-in",
        zoomOutButton: "zoom-out",
        homeButton: "home",
        fullPageButton: "full-page",
        maxZoomPixelRatio: 5,
        animationTime: 0.5,
        visibilityRatio: 1,
        constrainDuringPan: true
      });

      // Adiciona manipulador de evento para capturar coordenadas do mouse
      viewerInstance.current.addHandler('canvas-click', function (event) {
        const webPoint = event.position;
        const viewportPoint = viewerInstance.current.viewport.pointFromPixel(webPoint);

        // Remove marcador anterior se existir
        if (overlay) {
          viewerInstance.current.removeOverlay(overlay);
        }

        // Cria um novo elemento para o marcador
        const marker = document.createElement('div');
        marker.className = 'coordinate-marker';
        marker.style.width = '20px';
        marker.style.height = '20px';
        marker.style.borderRadius = '50%';
        marker.style.backgroundColor = 'red';

        // Adiciona o novo marcador
        const newOverlay = viewerInstance.current.addOverlay({
          element: marker,
          location: new OpenSeadragon.Point(viewportPoint.x, viewportPoint.y),
          placement: OpenSeadragon.Placement.CENTER
        });

        setOverlay(newOverlay);

        // Atualiza as coordenadas
        setCoordinates({
          x: viewportPoint.x.toFixed(4),
          y: viewportPoint.y.toFixed(4)
        });
      });

      // Renderiza marcadores salvos
      savedCoordinates.forEach(coord => {
        const marker = document.createElement('div');
        marker.className = 'saved-coordinate-marker';
        marker.style.width = '20px';
        marker.style.height = '20px';
        marker.style.borderRadius = '50%';
        marker.style.backgroundColor = 'blue';
        marker.title = coord.name;

        viewerInstance.current.addOverlay({
          element: marker,
          location: new OpenSeadragon.Point(parseFloat(coord.x), parseFloat(coord.y)),
          placement: OpenSeadragon.Placement.CENTER
        });
      });
    }

    return () => {
      if (viewerInstance.current) {
        viewerInstance.current.destroy();
      }
    };
  }, [pdfData, currentPage, savedCoordinates]);

  // Função para salvar coordenadas
  const saveCoordinate = () => {
    if (!coordinates.x || !coordinates.y || !coordinateName) {
      alert('Por favor, selecione um ponto e dê um nome para a coordenada');
      return;
    }

    const newCoordinate = {
      name: coordinateName,
      x: coordinates.x,
      y: coordinates.y,
      page: currentPage
    };

    setSavedCoordinates([...savedCoordinates, newCoordinate]);
    setCoordinateName('');
  };

  // Função para navegar até uma coordenada salva
  const navigateToSavedCoordinate = (coord) => {
    setCurrentPage(coord.page);
    setCoordinates({ x: coord.x, y: coord.y });
    navigateToCoordinates(coord.x, coord.y);
  };

  // Função para navegar até coordenadas específicas
  const navigateToCoordinates = (x = coordinates.x, y = coordinates.y) => {
    if (!viewerInstance.current) return;

    const xCoord = parseFloat(x);
    const yCoord = parseFloat(y);

    if (isNaN(xCoord) || isNaN(yCoord)) {
      alert("Coordenadas inválidas");
      return;
    }

    viewerInstance.current.viewport.panTo(new OpenSeadragon.Point(xCoord, yCoord));
    viewerInstance.current.viewport.zoomTo(6.0);
  };

  // Upload e processamento do PDF
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Por favor, selecione um arquivo PDF");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload-pdf/", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Falha ao fazer upload do PDF");
      }

      const data = await response.json();
      setPdfData(data);
      setCurrentPage(1);
    } catch (error) {
      console.error("Erro:", error);
      alert("Ocorreu um erro ao processar o PDF");
    } finally {
      setLoading(false);
    }
  };

  // Navegação entre páginas
  const nextPage = () => {
    if (pdfData && currentPage < pdfData.pages.length) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Visualizador de PDF com Navegação por Coordenadas</h1>
      </header>

      <div className="upload-section">
        <form onSubmit={handleSubmit}>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf"
          />
          <button type="submit" disabled={loading || !file}>
            {loading ? "Processando..." : "Enviar PDF"}
          </button>
        </form>
      </div>

      {pdfData && (
        <div className="content-container">
          <div className="viewer-container">
            <div id="openseadragon-viewer" ref={viewerRef}></div>
            <div className="viewer-controls">
              <button id="zoom-in">Zoom +</button>
              <button id="zoom-out">Zoom -</button>
              <button id="home">Resetar</button>
              <button id="full-page">Tela Cheia</button>

              <div className="pagination">
                <button onClick={prevPage} disabled={currentPage === 1}>
                  Anterior
                </button>
                <span>Página {currentPage} de {pdfData.pages.length}</span>
                <button onClick={nextPage} disabled={currentPage === pdfData.pages.length}>
                  Próxima
                </button>
              </div>
            </div>
          </div>

          <div className="coordinates-panel">
            <h3>Navegação por Coordenadas</h3>
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
              <button onClick={() => navigateToCoordinates()}>Navegar</button>
            </div>
            <div className="coordinate-save">
              <input
                type="text"
                value={coordinateName}
                onChange={(e) => setCoordinateName(e.target.value)}
                placeholder="Nome do ponto"
              />
              <button onClick={saveCoordinate}>Salvar Coordenada</button>
            </div>
            <div className="saved-coordinates">
              <h4>Coordenadas Salvas:</h4>
              <ul>
                {savedCoordinates.map((coord, index) => (
                  <li key={index}>
                    {coord.name} ({coord.x}, {coord.y})
                    <button onClick={() => navigateToSavedCoordinate(coord)}>
                      Ir para ponto
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div className="coordinate-info">
              <p>Clique na imagem para obter coordenadas</p>
              <p>Coordenadas atuais: ({coordinates.x}, {coordinates.y})</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;