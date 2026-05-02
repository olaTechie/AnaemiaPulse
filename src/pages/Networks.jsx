import Page from '../components/Page.jsx';
import { SectionCard } from '../components/Cards.jsx';
import { HorizontalBars } from '../components/Charts.jsx';
import { useResearchData } from '../hooks/useResearchData.jsx';
import { collaborationPairs, countryStats, topList } from '../utils/data.js';

export default function Networks() {
  const { filteredRecords } = useResearchData();
  const authorPairs = collaborationPairs(filteredRecords, (item) => item.authors, 14);
  const institutionPairs = collaborationPairs(filteredRecords, (item) => item.affiliations, 14);
  const countryPairs = collaborationPairs(filteredRecords, (item) => [item.country, ...item.affiliations.slice(0, 2)], 12);

  return (
    <Page eyebrow="Networks" title="Citation and collaboration networks, simplified for the web." description="The original VOS/network pages are represented as performant collaboration pair rankings and a lightweight visual graph for launch readiness on GitHub Pages.">
      <SectionCard title="Author Collaboration Network">
        <NetworkMap pairs={authorPairs} />
      </SectionCard>
      <div className="content-grid two">
        <SectionCard title="Author Co-authorship Pairs">
          <HorizontalBars data={authorPairs} height={380} />
        </SectionCard>
        <SectionCard title="Organization Co-authorship Pairs">
          <HorizontalBars data={institutionPairs} height={380} />
        </SectionCard>
      </div>
      <div className="content-grid two">
        <SectionCard title="Country Citation Presence">
          <HorizontalBars data={countryStats(filteredRecords).slice(0, 12)} height={360} />
        </SectionCard>
        <SectionCard title="Journal Citation Network Proxy">
          <HorizontalBars data={topList(filteredRecords, (item) => [item.journal], 12)} height={360} />
        </SectionCard>
      </div>
      <SectionCard title="Country and Institution Bridges">
        <HorizontalBars data={countryPairs} height={330} />
      </SectionCard>
    </Page>
  );
}

function NetworkMap({ pairs }) {
  const nodes = [...new Set(pairs.flatMap((pair) => pair.name.split(' & ')))].slice(0, 18);
  const center = 180;
  const radius = 140;
  const positions = Object.fromEntries(
    nodes.map((node, index) => [
      node,
      {
        x: center + Math.cos((index / nodes.length) * Math.PI * 2) * radius,
        y: center + Math.sin((index / nodes.length) * Math.PI * 2) * radius,
      },
    ]),
  );

  return (
    <svg className="network-map" viewBox="0 0 360 360" role="img" aria-label="Author collaboration network">
      {pairs.slice(0, 20).map((pair) => {
        const [a, b] = pair.name.split(' & ');
        if (!positions[a] || !positions[b]) return null;
        return <line key={pair.name} x1={positions[a].x} y1={positions[a].y} x2={positions[b].x} y2={positions[b].y} strokeWidth={Math.max(1, pair.value / 2)} />;
      })}
      {nodes.map((node) => (
        <g key={node}>
          <circle cx={positions[node].x} cy={positions[node].y} r="10" />
          <text x={positions[node].x} y={positions[node].y - 15}>{node.split(' ').slice(0, 2).join(' ')}</text>
        </g>
      ))}
    </svg>
  );
}
