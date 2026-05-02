import Page from '../components/Page.jsx';
import { SectionCard } from '../components/Cards.jsx';
import hero from '../assets/hero_image.png';
import overview from '../assets/overview_diagram.png';
import topic from '../assets/topic_model.png';
import impact from '../assets/impact_analysis.png';

export default function About() {
  return (
    <Page eyebrow="About" title="From Streamlit prototype to branded research product." description="AnaemiaPulse preserves the maternal anaemia dashboard logic while modernizing the interface, architecture, and deployment path.">
      <section className="visual-hero">
        <img src={hero} alt="Maternal anaemia dashboard visual" />
        <div>
          <h2>Migration Strategy</h2>
          <p>Streamlit pages are mapped into persistent React routes. Session state became a shared data provider, pandas transforms became pure utility functions, and charts moved into responsive Recharts components with subtle Framer Motion transitions.</p>
        </div>
      </section>
      <div className="content-grid three">
        <SectionCard title="Bibliometrics">
          <img className="card-image" src={overview} alt="Overview diagram" />
        </SectionCard>
        <SectionCard title="Topic Modelling">
          <img className="card-image" src={topic} alt="Topic model" />
        </SectionCard>
        <SectionCard title="Impact Analysis">
          <img className="card-image" src={impact} alt="Impact analysis" />
        </SectionCard>
      </div>
      <SectionCard title="Streamlit to React Mapping">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Streamlit Area</th><th>React Destination</th><th>Implementation</th></tr></thead>
            <tbody>
              <tr><td>Overview</td><td>Dashboard / Overview</td><td>KPI cards, trends, contributors, funding cloud</td></tr>
              <tr><td>Research Disciplines</td><td>Analytics and Insights</td><td>Discipline bars, keyword cloud, growth signals</td></tr>
              <tr><td>Funding Analysis</td><td>Analytics, Insights, Reports</td><td>Normalized funder extraction and ranking</td></tr>
              <tr><td>Author Discovery</td><td>Analytics and Data Explorer</td><td>Author metrics, bubbles, searchable papers</td></tr>
              <tr><td>Network Pages</td><td>Networks</td><td>Author, journal, country, and institution network proxies</td></tr>
              <tr><td>References</td><td>Data Explorer</td><td>Search, sorting, inline abstract expansion, DOI links</td></tr>
            </tbody>
          </table>
        </div>
      </SectionCard>
    </Page>
  );
}
