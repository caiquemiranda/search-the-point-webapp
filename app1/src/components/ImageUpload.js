import React, { useState } from 'react';
import { MapContainer, ImageOverlay, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const ImageUpload = () => {
  const [image, setImage] = useState(null);
  const [bounds, setBounds] = useState([[0, 0], [0, 0]]);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const width = img.width;
        const height = img.height;
        setBounds([[0, 0], [height, width]]);
        setImage(e.target.result);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleImageUpload} />
      {image && (
        <MapContainer
          crs={L.CRS.Simple}
          bounds={bounds}
          style={{ height: '500px', width: '100%' }}
        >
          <ImageOverlay url={image} bounds={bounds} />
          <AddClick />
        </MapContainer>
      )}
    </div>
  );
};

const AddClick = () => {
  const map = useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      console.log(`Coordinates: ${lat}, ${lng}`);
      map.setView([lat, lng], map.getZoom() + 1); 
    },
  });
  return null;
};

export default ImageUpload;
