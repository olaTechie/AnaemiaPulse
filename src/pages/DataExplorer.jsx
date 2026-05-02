import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import Page from '../components/Page.jsx';
import { SectionCard } from '../components/Cards.jsx';
import { useResearchData } from '../hooks/useResearchData.jsx';

export default function DataExplorer() {
  const { filteredRecords } = useResearchData();
  const [query, setQuery] = useState('');
  const [sort, setSort] = useState('citations');
  const [expanded, setExpanded] = useState(null);
  const rows = useMemo(() => {
    const q = query.toLowerCase();
    return filteredRecords
      .filter((item) => !q || item.searchable.includes(q))
      .sort((a, b) => (sort === 'year' ? (b.year || 0) - (a.year || 0) : b.citations - a.citations))
      .slice(0, 80);
  }, [filteredRecords, query, sort]);

  return (
    <Page eyebrow="Data Explorer" title="Searchable publication workspace." description="Replaces Streamlit expanders, reference filters, and publication lists with a responsive table and inline detail view.">
      <SectionCard title="Explore References" subtitle={`${rows.length} visible rows from ${filteredRecords.length.toLocaleString()} filtered records`}>
        <div className="toolbar">
          <label className="search-box">
            <Search size={17} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search within filtered results" />
          </label>
          <select value={sort} onChange={(event) => setSort(event.target.value)}>
            <option value="citations">Sort by citations</option>
            <option value="year">Sort by year</option>
          </select>
        </div>
        <div className="publication-list">
          {rows.map((item) => (
            <article key={item.id} className="publication-row">
              <button onClick={() => setExpanded(expanded === item.id ? null : item.id)}>
                <span>{item.year || 'n/a'}</span>
                <strong>{item.title}</strong>
                <em>{item.journal}</em>
                <b>{item.citations} citations</b>
              </button>
              {expanded === item.id && (
                <div className="publication-detail">
                  <p><strong>Authors:</strong> {item.authors.join(', ') || 'Not listed'}</p>
                  <p><strong>Country:</strong> {item.country}</p>
                  <p><strong>Research areas:</strong> {item.researchAreas.join(', ') || 'Not listed'}</p>
                  {item.abstract && <p>{item.abstract}</p>}
                  {item.doi && <a href={`https://doi.org/${item.doi}`} target="_blank" rel="noreferrer">Open DOI</a>}
                </div>
              )}
            </article>
          ))}
        </div>
      </SectionCard>
    </Page>
  );
}
