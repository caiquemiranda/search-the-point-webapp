// App.js
import React, { useState, useRef, useEffect } from 'react';
import OpenSeadragon from 'openseadragon';
import './App.css';
import { api } from './services/api';
import { useImageViewer } from './hooks/useImageViewer';
import { SavedCoordinatesList } from './components/SavedCoordinatesList';
import { ImageHistory } from './components/ImageHistory';
import { CoordinateSearch } from './components/CoordinateSearch';

// Configuração do servidor
// Lógica melhorada para ambientes de produção e desenvolvimento
const SERVER_URL = (() => {
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
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredCoordinates, setFilteredCoordinates] = useState([]);

  const {
    viewerRef,
    viewerInstance,
    overlay: imageViewerOverlay,
    setOverlay: setImageViewerOverlay,
    activeMarker: imageViewerActiveMarker,
    setActiveMarker: setImageViewerActiveMarker,
    clearAllMarkers: clearImageViewerMarkers,
    initializeViewer,
    navigateToCoordinates
  } = useImageViewer(activeTab);

  const searchInputRef = useRef(null);

  // Carrega o histórico de imagens
  useEffect(() => {
    fetchImageHistory();
    fetchAllSavedCoordinates();
  }, []);

  // Efeito para lidar com cliques fora do dropdown de sugestões
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchInputRef.current && !searchInputRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Efeito para atualizar os resultados filtrados quando o termo de busca muda
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredCoordinates(allSavedCoordinates);
      setSearchResults([]);
      return;
    }

    const lowerCaseSearchTerm = searchTerm.toLowerCase();

    // Filtrar coordenadas que correspondam ao termo de busca (no nome ou source)
    const filtered = allSavedCoordinates.filter(coord =>
      coord.name.toLowerCase().includes(lowerCaseSearchTerm) ||
      (coord.source && coord.source.toLowerCase().includes(lowerCaseSearchTerm))
    );

    setFilteredCoordinates(filtered);

    // Gerar sugestões de autocomplete (apenas nomes únicos)
    const suggestions = Array.from(new Set(
      allSavedCoordinates
        .filter(coord => coord.name.toLowerCase().includes(lowerCaseSearchTerm))
        .map(coord => coord.name)
    )).slice(0, 10); // Limitar a 10 sugestões

    setSearchResults(suggestions);
  }, [searchTerm, allSavedCoordinates]);

  const fetchImageHistory = async () => {
    try {
      const data = await api.fetchImageHistory();
      setImageHistory(data);
    } catch (error) {
      console.error('Erro ao carregar histórico de imagens:', error);
    }
  };

  // Carrega todas as coordenadas salvas
  const fetchAllSavedCoordinates = async () => {
    setLoadingAllCoordinates(true);
    try {
      console.log('Buscando todas as coordenadas salvas...');
      const data = await api.fetchAllSavedCoordinates();
      console.log(`Encontradas ${data.length} coordenadas salvas`);
      setAllSavedCoordinates(data);
      setFilteredCoordinates(data);
    } catch (error) {
      console.error('Erro ao carregar todas as coordenadas:', error);
    } finally {
      setLoadingAllCoordinates(false);
    }
  };

  // Função para selecionar uma sugestão do autocomplete
  const handleSelectSuggestion = (suggestion) => {
    setSearchTerm(suggestion);
    setShowSuggestions(false);

    // Filtrar para mostrar apenas os pontos com esse nome exato
    const exactMatches = allSavedCoordinates.filter(
      coord => coord.name.toLowerCase() === suggestion.toLowerCase()
    );
    setFilteredCoordinates(exactMatches);
  };

  // Carrega as coordenadas salvas para uma imagem
  const fetchSavedCoordinates = async (imageId) => {
    try {
      const data = await api.fetchSavedCoordinates(imageId);
      return data;
    } catch (error) {
      console.error('Erro ao carregar coordenadas salvas:', error);
      return [];
    }
  };

  const clearAllMarkers = () => {
    // Remove o marcador ativo se existir
    if (imageViewerActiveMarker && viewerInstance.current) {
      try {
        viewerInstance.current.removeOverlay(imageViewerActiveMarker);
        console.log('Marcador ativo removido');
      } catch (error) {
        console.error('Erro ao remover marcador ativo:', error);
      }
      setImageViewerActiveMarker(null);
    }

    // Remove o marcador de clique atual se existir
    if (imageViewerOverlay && viewerInstance.current) {
      try {
        viewerInstance.current.removeOverlay(imageViewerOverlay);
        console.log('Marcador de clique removido');
      } catch (error) {
        console.error('Erro ao remover marcador de clique:', error);
      }
      setImageViewerOverlay(null);
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

      initializeViewer(currentPageData.path);

      // Adiciona manipulador de evento para capturar coordenadas do mouse apenas na aba "capturar"
      if (activeTab === 'capture') {
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

            setImageViewerOverlay(newOverlay);

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
    }

    return () => {
      clearAllMarkers();
      if (viewerInstance.current) {
        viewerInstance.current.destroy();
        viewerInstance.current = null;
      }
    };
  }, [pdfData, currentPage, activeTab]);

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
    if (!coordinateName || !coordinates.x || !coordinates.y) {
      alert('Por favor, preencha todos os campos necessários.');
      return;
    }

    try {
      await api.saveCoordinate({
        name: coordinateName,
        x: parseFloat(coordinates.x),
        y: parseFloat(coordinates.y),
        source: coordinateSource,
        image_id: selectedImage?.id
      });

      setCoordinateName('');
      setCoordinateSource('');
      clearAllMarkers();
      alert('Coordenada salva com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar coordenada:', error);
      alert('Erro ao salvar coordenada. Por favor, tente novamente.');
    }
  };

  // Exportar coordenadas para CSV
  const exportCoordinatesCsv = async () => {
    try {
      const blob = await api.exportCoordinatesCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'coordenadas.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Erro ao exportar coordenadas:', error);
      alert('Erro ao exportar coordenadas. Por favor, tente novamente.');
    }
  };

  // Função para navegar até uma coordenada salva
  const navigateToSavedCoordinate = async (coord) => {
    try {
      console.log('Navegando para coordenada salva:', coord);

      // Mudar para a aba 'find' para exibir o visualizador
      setActiveTab('find');

      // Se a coordenada tem uma imagem diferente da atual, ou nenhuma imagem está carregada
      if (!pdfData || coord.image_id !== pdfData.session_id) {
        console.log('Carregando imagem associada à coordenada...');
        const imageInfo = imageHistory.find(img => img.id === coord.image_id);

        if (imageInfo) {
          // Carregar a imagem do histórico
          await loadImageFromHistory(imageInfo);
          console.log('Imagem carregada com sucesso');
        } else {
          // Se a imagem não estiver no histórico, buscar direto do servidor
          console.log('Imagem não encontrada no histórico, buscando informações do servidor...');
          try {
            const response = await fetch(`${SERVER_URL}/image-info/${coord.image_id}`);
            if (response.ok) {
              const imageData = await response.json();
              setPdfData({
                session_id: imageData.id,
                filename: imageData.filename,
                pages: Array.from({ length: imageData.page_count }, (_, i) => ({
                  page_num: i + 1,
                  path: `/images/${imageData.id}/page_${i + 1}.png`
                }))
              });
              console.log('Informações da imagem obtidas do servidor');
            } else {
              throw new Error('Falha ao buscar informações da imagem');
            }
          } catch (error) {
            console.error('Erro ao buscar imagem:', error);
            alert('Imagem associada à coordenada não encontrada. Tente carregar a imagem manualmente.');
            return;
          }
        }
      }

      // Definir a página correta
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

          setImageViewerActiveMarker(newMarker);

          // Navegar para a coordenada
          navigateToCoordinates(coord.x, coord.y);
          console.log('Navegação para coordenada concluída');
        } catch (error) {
          console.error('Erro ao adicionar marcador para coordenada salva:', error);
        }
      } else {
        console.error('Visualizador não inicializado');
      }
    } catch (error) {
      console.error('Erro ao navegar para coordenada:', error);
      alert('Houve um erro ao navegar para a coordenada selecionada');
    }
  };

  const loadImageFromHistory = async (image) => {
    try {
      setSelectedImage(image);
      setPdfData(image);
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
        <h1>Search the Point</h1>
      </header>

      <div className="tabs main-tabs">
        <button
          className={activeTab === 'capture' ? 'active' : ''}
          onClick={() => setActiveTab('capture')}
        >
          Capturar
        </button>
        <button
          className={activeTab === 'find' ? 'active' : ''}
          onClick={() => setActiveTab('find')}
        >
          Encontrar
        </button>
      </div>

      {activeTab === 'capture' && (
        <form className="upload-section" onSubmit={handleSubmit}>
          <input type="file" accept=".pdf" onChange={handleFileChange} />
          <button type="submit" disabled={loading}>
            {loading ? "Enviando..." : "Enviar"}
          </button>
          <button type="button" onClick={toggleHistory}>
            {historyOpen ? "Fechar Histórico" : "Ver Histórico"}
          </button>
          <button type="button" onClick={exportCoordinatesCsv}>Exportar CSV</button>
        </form>
      )}

      {historyOpen && activeTab === 'capture' && (
        <div className="history-sidebar">
          <h3>Histórico de Imagens</h3>
          <ul>
            {imageHistory.map((image) => (
              <li key={image.id} onClick={() => loadImageFromHistory(image)}>
                <div className="history-item">
                  <img
                    src={`${SERVER_URL}${image.thumbnail_path}`}
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

      {pdfData && activeTab === 'capture' && (
        <div className="content-container">
          <div className="viewer-container">
            <div id="openseadragon-viewer" ref={viewerRef}></div>
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
            </div>
            <div className="coordinate-info">
              <p>Clique na imagem para obter coordenadas</p>
              <p>Coordenadas atuais: ({coordinates.x}, {coordinates.y})</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'find' && (
        <div className="find-point-section">
          <h3>Ache o Ponto</h3>
          <div className="find-point-container">
            <div className="search-container" ref={searchInputRef}>
              <input
                type="text"
                className="search-input"
                placeholder="Buscar pontos salvos..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
              />
              {showSuggestions && searchResults.length > 0 && (
                <ul className="autocomplete-results">
                  {searchResults.map((result, index) => (
                    <li
                      key={index}
                      onClick={() => handleSelectSuggestion(result)}
                    >
                      {result}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {loadingAllCoordinates ? (
              <p>Carregando coordenadas...</p>
            ) : filteredCoordinates.length === 0 ? (
              <p>Nenhuma coordenada encontrada {searchTerm && `para "${searchTerm}"`}.</p>
            ) : (
              <div className="all-coordinates-list">
                <p className="coordinates-info">Clique em "Ir para o ponto" para navegar até a coordenada selecionada.</p>
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
                    {filteredCoordinates.map((coord) => (
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

          {pdfData && (
            <div className="viewer-only-container">
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
            </div>
          )}
        </div>
      )}

      <ImageHistory
        historyOpen={historyOpen}
        imageHistory={imageHistory}
        selectedImage={selectedImage}
        onImageSelect={loadImageFromHistory}
        onToggleHistory={toggleHistory}
      />
    </div>
  );
}

export default App;