import { RotateCcw } from 'lucide-react';
import { useResearchData } from '../hooks/useResearchData.jsx';

export default function FilterPanel() {
  const { filters, updateFilter, resetFilters, filterOptions } = useResearchData();

  return (
    <section className="filter-panel">
      <div className="panel-title">
        <span>Global Filters</span>
        <button className="ghost-button" onClick={resetFilters}>
          <RotateCcw size={15} /> Reset
        </button>
      </div>
      <label>
        <span>Search publications</span>
        <input value={filters.query} onChange={(event) => updateFilter('query', event.target.value)} placeholder="Title, abstract, journal..." />
      </label>
      <RangePair
        label="Publication years"
        value={filters.yearRange}
        min={filterOptions.years?.[0] || 1990}
        max={filterOptions.years?.[1] || new Date().getFullYear()}
        onChange={(value) => updateFilter('yearRange', value)}
      />
      <RangePair
        label="Citations"
        value={filters.citationRange}
        min={0}
        max={Math.max(filters.citationRange[1], 1000)}
        onChange={(value) => updateFilter('citationRange', value)}
      />
      <MultiSelect label="Countries" values={filters.countries} options={filterOptions.countries} onChange={(value) => updateFilter('countries', value)} />
      <MultiSelect label="Journals" values={filters.journals} options={filterOptions.journals} onChange={(value) => updateFilter('journals', value)} />
    </section>
  );
}

function RangePair({ label, value, min, max, onChange }) {
  const setValue = (index, next) => {
    const pair = [...value];
    pair[index] = Number(next);
    if (pair[0] > pair[1]) pair[index === 0 ? 1 : 0] = pair[index];
    onChange(pair);
  };

  return (
    <label>
      <span>{label}</span>
      <div className="range-pair">
        <input type="number" min={min} max={max} value={value[0]} onChange={(event) => setValue(0, event.target.value)} />
        <input type="number" min={min} max={max} value={value[1]} onChange={(event) => setValue(1, event.target.value)} />
      </div>
    </label>
  );
}

function MultiSelect({ label, values, options, onChange }) {
  return (
    <label>
      <span>{label}</span>
      <select
        multiple
        value={values}
        onChange={(event) => onChange([...event.target.selectedOptions].map((option) => option.value))}
      >
        {options.map((option) => (
          <option key={option.name} value={option.name}>
            {option.name} ({option.value})
          </option>
        ))}
      </select>
    </label>
  );
}
