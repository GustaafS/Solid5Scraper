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
  municipality_id: number;
  description: string;
  function_category: string;
  education_level: string;
}

interface Municipality {
  id: number;
  name: string;
}

const VacancyList: React.FC = () => {
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
  const [loading, setLoading] = useState(true);
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

        const vacanciesData = await vacanciesResponse.json();
        const municipalitiesData = await municipalitiesResponse.json();

        setVacancies(vacanciesData);
        setMunicipalities(municipalitiesData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredVacancies = vacancies.filter((vacancy) => {
    const matchesSearch = vacancy.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vacancy.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || vacancy.function_category === selectedCategory;
    const matchesEducation = !selectedEducationLevel || vacancy.education_level === selectedEducationLevel;

    return matchesSearch && matchesCategory && matchesEducation;
  });

  const uniqueCategories = Array.from(new Set(vacancies.map(v => v.function_category)));
  const uniqueEducationLevels = Array.from(new Set(vacancies.map(v => v.education_level)));

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
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
        {filteredVacancies.map((vacancy) => {
          const municipality = municipalities.find(m => m.id === vacancy.municipality_id);
          return (
            <Box key={vacancy.id} flex={1} minWidth={300}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {vacancy.title}
                  </Typography>
                  <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                    {municipality?.name}
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {vacancy.description.length > 150
                      ? `${vacancy.description.substring(0, 150)}...`
                      : vacancy.description}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Functiecategorie: {vacancy.function_category}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Opleidingsniveau: {vacancy.education_level}
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
        })}
      </Box>
    </Box>
  );
};

export default VacancyList; 