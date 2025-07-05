import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import InventoryPage from './pages/InventoryPage'
import CoachDetailPage from './pages/CoachDetailPage'
import AboutPage from './pages/AboutPage'
import ContactPage from './pages/ContactPage'
import SearchTest from './components/SearchTest'
import ImageDiagnostic from './components/ImageDiagnostic'
import CoachDebugTest from './components/CoachDebugTest'

function App() {
  // Debug: Log API URL on app load
  console.log('App loaded with VITE_API_URL:', import.meta.env.VITE_API_URL);
  console.log('All env vars:', import.meta.env);
  
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="inventory/:coachId" element={<CoachDetailPage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="contact" element={<ContactPage />} />
        <Route path="test" element={<SearchTest />} />
        <Route path="image-test" element={<ImageDiagnostic />} />
        <Route path="debug-coach" element={<CoachDebugTest />} />
      </Route>
    </Routes>
  )
}

export default App
