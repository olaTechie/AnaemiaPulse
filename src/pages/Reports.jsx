import { useMemo, useState } from 'react';
import Page from '../components/Page.jsx';
import { SectionCard } from '../components/Cards.jsx';
import { useResearchData } from '../hooks/useResearchData.jsx';
import { countryStats, fundingSources, researchAreaData, topCited, yearlyTrends } from '../utils/data.js';

export default function Reports() {
  const { filteredRecords } = useResearchData();
  const [section, setSection] = useState('impact');
  const report = useMemo(() => {
    const trends = yearlyTrends(filteredRecords);
    const first = trends[0]?.year || 'n/a';
    const last = trends.at(-1)?.year || 'n/a';
    return {
      years: `${first}-${last}`,
      topArea: researchAreaData(filteredRecords, 1)[0]?.name || 'n/a',
      topCountry: countryStats(filteredRecords)[0]?.name || 'n/a',
      topFunders: fundingSources(filteredRecords, 5),
      cited: topCited(filteredRecords, 5),
    };
  }, [filteredRecords]);

  return (
    <Page eyebrow="Reports" title="Executive summaries ready for review meetings." description="Narrative reporting keeps the original references and impact workflows, with concise evidence tables for export-ready interpretation.">
      <div className="segmented">
        {['impact', 'funding', 'geography'].map((item) => (
          <button key={item} className={section === item ? 'active' : ''} onClick={() => setSection(item)}>
            {item}
          </button>
        ))}
      </div>
      <SectionCard title={`${section[0].toUpperCase()}${section.slice(1)} Report`} subtitle={`Dataset window: ${report.years}`}>
        {section === 'impact' && (
          <div className="report-copy">
            <p>
              The filtered corpus contains <strong>{filteredRecords.length.toLocaleString()}</strong> publications, with the strongest disciplinary concentration in <strong>{report.topArea}</strong>. Citation attention is led by the publications below.
            </p>
            <ol>
              {report.cited.map((item) => (
                <li key={item.id}>{item.title} ({item.year}) - {item.citations.toLocaleString()} citations</li>
              ))}
            </ol>
          </div>
        )}
        {section === 'funding' && (
          <div className="report-copy">
            <p>Funding signals are extracted and normalized from the original funding details field. The most frequent funders in the current filter are:</p>
            <ol>{report.topFunders.map((item) => <li key={item.name}>{item.name} - {item.value} mentions</li>)}</ol>
          </div>
        )}
        {section === 'geography' && (
          <div className="report-copy">
            <p>
              Country extraction follows the Streamlit address parsing approach. The current leading geography is <strong>{report.topCountry}</strong>, with collaboration concentrated around the highest-output institutions and countries visible in Networks.
            </p>
          </div>
        )}
      </SectionCard>
    </Page>
  );
}
