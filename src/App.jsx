import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import AppLayout from './layouts/AppLayout.jsx';
import Overview from './pages/Overview.jsx';
import Analytics from './pages/Analytics.jsx';
import Reports from './pages/Reports.jsx';
import DataExplorer from './pages/DataExplorer.jsx';
import Insights from './pages/Insights.jsx';
import Networks from './pages/Networks.jsx';
import About from './pages/About.jsx';
import { DataProvider } from './hooks/useResearchData.jsx';

export default function App() {
  const location = useLocation();

  return (
    <DataProvider>
      <AppLayout>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Overview />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/explorer" element={<DataExplorer />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/networks" element={<Networks />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AnimatePresence>
      </AppLayout>
    </DataProvider>
  );
}
