import Page from '../components/Page.jsx';
import { MetricCard, SectionCard } from '../components/Cards.jsx';
import { HorizontalBars, WordCloud } from '../components/Charts.jsx';
import { useResearchData } from '../hooks/useResearchData.jsx';
import { fundingSources, keywordCloud, researchAreaData, yearlyTrends } from '../utils/data.js';

export default function Insights() {
  const { filteredRecords } = useResearchData();
  const trends = yearlyTrends(filteredRecords);
  const recent = trends.slice(-3).reduce((total, item) => total + item.publications, 0);
  const previous = trends.slice(-6, -3).reduce((total, item) => total + item.publications, 0);
  const growth = previous ? Math.round(((recent - previous) / previous) * 100) : 0;

  return (
    <Page eyebrow="Insights" title="Signals surfaced from the research corpus." description="A focused interpretation layer for topic discovery, keyword evolution, growth, and funding patterns.">
      <div className="metric-grid compact">
        <MetricCard label="Recent publications" value={recent} detail="Last three years in current view" />
        <MetricCard label="Growth vs prior period" value={`${growth}%`} detail="Three-year comparison" tone={growth >= 0 ? 'green' : 'coral'} />
        <MetricCard label="Dominant discipline" value={researchAreaData(filteredRecords, 1)[0]?.name || 'n/a'} />
      </div>
      <div className="content-grid two">
        <SectionCard title="Topic Discovery Cloud" subtitle="Client-side equivalent of title and abstract keyword exploration.">
          <WordCloud words={keywordCloud(filteredRecords, 70)} />
        </SectionCard>
        <SectionCard title="Fastest Visible Disciplines" subtitle="Top research area frequencies in the current filter.">
          <HorizontalBars data={researchAreaData(filteredRecords, 12)} height={360} />
        </SectionCard>
      </div>
      <SectionCard title="Funding Intelligence">
        <HorizontalBars data={fundingSources(filteredRecords, 18)} height={430} />
      </SectionCard>
    </Page>
  );
}
