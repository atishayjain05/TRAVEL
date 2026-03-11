import { useState } from 'react';
import Navbar from './components/Navbar.jsx';
import Sidebar from './components/Sidebar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import ScanCity from './pages/ScanCity.jsx';
import Restaurants from './pages/Restaurants.jsx';
import Export from './pages/Export.jsx';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigate = (page) => setCurrentPage(page);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard navigate={navigate} />;
      case 'scan': return <ScanCity navigate={navigate} />;
      case 'restaurants': return <Restaurants />;
      case 'export': return <Export />;
      default: return <Dashboard navigate={navigate} />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-deep)' }}>
      <Sidebar
        currentPage={currentPage}
        navigate={navigate}
        open={sidebarOpen}
        setOpen={setSidebarOpen}
      />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Navbar
          currentPage={currentPage}
          navigate={navigate}
          toggleSidebar={() => setSidebarOpen((o) => !o)}
        />
        <main className="flex-1 overflow-y-auto p-6">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
