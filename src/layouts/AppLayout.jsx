import { NavLink } from 'react-router-dom';
import {
  Activity,
  BarChart3,
  BookOpen,
  Database,
  Info,
  Menu,
  Network,
  Search,
  Sparkles,
  X,
} from 'lucide-react';
import { useState } from 'react';
import logo from '../assets/logo.png';
import FilterPanel from '../components/FilterPanel.jsx';

const nav = [
  { to: '/', label: 'Overview', icon: Activity },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/reports', label: 'Reports', icon: BookOpen },
  { to: '/explorer', label: 'Data Explorer', icon: Database },
  { to: '/insights', label: 'Insights', icon: Sparkles },
  { to: '/networks', label: 'Networks', icon: Network },
  { to: '/about', label: 'About', icon: Info },
];

export default function AppLayout({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? 'is-open' : ''}`}>
        <div className="brand">
          <img src={logo} alt="" />
          <div>
            <strong>AnaemiaPulse</strong>
            <span>Maternal research intelligence</span>
          </div>
        </div>
        <nav className="nav-list" aria-label="Primary">
          {nav.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} onClick={() => setOpen(false)}>
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <FilterPanel />
      </aside>
      <div className="main-frame">
        <header className="topbar">
          <button className="icon-button mobile-only" onClick={() => setOpen((value) => !value)} aria-label="Toggle menu">
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="command-strip">
            <Search size={17} />
            <span>Search, filter, compare, and export maternal anaemia publications</span>
          </div>
        </header>
        <main>{children}</main>
      </div>
    </div>
  );
}
