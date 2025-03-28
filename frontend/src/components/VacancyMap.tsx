import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Typography, Link, CircularProgress, Box } from '@mui/material';

interface Municipality {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

interface Vacancy {
  id: number;
  title: string;
  municipality_id: string;
  description: string;
  function_category: string;
  education_level: string;
}

const VacancyMap: React.FC = () => {
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const municipalitiesResponse = await fetch('http://localhost:8000/api/municipalities');
        const vacanciesResponse = await fetch('http://localhost:8000/api/vacancies');
        const geoJsonResponse = await fetch('/data/gemeentekaart.geojson');

        if (!municipalitiesResponse.ok) {
          throw new Error(`Failed to fetch municipalities: ${municipalitiesResponse.statusText}`);
        }

        if (!vacanciesResponse.ok) {
          throw new Error(`Failed to fetch vacancies: ${vacanciesResponse.statusText}`);
        }

        if (!geoJsonResponse.ok) {
          throw new Error(`Failed to fetch GeoJSON data: ${geoJsonResponse.statusText}`);
        }

        const municipalitiesData = await municipalitiesResponse.json();
        const vacanciesData = await vacanciesResponse.json();
        const geoJsonData = await geoJsonResponse.json();

        if (!Array.isArray(municipalitiesData)) {
          throw new Error('Invalid municipalities data format');
        }

        if (!Array.isArray(vacanciesData)) {
          throw new Error('Invalid vacancies data format');
        }

        setMunicipalities(municipalitiesData);
        setVacancies(vacanciesData);
        setGeoJsonData(geoJsonData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(error instanceof Error ? error.message : 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getMunicipalityVacancies = (statcode: string) => {
    return vacancies.filter((vacancy) => vacancy.municipality_id === statcode);
  };

  const style = (feature: any) => {
    const municipalityId = feature.properties.statcode;
    const municipalityVacancies = getMunicipalityVacancies(municipalityId);
    
    return {
      fillColor: municipalityVacancies.length > 0 ? '#4CAF50' : '#ccc',
      weight: 1,
      opacity: 1,
      color: '#666',
      fillOpacity: 0.7
    };
  };

  const onEachFeature = (feature: any, layer: any) => {
    const municipalityId = feature.properties.statcode;
    const municipalityVacancies = getMunicipalityVacancies(municipalityId);
    
    layer.on({
      mouseover: (e: any) => {
        const layer = e.target;
        layer.setStyle({
          fillOpacity: 0.9,
          weight: 2
        });
      },
      mouseout: (e: any) => {
        const layer = e.target;
        layer.setStyle({
          fillOpacity: 0.7,
          weight: 1
        });
      }
    });

    layer.bindPopup(`
      <div>
        <h3>${feature.properties.statnaam}</h3>
        <p>Aantal vacatures: ${municipalityVacancies.length}</p>
        ${municipalityVacancies.slice(0, 3).map((vacancy: Vacancy) => `
          <div>
            <a href="/vacancy/${vacancy.id}">${vacancy.title}</a>
          </div>
        `).join('')}
      </div>
    `);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Typography color="error">Error: {error}</Typography>
      </Box>
    );
  }

  if (!geoJsonData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Typography>Geen kaartdata gevonden</Typography>
      </Box>
    );
  }

  return (
    <MapContainer
      center={[52.1326, 5.2913]}
      zoom={8}
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <GeoJSON
        data={geoJsonData}
        style={style}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  );
};

export default VacancyMap; 