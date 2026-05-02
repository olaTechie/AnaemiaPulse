import { Download, SlidersHorizontal } from 'lucide-react';
import Page from '../components/Page.jsx';
import { MetricCard, SectionCard } from '../components/Cards.jsx';
import { HorizontalBars, MiniArea, TrendChart, WordCloud } from '../components/Charts.jsx';
import { useResearchData } from '../hooks/useResearchData.jsx';
import {
  countryStats,
  fundingSources,
  keywordCloud,
  metrics,
  researchAreaData,
  toCsv,
  topList,
  yearlyTrends,
} from '../utils/data.js';

export default function Overview() {
  const { filteredRecords, filters } = useResearchData();
  const kpis = metrics(filteredRecords);
  const trends = yearlyTrends(filteredRecords);
  const recent = trends.slice(-10);

  const exportCsv = () => {
    const blob = new Blob([toCsv(filteredRecords)], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'anaemia-pulse-filtered-publications.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Page
      eyebrow="Maternal anaemia bibliometrics"
      title="A polished research command center for maternal anaemia evidence."
      description="Explore publication momentum, citation impact, disciplinary focus, funding signals, geography, and collaboration patterns from the imported Web of Science dataset."
      actions={
        <button className="primary-button" onClick={exportCsv}>
          <Download size={17} /> Export CSV
        </button>
      }
    >
      <div className="metric-grid">
        <MetricCard label="Total articles" value={kpis.articles.toLocaleString()} detail="Filtered publications" />
        <MetricCard label="Authors" value={kpis.authors.toLocaleString()} detail="Unique author names" tone="blue" />
        <MetricCard label="Institutions" value={kpis.institutions.toLocaleString()} detail="Affiliation entries" tone="green" />
        <MetricCard label="Countries" value={kpis.countries.toLocaleString()} detail="Extracted from addresses" tone="gold" />
        <MetricCard label="Citations" value={kpis.citations.toLocaleString()} detail="Usage count since 2013" tone="coral" />
      </div>

      <section className="summary-band">
        <div>
          <SlidersHorizontal size={18} />
          <strong>Current view</strong>
          <span>
            {filters.yearRange[0]}-{filters.yearRange[1]}, {filteredRecords.length.toLocaleString()} papers,
            {filters.countries.length ? ` ${filters.countries.length} selected countries` : ' all countries'}
          </span>
        </div>
        <MiniArea data={recent} />
      </section>

      <div className="content-grid two">
        <SectionCard title="Publication and Citation Trends" subtitle="Streamlit line and citation charts rebuilt with responsive Recharts.">
          <TrendChart data={trends} />
        </SectionCard>
        <SectionCard title="Research Disciplines" subtitle="Normalized top disciplines from research area metadata.">
          <HorizontalBars data={researchAreaData(filteredRecords, 12)} height={320} />
        </SectionCard>
      </div>

      <div className="content-grid three">
        <SectionCard title="Top Authors">
          <HorizontalBars data={topList(filteredRecords, (item) => item.authors, 8)} height={300} />
        </SectionCard>
        <SectionCard title="Countries">
          <HorizontalBars data={countryStats(filteredRecords).slice(0, 8)} height={300} />
        </SectionCard>
        <SectionCard title="Funding Cloud">
          <WordCloud words={[...fundingSources(filteredRecords, 18), ...keywordCloud(filteredRecords, 12)].slice(0, 28)} />
        </SectionCard>
      </div>
    </Page>
  );
}
