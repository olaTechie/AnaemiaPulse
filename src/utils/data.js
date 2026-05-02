const STOPWORDS = new Set([
  'the', 'and', 'for', 'with', 'from', 'this', 'that', 'were', 'was', 'are', 'among',
  'study', 'studies', 'pregnancy', 'pregnant', 'women', 'anaemia', 'anemia', 'iron',
  'deficiency', 'maternal', 'using', 'between', 'during', 'after', 'before', 'into',
  'their', 'have', 'has', 'had', 'risk', 'results', 'analysis', 'associated',
]);

export function enrichRecords(records) {
  return records.map((record, index) => {
    const authors = splitList(record.author || record.authors, ' and ');
    const affiliations = splitList(record.affiliation, ';');
    const researchAreas = splitFlexible(record.research_areas);
    const keywords = splitFlexible(record.keywords || record.author_keywords);
    return {
      ...record,
      id: record.unique_id || `publication-${index}`,
      year: Number(record.year) || null,
      citations: Number(record.citations ?? record.usage_count_since_2013) || 0,
      title: record.title || 'Untitled publication',
      journal: record.journal || 'Unknown journal',
      authors,
      affiliations,
      researchAreas,
      keywords,
      country: extractCountry(record.address),
      searchable: [record.title, record.abstract, record.journal, record.author, record.keywords]
        .filter(Boolean)
        .join(' ')
        .toLowerCase(),
    };
  });
}

export function splitList(value, delimiter) {
  if (!value || typeof value !== 'string') return [];
  return value.split(delimiter).map((item) => item.trim()).filter(Boolean);
}

export function splitFlexible(value) {
  if (!value || typeof value !== 'string') return [];
  return value.split(/[;,]/).map((item) => item.trim()).filter(Boolean);
}

export function extractCountry(address) {
  if (!address || typeof address !== 'string') return 'Unknown';
  const aliases = {
    USA: 'United States',
    US: 'United States',
    ENGLAND: 'United Kingdom',
    UK: 'United Kingdom',
    BRITAIN: 'United Kingdom',
    UAE: 'United Arab Emirates',
  };
  const parts = address.toUpperCase().split(',').map((part) => part.trim()).filter(Boolean);
  const candidate = parts.at(-1) || 'Unknown';
  if (candidate.endsWith(' USA') || candidate === 'USA') return 'United States';
  return aliases[candidate] || toTitleCase(candidate);
}

export function toTitleCase(value) {
  return String(value).toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
}

export function getYearExtent(records) {
  const years = records.map((item) => item.year).filter(Boolean);
  return [Math.min(...years), Math.max(...years)];
}

export function getFilterOptions(records) {
  return {
    years: getYearExtent(records),
    countries: topValues(records.map((item) => item.country), 30),
    journals: topValues(records.map((item) => item.journal), 30),
    institutions: topValues(records.flatMap((item) => item.affiliations), 30),
  };
}

export function runSearch(records, filters) {
  const query = filters.query.trim().toLowerCase();
  return records.filter((item) => {
    const yearMatch = item.year >= filters.yearRange[0] && item.year <= filters.yearRange[1];
    const citationMatch = item.citations >= filters.citationRange[0] && item.citations <= filters.citationRange[1];
    const queryMatch = !query || item.searchable.includes(query);
    const countryMatch = filters.countries.length === 0 || filters.countries.includes(item.country);
    const journalMatch = filters.journals.length === 0 || filters.journals.includes(item.journal);
    const institutionMatch =
      filters.institutions.length === 0 || item.affiliations.some((affiliation) => filters.institutions.includes(affiliation));
    return yearMatch && citationMatch && queryMatch && countryMatch && journalMatch && institutionMatch;
  });
}

export function metrics(records) {
  return {
    articles: records.length,
    authors: new Set(records.flatMap((item) => item.authors)).size,
    institutions: new Set(records.flatMap((item) => item.affiliations)).size,
    countries: new Set(records.map((item) => item.country)).size,
    citations: sum(records, (item) => item.citations),
  };
}

export function yearlyTrends(records) {
  const grouped = groupBy(records.filter((item) => item.year), (item) => item.year);
  return Object.entries(grouped)
    .map(([year, items]) => ({
      year: Number(year),
      publications: items.length,
      citations: sum(items, (item) => item.citations),
      avgCitations: round(sum(items, (item) => item.citations) / items.length),
    }))
    .sort((a, b) => a.year - b.year);
}

export function topValues(values, limit = 10) {
  const counts = new Map();
  values.filter(Boolean).forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([name, value]) => ({ name, value }));
}

export function topList(records, selector, limit = 10) {
  return topValues(records.flatMap(selector), limit);
}

export function researchAreaData(records, limit = 15) {
  return topList(records, (item) => item.researchAreas, limit);
}

export function fundingSources(records, limit = 20) {
  const normalized = records.flatMap((item) => splitFlexible(item.funding_details)).map(cleanFundingSource).filter(Boolean);
  return topValues(normalized, limit);
}

export function cleanFundingSource(source) {
  const cleaned = source.replace(/Funding Source:\s*/i, '').replace(/\[.*?\]/g, '').replace(/[.,;:]+$/g, '').trim();
  const lower = cleaned.toLowerCase();
  if (lower.includes('gates') || lower.includes('melinda')) return 'Bill & Melinda Gates Foundation';
  if (lower.includes('wellcome')) return 'Wellcome Trust';
  if (lower.includes('vifor')) return 'Vifor Pharma';
  if (lower.includes('nihr')) return 'National Institute for Health and Care Research';
  return cleaned;
}

export function keywordCloud(records, limit = 45) {
  const text = records
    .map((item) => `${item.title} ${item.abstract || ''} ${item.keywords.join(' ')}`)
    .join(' ')
    .toLowerCase()
    .replace(/[^a-z\s-]/g, ' ');
  return topValues(
    text.split(/\s+/).filter((word) => word.length > 4 && !STOPWORDS.has(word)),
    limit,
  );
}

export function topCited(records, limit = 10) {
  return [...records].sort((a, b) => b.citations - a.citations).slice(0, limit);
}

export function collaborationPairs(records, selector, limit = 12) {
  const counts = new Map();
  records.forEach((item) => {
    const values = [...new Set(selector(item).filter(Boolean))].slice(0, 12);
    for (let i = 0; i < values.length; i += 1) {
      for (let j = i + 1; j < values.length; j += 1) {
        const pair = [values[i], values[j]].sort().join(' | ');
        counts.set(pair, (counts.get(pair) || 0) + 1);
      }
    }
  });
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([pair, value]) => ({ name: pair.replace(' | ', ' & '), value }));
}

export function countryStats(records) {
  return topValues(records.map((item) => item.country), 20).map((country) => {
    const items = records.filter((item) => item.country === country.name);
    return {
      ...country,
      citations: sum(items, (item) => item.citations),
      authors: new Set(items.flatMap((item) => item.authors)).size,
      avgCitations: round(sum(items, (item) => item.citations) / items.length),
    };
  });
}

export function groupBy(values, selector) {
  return values.reduce((acc, item) => {
    const key = selector(item);
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});
}

export function sum(values, selector) {
  return values.reduce((total, item) => total + selector(item), 0);
}

export function round(value, digits = 1) {
  return Number.isFinite(value) ? Number(value.toFixed(digits)) : 0;
}

export function toCsv(records) {
  const columns = ['title', 'year', 'journal', 'country', 'citations', 'doi'];
  const escape = (value) => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return [columns.join(','), ...records.map((row) => columns.map((column) => escape(row[column])).join(','))].join('\n');
}
