import { useState, useRef, useEffect } from 'react';
import OpenSeadragon from 'openseadragon';
import { SERVER_URL } from '../config/server';

export const useImageViewer = (activeTab) => {
    const [overlay, setOverlay] = useState(null);
    const [activeMarker, setActiveMarker] = useState(null);
    const viewerRef = useRef(null);
    const viewerInstance = useRef(null);

    const clearAllMarkers = () => {
        if (activeMarker && viewerInstance.current) {
            try {
                viewerInstance.current.removeOverlay(activeMarker);
                console.log('Marcador ativo removido');
            } catch (error) {
                console.error('Erro ao remover marcador ativo:', error);
            }
            setActiveMarker(null);
        }

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

    const initializeViewer = (imageUrl) => {
        if (viewerInstance.current) {
            clearAllMarkers();
            viewerInstance.current.destroy();
            viewerInstance.current = null;
        }

        viewerInstance.current = OpenSeadragon({
            id: "openseadragon-viewer",
            tileSources: {
                type: 'image',
                url: `${SERVER_URL}${imageUrl}`,
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

        if (activeTab === 'capture') {
            viewerInstance.current.addHandler('canvas-click', function (event) {
                const webPoint = event.position;
                const viewportPoint = viewerInstance.current.viewport.pointFromPixel(webPoint);

                clearAllMarkers();

                const marker = document.createElement('div');
                marker.className = 'coordinate-marker';
                marker.style.width = '10px';
                marker.style.height = '10px';
                marker.style.borderRadius = '50%';
                marker.style.backgroundColor = 'red';

                try {
                    const newOverlay = viewerInstance.current.addOverlay({
                        element: marker,
                        location: new OpenSeadragon.Point(viewportPoint.x, viewportPoint.y),
                        placement: OpenSeadragon.Placement.CENTER
                    });

                    setOverlay(newOverlay);
                    return {
                        x: viewportPoint.x.toFixed(3),
                        y: viewportPoint.y.toFixed(3)
                    };
                } catch (error) {
                    console.error('Erro ao adicionar marcador:', error);
                    return null;
                }
            });
        }
    };

    const navigateToCoordinates = (x, y) => {
        if (viewerInstance.current) {
            viewerInstance.current.viewport.panTo(new OpenSeadragon.Point(x, y), true);
            viewerInstance.current.viewport.zoomTo(2, new OpenSeadragon.Point(x, y), true);
        }
    };

    return {
        viewerRef,
        viewerInstance,
        overlay,
        setOverlay,
        activeMarker,
        setActiveMarker,
        clearAllMarkers,
        initializeViewer,
        navigateToCoordinates
    };
}; 