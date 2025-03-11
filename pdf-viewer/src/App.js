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
  const [coordinateName, setCoordinateName] = useState('');
  const [coordinateSource, setCoordinateSource] = useState('');
  const [overlay, setOverlay] = useState(null);
  const [activeMarker, setActiveMarker] = useState(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [imageHistory, setImageHistory] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [activeTab, setActiveTab] = useState('capture'); // 'capture' ou 'find'
  const [allSavedCoordinates, setAllSavedCoordinates] = useState([]);
  const [loadingAllCoordinates, setLoadingAllCoordinates] = useState(false);

  const viewerRef = useRef(null);
  const viewerInstance = useRef(null);

  // Carrega o histórico de imagens
  useEffect(() => {
    fetchImageHistory();
    fetchAllSavedCoordinates();
  }, []);

  const fetchImageHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/history');
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setImageHistory(data);
    } catch (error) {
      console.error('Erro ao carregar histórico de imagens:', error);
      // Não exibe alerta aqui para não interromper a experiência do usuário
    }
  };

  // Carrega todas as coordenadas salvas
  const fetchAllSavedCoordinates = async () => {
    setLoadingAllCoordinates(true);
    try {
      console.log('Buscando todas as coordenadas salvas...');
      const response = await fetch('http://localhost:8000/all-coordinates');
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      console.log(`Encontradas ${data.length} coordenadas salvas`);
      setAllSavedCoordinates(data);
    } catch (error) {
      console.error('Erro ao carregar todas as coordenadas:', error);
    } finally {
      setLoadingAllCoordinates(false);
    }
  };

  // Carrega as coordenadas salvas para uma imagem
  const fetchSavedCoordinates = async (imageId) => {
    try {
      const response = await fetch(`http://localhost:8000/coordinates/${imageId}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao carregar coordenadas salvas:', error);
      return [];
    }
  };

  const clearAllMarkers = () => {
    // Remove o marcador ativo se existir
    if (activeMarker && viewerInstance.current) {
      try {
        viewerInstance.current.removeOverlay(activeMarker);
        console.log('Marcador ativo removido');
      } catch (error) {
        console.error('Erro ao remover marcador ativo:', error);
      }
      setActiveMarker(null);
    }

    // Remove o marcador de clique atual se existir
    if (overlay && viewerInstance.current) {
      try {
        viewerInstance.current.removeOverlay(overlay);
        console.log('Marcador de clique removido');
      } catch (error) {
        console.error('Erro ao remover marcador de clique:', error);
      }
      setOverlay(null);
    }
  };

  useEffect(() => {
    if (pdfData && pdfData.pages.length > 0) {
      const currentPageData = pdfData.pages.find(p => p.page_num === currentPage);

      if (!currentPageData) return;

      // Limpa os marcadores antes de destruir a instância atual
      if (viewerInstance.current) {
        clearAllMarkers();
        viewerInstance.current.destroy();
        viewerInstance.current = null;
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
        maxZoomPixelRatio: 3,
        animationTime: 0.5,
        visibilityRatio: 1,
        constrainDuringPan: true
      });

      // Adiciona manipulador de evento para capturar coordenadas do mouse
      viewerInstance.current.addHandler('canvas-click', function (event) {
        const webPoint = event.position;
        const viewportPoint = viewerInstance.current.viewport.pointFromPixel(webPoint);

        // Limpar todos os marcadores existentes
        clearAllMarkers();

        // Cria um novo elemento para o marcador
        const marker = document.createElement('div');
        marker.className = 'coordinate-marker';
        marker.style.width = '10px';
        marker.style.height = '10px';
        marker.style.borderRadius = '50%';
        marker.style.backgroundColor = 'red';

        // Adiciona o novo marcador
        try {
          const newOverlay = viewerInstance.current.addOverlay({
            element: marker,
            location: new OpenSeadragon.Point(viewportPoint.x, viewportPoint.y),
            placement: OpenSeadragon.Placement.CENTER
          });

          setOverlay(newOverlay);

          // Atualiza as coordenadas com 3 casas decimais
          setCoordinates({
            x: viewportPoint.x.toFixed(3),
            y: viewportPoint.y.toFixed(3)
          });

          // Define o nome do arquivo como source padrão
          if (!coordinateSource && pdfData?.filename) {
            setCoordinateSource(pdfData.filename);
          }
        } catch (error) {
          console.error('Erro ao adicionar marcador:', error);
        }
      });
    }

    return () => {
      clearAllMarkers();
      if (viewerInstance.current) {
        viewerInstance.current.destroy();
        viewerInstance.current = null;
      }
    };
  }, [pdfData, currentPage]);

  // Evento para prevenir erros quando o componente é desmontado
  useEffect(() => {
    return () => {
      // Limpa os marcadores e estados
      if (viewerInstance.current) {
        clearAllMarkers();
        viewerInstance.current.destroy();
        viewerInstance.current = null;
      }
    };
  }, []);

  // Função para salvar coordenadas no banco de dados
  const saveCoordinate = async () => {
    if (!coordinates.x || !coordinates.y || !coordinateName || !pdfData) {
      alert('Por favor, selecione um ponto e dê um nome para a coordenada');
      return;
    }

    try {
      console.log('Enviando coordenada para o servidor:', {
        name: coordinateName,
        x: parseFloat(coordinates.x),
        y: parseFloat(coordinates.y),
        page: currentPage,
        source: coordinateSource || pdfData.filename
      });

      const response = await fetch(`http://localhost:8000/coordinates/${pdfData.session_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: coordinateName,
          x: parseFloat(coordinates.x),
          y: parseFloat(coordinates.y),
          page: currentPage,
          source: coordinateSource || pdfData.filename
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      alert('Coordenada salva com sucesso!');
      setCoordinateName('');

      // Limpa o marcador após salvar
      console.log('Limpando marcadores após salvar coordenada');
      clearAllMarkers();

      // Atualiza o estado de todas as coordenadas salvas
      fetchAllSavedCoordinates();

      // Atualiza a lista de coordenadas salvas se estiver usando o componente SavedCoordinatesList
      if (pdfData?.session_id) {
        const savedCoordinatesListElement = document.querySelector('.saved-coordinates');
        if (savedCoordinatesListElement) {
          // Dispara um evento personalizado para notificar o componente SavedCoordinatesList
          const event = new CustomEvent('coordinateAdded', { detail: { imageId: pdfData.session_id } });
          savedCoordinatesListElement.dispatchEvent(event);
        }
      }
    } catch (error) {
      console.error('Erro ao salvar coordenada:', error);
      alert(`Erro ao salvar coordenada: ${error.message || 'Falha na conexão com o servidor'}`);
    }
  };

  // Exportar coordenadas para CSV
  const exportCoordinatesCsv = async () => {
    if (!pdfData || !pdfData.session_id) {
      alert('Nenhuma imagem carregada');
      return;
    }

    try {
      window.open(`http://localhost:8000/coordinates/export/${pdfData.session_id}`, '_blank');
    } catch (error) {
      console.error('Erro ao exportar coordenadas:', error);
      alert(`Erro ao exportar coordenadas: ${error.message || 'Falha na conexão com o servidor'}`);
    }
  };

  // Função para navegar até uma coordenada salva
  const navigateToSavedCoordinate = async (coord) => {
    // Se a coordenada tem uma imagem diferente da atual, precisamos carregar essa imagem primeiro
    if (coord.image_id && (!pdfData || coord.image_id !== pdfData.session_id)) {
      const imageInfo = imageHistory.find(img => img.id === coord.image_id);
      if (imageInfo) {
        await loadImageFromHistory(imageInfo);
      } else {
        alert('Imagem associada à coordenada não encontrada no histórico');
        return;
      }
    }

    setCurrentPage(coord.page);
    setCoordinates({ x: coord.x.toString(), y: coord.y.toString() });

    // Esperar pela atualização da página, se necessário
    await new Promise(resolve => setTimeout(resolve, 300));

    // Mostrar marcador
    if (viewerInstance.current) {
      // Limpar marcadores anteriores
      clearAllMarkers();

      // Criar novo marcador
      const marker = document.createElement('div');
      marker.className = 'saved-coordinate-marker';
      marker.style.width = '10px';
      marker.style.height = '10px';
      marker.style.borderRadius = '50%';
      marker.style.backgroundColor = 'green';
      marker.title = coord.name;

      try {
        // Adicionar novo marcador
        const newMarker = viewerInstance.current.addOverlay({
          element: marker,
          location: new OpenSeadragon.Point(parseFloat(coord.x), parseFloat(coord.y)),
          placement: OpenSeadragon.Placement.CENTER
        });

        setActiveMarker(newMarker);

        // Navegar para a coordenada
        navigateToCoordinates(coord.x, coord.y);
      } catch (error) {
        console.error('Erro ao adicionar marcador para coordenada salva:', error);
      }
    }
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
    viewerInstance.current.viewport.zoomTo(5.5);
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Por favor, selecione um arquivo PDF.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload-pdf/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setPdfData(data);
      setCurrentPage(1);

      // Define o nome do arquivo como source padrão
      if (data.filename) {
        setCoordinateSource(data.filename);
      }

      // Atualiza o histórico após upload
      fetchImageHistory();
      fetchAllSavedCoordinates();
    } catch (error) {
      console.error("Erro ao fazer upload do PDF:", error);
      alert(`Erro ao processar o PDF: ${error.message || 'Falha na conexão com o servidor'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadImageFromHistory = async (image) => {
    try {
      setSelectedImage(image);
      setPdfData({
        session_id: image.id,
        filename: image.filename,
        pages: Array.from({ length: image.page_count }, (_, i) => ({
          page_num: i + 1,
          path: `/images/${image.id}/page_${i + 1}.png`
        }))
      });
      setCurrentPage(1);
      setHistoryOpen(false);

      // Define o nome do arquivo como source padrão
      setCoordinateSource(image.filename);

      // Limpa marcadores anteriores
      clearAllMarkers();
    } catch (error) {
      console.error('Erro ao carregar imagem do histórico:', error);
    }
  };

  const nextPage = () => {
    if (pdfData && currentPage < pdfData.pages.length) {
      setCurrentPage(currentPage + 1);
      // Limpa marcadores ao trocar de página
      clearAllMarkers();
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      // Limpa marcadores ao trocar de página
      clearAllMarkers();
    }
  };

  const toggleHistory = () => {
    setHistoryOpen(!historyOpen);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Visualizador de PDF com Coordenadas</h1>
      </header>

      <form className="upload-section" onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <button type="submit" disabled={loading}>
          {loading ? "Processando..." : "Processar PDF"}
        </button>
        <button type="button" onClick={toggleHistory}>
          {historyOpen ? "Fechar Histórico" : "Ver Histórico"}
        </button>
      </form>

      {historyOpen && (
        <div className="history-sidebar">
          <h3>Histórico de Imagens</h3>
          <ul>
            {imageHistory.map((image) => (
              <li key={image.id} onClick={() => loadImageFromHistory(image)}>
                <div className="history-item">
                  <img
                    src={`http://localhost:8000${image.thumbnail_path}`}
                    alt={image.filename}
                    className="history-thumbnail"
                  />
                  <div className="history-info">
                    <p className="history-filename">{image.filename}</p>
                    <p className="history-date">
                      {new Date(image.upload_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {pdfData && (
        <div className="content-container">
          <div className="viewer-container">
            <div id="openseadragon-viewer"></div>
            <div className="viewer-controls">
              <button id="zoom-in">+</button>
              <button id="zoom-out">-</button>
              <button id="home">⌂</button>
              <button id="full-page">⤢</button>
            </div>
            <div className="pagination">
              <button onClick={prevPage} disabled={currentPage === 1}>Anterior</button>
              <span>Página {currentPage} de {pdfData.pages.length}</span>
              <button onClick={nextPage} disabled={currentPage === pdfData.pages.length}>Próxima</button>
            </div>
          </div>

          <div className="coordinates-panel">
            <div className="tabs">
              <button
                className={activeTab === 'capture' ? 'active' : ''}
                onClick={() => setActiveTab('capture')}
              >
                Capturar Coordenadas
              </button>
              <button
                className={activeTab === 'find' ? 'active' : ''}
                onClick={() => setActiveTab('find')}
              >
                Ache o Ponto
              </button>
            </div>

            {activeTab === 'capture' && (
              <>
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
                  <button onClick={() => navigateToCoordinates()}>Navegar</button>
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
                  <button onClick={saveCoordinate}>Salvar Coordenada</button>
                  <button onClick={exportCoordinatesCsv} className="export-btn">Exportar CSV</button>
                </div>
                <SavedCoordinatesList
                  imageId={pdfData?.session_id}
                  onNavigate={navigateToSavedCoordinate}
                />
                <div className="coordinate-info">
                  <p>Clique na imagem para obter coordenadas</p>
                  <p>Coordenadas atuais: ({coordinates.x}, {coordinates.y})</p>
                </div>
              </>
            )}

            {activeTab === 'find' && (
              <>
                <h3>Ache o Ponto</h3>
                <div className="find-point-container">
                  {loadingAllCoordinates ? (
                    <p>Carregando coordenadas...</p>
                  ) : allSavedCoordinates.length === 0 ? (
                    <p>Nenhuma coordenada salva encontrada.</p>
                  ) : (
                    <div className="all-coordinates-list">
                      <table>
                        <thead>
                          <tr>
                            <th>Nome</th>
                            <th>Fonte</th>
                            <th>Coordenadas</th>
                            <th>Ação</th>
                          </tr>
                        </thead>
                        <tbody>
                          {allSavedCoordinates.map((coord) => (
                            <tr key={coord.id}>
                              <td>{coord.name}</td>
                              <td>{coord.source || "Desconhecido"}</td>
                              <td>({coord.x}, {coord.y})</td>
                              <td>
                                <button
                                  className="go-to-point-btn"
                                  onClick={() => navigateToSavedCoordinate(coord)}
                                >
                                  Ir para o ponto
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Componente para listar coordenadas salvas
function SavedCoordinatesList({ imageId, onNavigate }) {
  const [coordinates, setCoordinates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const coordListRef = useRef(null);

  useEffect(() => {
    if (imageId) {
      fetchCoordinates();
    }
  }, [imageId]);

  useEffect(() => {
    // Adiciona event listener para o evento customizado
    const handleCoordinateAdded = () => {
      fetchCoordinates();
    };

    const coordListElement = coordListRef.current;
    if (coordListElement) {
      coordListElement.addEventListener('coordinateAdded', handleCoordinateAdded);
    }

    return () => {
      if (coordListElement) {
        coordListElement.removeEventListener('coordinateAdded', handleCoordinateAdded);
      }
    };
  }, []);

  const fetchCoordinates = async () => {
    if (!imageId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/coordinates/${imageId}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setCoordinates(data);
    } catch (error) {
      console.error('Erro ao buscar coordenadas:', error);
      setError('Não foi possível carregar as coordenadas salvas.');
    } finally {
      setLoading(false);
    }
  };

  const deleteCoordinate = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta coordenada?')) {
      try {
        const response = await fetch(`http://localhost:8000/coordinates/${id}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`);
        }

        // Atualiza a lista após excluir
        fetchCoordinates();
      } catch (error) {
        console.error('Erro ao excluir coordenada:', error);
        alert(`Erro ao excluir coordenada: ${error.message || 'Falha na conexão com o servidor'}`);
      }
    }
  };

  if (loading) {
    return <div className="saved-coordinates" ref={coordListRef}><p>Carregando coordenadas...</p></div>;
  }

  if (error) {
    return <div className="saved-coordinates" ref={coordListRef}><p className="error-message">{error}</p></div>;
  }

  return (
    <div className="saved-coordinates" ref={coordListRef}>
      <h4>Coordenadas Salvas:</h4>
      {coordinates.length === 0 ? (
        <p>Nenhuma coordenada salva para esta imagem.</p>
      ) : (
        <ul>
          {coordinates.map((coord) => (
            <li key={coord.id}>
              <span>
                {coord.name} ({coord.x}, {coord.y})
                <small className="source-text">{coord.source}</small>
              </span>
              <div>
                <button onClick={() => onNavigate(coord)}>Ir para ponto</button>
                <button
                  className="delete-btn"
                  onClick={() => deleteCoordinate(coord.id)}
                >
                  Excluir
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;