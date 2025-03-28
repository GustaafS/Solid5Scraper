import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  CircularProgress,
} from '@mui/material';

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

const VacancyList: React.FC = () => {
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedEducationLevel, setSelectedEducationLevel] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [vacanciesResponse, municipalitiesResponse] = await Promise.all([
          fetch('http://localhost:8000/api/vacancies'),
          fetch('http://localhost:8000/api/municipalities')
        ]);

        if (!vacanciesResponse.ok || !municipalitiesResponse.ok) {
          throw new Error('Failed to fetch data');
        }

        const vacanciesData = await vacanciesResponse.json();
        const municipalitiesData = await municipalitiesResponse.json();

        if (!Array.isArray(vacanciesData)) {
          setVacancies([]);
        } else {
          setVacancies(vacanciesData);
        }

        if (!Array.isArray(municipalitiesData)) {
          setMunicipalities([]);
        } else {
          setMunicipalities(municipalitiesData);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(error instanceof Error ? error.message : 'An error occurred');
        setVacancies([]);
        setMunicipalities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredVacancies = vacancies.filter((vacancy) => {
    const matchesSearch = (vacancy.title?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (vacancy.description?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || vacancy.function_category === selectedCategory;
    const matchesEducation = !selectedEducationLevel || vacancy.education_level === selectedEducationLevel;

    return matchesSearch && matchesCategory && matchesEducation;
  });

  const uniqueCategories = Array.from(new Set(vacancies.filter(v => v.function_category).map(v => v.function_category)));
  const uniqueEducationLevels = Array.from(new Set(vacancies.filter(v => v.education_level).map(v => v.education_level)));

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

  return (
    <Box p={3}>
      <Box mb={3}>
        <Box display="flex" flexWrap="wrap" gap={2}>
          <Box flex={1} minWidth={200}>
            <TextField
              fullWidth
              label="Zoeken"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Box>
          <Box flex={1} minWidth={200}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Functiecategorie</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value as string)}
                label="Functiecategorie"
              >
                <MenuItem value="">Alle categorieën</MenuItem>
                {uniqueCategories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
          <Box flex={1} minWidth={200}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Opleidingsniveau</InputLabel>
              <Select
                value={selectedEducationLevel}
                onChange={(e) => setSelectedEducationLevel(e.target.value as string)}
                label="Opleidingsniveau"
              >
                <MenuItem value="">Alle niveaus</MenuItem>
                {uniqueEducationLevels.map((level) => (
                  <MenuItem key={level} value={level}>
                    {level}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Box>

      <Box display="flex" flexWrap="wrap" gap={2}>
        {filteredVacancies.length === 0 ? (
          <Typography variant="body1" color="textSecondary">
            Geen vacatures gevonden
          </Typography>
        ) : (
          filteredVacancies.map((vacancy) => {
            const municipality = municipalities.find(m => m.id === vacancy.municipality_id);
            return (
              <Box key={vacancy.id} flex={1} minWidth={300}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {vacancy.title}
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                      {municipality?.name || 'Onbekende gemeente'}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {vacancy.description && vacancy.description.length > 150
                        ? `${vacancy.description.substring(0, 150)}...`
                        : vacancy.description}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Functiecategorie: {vacancy.function_category || 'Niet gespecificeerd'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Opleidingsniveau: {vacancy.education_level || 'Niet gespecificeerd'}
                    </Typography>
                    <Box mt={2}>
                      <Button
                        variant="contained"
                        color="primary"
                        href={`/vacancy/${vacancy.id}`}
                      >
                        Bekijk vacature
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            );
          })
        )}
      </Box>
    </Box>
  );
};

export default VacancyList; 