import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, Container, CssBaseline } from '@mui/material';
import VacancyList from './components/VacancyList';
import VacancyMap from './components/VacancyMap';
import VacancyDetail from './components/VacancyDetail';

const App: React.FC = () => {
  return (
    <Router>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Container maxWidth={false} sx={{ flex: 1, p: 0 }}>
          <Routes>
            <Route path="/" element={
              <Box sx={{ display: 'flex', height: '100vh' }}>
                <Box sx={{ flex: 1 }}>
                  <VacancyMap />
                </Box>
                <Box sx={{ flex: 1, overflowY: 'auto' }}>
                  <VacancyList />
                </Box>
              </Box>
            } />
            <Route path="/vacancy/:id" element={<VacancyDetail />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
};

export default App;
