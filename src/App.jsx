import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';
import AllItemsPage from './AllItemsPage';
import UploadImage from './UploadImage';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/all-items" element={<AllItemsPage />} />
                <Route path="/upload-image" element={<UploadImage />} />
            </Routes>
        </Router>
    );
}

export default App;