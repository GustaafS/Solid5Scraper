import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Breadcrumbs,
  Link,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

interface Vacancy {
  id: number;
  title: string;
  municipality_id: string;
  description: string;
  function_category: string;
  education_level: string;
}

interface Municipality {
  id: string;
  name: string;
}

const VacancyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [vacancy, setVacancy] = useState<Vacancy | null>(null);
  const [municipality, setMunicipality] = useState<Municipality | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Haal de vacature op
        const vacancyResponse = await fetch(`http://localhost:8000/api/vacancies/${id}`);
        if (!vacancyResponse.ok) {
          throw new Error('Vacature niet gevonden');
        }
        const vacancyData = await vacancyResponse.json();
        setVacancy(vacancyData);

        // Haal de gemeente op
        const municipalityResponse = await fetch(`http://localhost:8000/api/municipalities/${vacancyData.municipality_id}`);
        if (municipalityResponse.ok) {
          const municipalityData = await municipalityResponse.json();
          setMunicipality(municipalityData);
        }
      } catch (error) {
        console.error('Error fetching vacancy:', error);
        setError(error instanceof Error ? error.message : 'Er is een fout opgetreden');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !vacancy) {
    return (
      <Box p={3}>
        <Typography color="error" variant="h6">
          {error || 'Vacature niet gevonden'}
        </Typography>
        <Button component={RouterLink} to="/" color="primary" sx={{ mt: 2 }}>
          Terug naar overzicht
        </Button>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
        <Link component={RouterLink} to="/" color="inherit">
          Vacatures
        </Link>
        <Typography color="text.primary">{vacancy.title}</Typography>
      </Breadcrumbs>

      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            {vacancy.title}
          </Typography>
          
          <Typography variant="h6" color="textSecondary" gutterBottom>
            {municipality?.name || 'Onbekende gemeente'}
          </Typography>

          <Box my={3}>
            <Typography variant="body1" paragraph>
              {vacancy.description}
            </Typography>
          </Box>

          <Box mb={3}>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Functiecategorie:</strong> {vacancy.function_category || 'Niet gespecificeerd'}
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Opleidingsniveau:</strong> {vacancy.education_level || 'Niet gespecificeerd'}
            </Typography>
          </Box>

          <Button
            variant="contained"
            color="primary"
            component={RouterLink}
            to="/"
          >
            Terug naar overzicht
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default VacancyDetail; 