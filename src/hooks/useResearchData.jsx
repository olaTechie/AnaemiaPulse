import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { enrichRecords, getFilterOptions, getYearExtent, runSearch } from '../utils/data.js';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [rawRecords, setRawRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const records = useMemo(() => enrichRecords(rawRecords), [rawRecords]);
  const yearExtent = useMemo(() => (records.length ? getYearExtent(records) : [1990, 2026]), [records]);
  const filterOptions = useMemo(() => (records.length ? getFilterOptions(records) : { years: yearExtent, countries: [], journals: [], institutions: [] }), [records, yearExtent]);
  const [filters, setFilters] = useState({
    query: '',
    yearRange: yearExtent,
    citationRange: [0, 1000],
    countries: [],
    journals: [],
    institutions: [],
  });

  useEffect(() => {
    let mounted = true;
    fetch(`${import.meta.env.BASE_URL}data/publications.json`)
      .then((response) => {
        if (!response.ok) throw new Error(`Could not load dataset: ${response.status}`);
        return response.json();
      })
      .then((data) => {
        if (!mounted) return;
        const nextRecords = enrichRecords(data);
        const nextYearExtent = getYearExtent(nextRecords);
        setRawRecords(data);
        setFilters({
          query: '',
          yearRange: nextYearExtent,
          citationRange: [0, Math.max(...nextRecords.map((item) => item.citations), 0)],
          countries: [],
          journals: [],
          institutions: [],
        });
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const filteredRecords = useMemo(() => runSearch(records, filters), [records, filters]);

  const updateFilter = (key, value) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({
      query: '',
      yearRange: yearExtent,
      citationRange: [0, Math.max(...records.map((item) => item.citations), 0)],
      countries: [],
      journals: [],
      institutions: [],
    });
  };

  return (
    <DataContext.Provider
      value={{ records, filteredRecords, filters, updateFilter, resetFilters, filterOptions, yearExtent, loading }}
    >
      {loading ? <LoadingShell /> : children}
    </DataContext.Provider>
  );
}

export function useResearchData() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useResearchData must be used inside DataProvider');
  }
  return context;
}

function LoadingShell() {
  return (
    <div className="loading-shell">
      <div className="loading-card">
        <span />
        <h1>AnaemiaPulse</h1>
        <p>Loading publication intelligence...</p>
        <div className="skeleton-grid">
          <i />
          <i />
          <i />
        </div>
      </div>
    </div>
  );
}
