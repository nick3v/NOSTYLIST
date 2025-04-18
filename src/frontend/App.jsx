import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './dashboard';
import AllItemsPage from './AllItemsPage';
import UploadImage from './UploadImage';
import PreviousFits from './PreviousFits';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/all-items" element={<AllItemsPage />} />
                <Route path="/upload-image" element={<UploadImage />} />
                <Route path="/previous-fits" element={<PreviousFits />} />
            </Routes>
        </Router>
    );
}

export default App;