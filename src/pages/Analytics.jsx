import Page from '../components/Page.jsx';
import { MetricCard, SectionCard } from '../components/Cards.jsx';
import { BubbleChart, HorizontalBars, TrendChart, WordCloud } from '../components/Charts.jsx';
import { useResearchData } from '../hooks/useResearchData.jsx';
import {
  collaborationPairs,
  fundingSources,
  keywordCloud,
  metrics,
  researchAreaData,
  topCited,
  topList,
  yearlyTrends,
} from '../utils/data.js';

export default function Analytics() {
  const { filteredRecords } = useResearchData();
  const kpis = metrics(filteredRecords);
  const authorRows = topList(filteredRecords, (item) => item.authors, 20).map((author) => {
    const papers = filteredRecords.filter((item) => item.authors.includes(author.name));
    return {
      name: author.name,
      publications: papers.length,
      citations: papers.reduce((total, item) => total + item.citations, 0),
    };
  });

  return (
    <Page
      eyebrow="Analytics"
      title="Deep analysis across authors, disciplines, funding, and impact."
      description="This route consolidates the original Research Disciplines, Funding Analysis, Authors Discovery, and Overview impact tabs into a faster product experience."
    >
      <div className="metric-grid compact">
        <MetricCard label="Single-author papers" value={filteredRecords.filter((item) => item.authors.length === 1).length} />
        <MetricCard label="Multi-author papers" value={filteredRecords.filter((item) => item.authors.length > 1).length} />
        <MetricCard label="Avg citations" value={(kpis.citations / Math.max(kpis.articles, 1)).toFixed(1)} />
        <MetricCard label="Funded records" value={filteredRecords.filter((item) => item.funding_details).length} />
      </div>
      <div className="content-grid two">
        <SectionCard title="Author Impact Bubble" subtitle="Top author publication count plotted against cumulative citations.">
          <BubbleChart data={authorRows} />
        </SectionCard>
        <SectionCard title="Topic and Keyword Signal" subtitle="Fast client-side keyword extraction from titles, abstracts, and keywords.">
          <WordCloud words={keywordCloud(filteredRecords, 55)} />
        </SectionCard>
      </div>
      <div className="content-grid two">
        <SectionCard title="Discipline Trend Backbone">
          <TrendChart data={yearlyTrends(filteredRecords)} />
        </SectionCard>
        <SectionCard title="Funding Contributors">
          <HorizontalBars data={fundingSources(filteredRecords, 14)} height={360} />
        </SectionCard>
      </div>
      <div className="content-grid two">
        <SectionCard title="Research Discipline Mix">
          <HorizontalBars data={researchAreaData(filteredRecords, 16)} height={410} />
        </SectionCard>
        <SectionCard title="Top Collaboration Pairs">
          <HorizontalBars data={collaborationPairs(filteredRecords, (item) => item.authors, 14)} height={410} />
        </SectionCard>
      </div>
      <SectionCard title="Most Cited Publications">
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Title</th><th>Year</th><th>Journal</th><th>Citations</th></tr>
            </thead>
            <tbody>
              {topCited(filteredRecords, 10).map((item) => (
                <tr key={item.id}>
                  <td>{item.title}</td>
                  <td>{item.year}</td>
                  <td>{item.journal}</td>
                  <td>{item.citations}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </Page>
  );
}
