import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import VacancyMap from './components/VacancyMap';
import VacancyList from './components/VacancyList';

const App: React.FC = () => {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Solid5 Vacatures
            </Typography>
            <Button color="inherit" component={Link} to="/">
              Kaart
            </Button>
            <Button color="inherit" component={Link} to="/list">
              Lijst
            </Button>
          </Toolbar>
        </AppBar>
        <Container maxWidth="xl" sx={{ mt: 4 }}>
          <Routes>
            <Route path="/" element={<VacancyMap />} />
            <Route path="/list" element={<VacancyList />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
};

export default App;
