import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';
import AllItemsPage from './AllItemsPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/all-items" element={<AllItemsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
