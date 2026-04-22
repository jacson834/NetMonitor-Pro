import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import './App.css'; // Assume dark theme estilos básicos

function App() {
  return (
    <BrowserRouter>
      <div className="app-container dark-theme">
        <nav className="sidebar">
          <h2>NetMonitor Pro</h2>
          <Link to="/">Dashboard (Live)</Link>
          <Link to="/history">Histórico</Link>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
export default App;