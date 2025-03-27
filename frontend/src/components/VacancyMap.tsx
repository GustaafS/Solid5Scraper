import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Typography, Link, CircularProgress, Box } from '@mui/material';

// Fix voor Leaflet marker iconen
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface Municipality {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

interface Vacancy {
  id: number;
  title: string;
  municipality_id: number;
  description: string;
  function_category: string;
  education_level: string;
}

const VacancyMap: React.FC = () => {
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const municipalitiesResponse = await fetch('http://localhost:8000/api/municipalities');
        const vacanciesResponse = await fetch('http://localhost:8000/api/vacancies');

        if (!municipalitiesResponse.ok) {
          throw new Error(`Failed to fetch municipalities: ${municipalitiesResponse.statusText}`);
        }

        if (!vacanciesResponse.ok) {
          throw new Error(`Failed to fetch vacancies: ${vacanciesResponse.statusText}`);
        }

        const municipalitiesData = await municipalitiesResponse.json();
        const vacanciesData = await vacanciesResponse.json();

        if (!Array.isArray(municipalitiesData)) {
          throw new Error('Invalid municipalities data format');
        }

        if (!Array.isArray(vacanciesData)) {
          throw new Error('Invalid vacancies data format');
        }

        // Filter gemeenten zonder coördinaten
        const validMunicipalities = municipalitiesData.filter(m => m.latitude !== null && m.longitude !== null);
        setMunicipalities(validMunicipalities);
        setVacancies(vacanciesData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(error instanceof Error ? error.message : 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  if (!municipalities.length) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Typography>Geen gemeentes gevonden</Typography>
      </Box>
    );
  }

  return (
    <MapContainer
      center={[52.1326, 5.2913]} // Centrum van Nederland
      zoom={8}
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {municipalities.map((municipality) => {
        const municipalityVacancies = vacancies.filter(
          (vacancy) => vacancy.municipality_id === municipality.id
        );

        return (
          <Marker
            key={municipality.id}
            position={[municipality.latitude, municipality.longitude]}
          >
            <Popup>
              <Typography variant="h6">{municipality.name}</Typography>
              <Typography variant="body2">
                Aantal vacatures: {municipalityVacancies.length}
              </Typography>
              {municipalityVacancies.slice(0, 3).map((vacancy) => (
                <Box key={vacancy.id} mt={1}>
                  <Link href={`/vacancy/${vacancy.id}`} color="primary">
                    {vacancy.title}
                  </Link>
                </Box>
              ))}
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
};

export default VacancyMap; 