import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';

export const CoordinateSearch = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredCoordinates, setFilteredCoordinates] = useState([]);
  const [loadingAllCoordinates, setLoadingAllCoordinates] = useState(false);
  const searchInputRef = useRef(null);

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

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredCoordinates([]);
      setSearchResults([]);
      return;
    }

    const lowerCaseSearchTerm = searchTerm.toLowerCase();

    const filtered = filteredCoordinates.filter(coord =>
      coord.name.toLowerCase().includes(lowerCaseSearchTerm) ||
      (coord.source && coord.source.toLowerCase().includes(lowerCaseSearchTerm))
    );

    const suggestions = Array.from(new Set(
      filteredCoordinates
        .filter(coord => coord.name.toLowerCase().includes(lowerCaseSearchTerm))
        .map(coord => coord.name)
    )).slice(0, 10);

    setSearchResults(suggestions);
  }, [searchTerm, filteredCoordinates]);

  const handleSelectSuggestion = (suggestion) => {
    setSearchTerm(suggestion);
    setShowSuggestions(false);

    const exactMatches = filteredCoordinates.filter(
      coord => coord.name.toLowerCase() === suggestion.toLowerCase()
    );
    setFilteredCoordinates(exactMatches);
  };

  const loadAllCoordinates = async () => {
    setLoadingAllCoordinates(true);
    try {
      const data = await api.fetchAllSavedCoordinates();
      setFilteredCoordinates(data);
    } catch (error) {
      console.error('Erro ao carregar coordenadas:', error);
    } finally {
      setLoadingAllCoordinates(false);
    }
  };

  return (
    <div className="coordinate-search">
      <div className="search-container" ref={searchInputRef}>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => {
            setShowSuggestions(true);
            loadAllCoordinates();
          }}
          placeholder="Buscar coordenadas..."
        />
        {showSuggestions && searchResults.length > 0 && (
          <ul className="suggestions">
            {searchResults.map((suggestion) => (
              <li
                key={suggestion}
                onClick={() => handleSelectSuggestion(suggestion)}
              >
                {suggestion}
              </li>
            ))}
          </ul>
        )}
      </div>

      {filteredCoordinates.length > 0 && (
        <div className="search-results">
          <h3>Resultados da Busca</h3>
          <ul>
            {filteredCoordinates.map((coord) => (
              <li key={coord.id}>
                <span>{coord.name}</span>
                <span>X: {coord.x}, Y: {coord.y}</span>
                <button onClick={() => onNavigate(coord.x, coord.y)}>
                  Navegar
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}; 