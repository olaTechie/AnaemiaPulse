# AnaemiaPulse

AnaemiaPulse is a production-ready React/Vite migration of the maternal anaemia Streamlit bibliometric dashboard. It turns the original Excel-backed research analysis into a polished, responsive, multi-page research intelligence product deployable to GitHub Pages.

## Migration Strategy

The original Streamlit pages were mapped into a scalable React architecture:

| Streamlit source | React destination | Preserved workflow |
| --- | --- | --- |
| Overview | `Dashboard / Overview` | KPIs, trends, contributors, geography, funding signals |
| Research Disciplines | `Analytics`, `Insights` | Discipline ranking, trends, keyword exploration |
| Funding Analysis | `Analytics`, `Reports`, `Insights` | Funding source cleanup, normalization, rankings |
| Author Discovery | `Analytics`, `Data Explorer`, `Networks` | Author metrics, citation bubbles, publication drill-down |
| Citation and collaboration networks | `Networks` | Author, institution, country, and journal relationship views |
| References | `Data Explorer` | Search, sorting, publication detail expansion, DOI links |
| About Project | `About` | Project framing, methodology, migration notes |

The Excel workbook is converted to `src/data/publications.json` and loaded statically, so the deployed site requires no backend.

## Tech Stack

- React
- Vite
- React Router
- Framer Motion
- Recharts
- Lucide React
- GitHub Actions
- GitHub Pages

## Project Structure

```text
src/
  assets/       Static brand and research visuals
  components/   Cards, charts, page shell primitives, filters
  data/         Static publication dataset
  hooks/        Shared data provider and filter state
  layouts/      Persistent application layout
  pages/        Multi-page React routes
  styles/       Global product styling
  utils/        Data processing and analytics utilities
```

## Development

```bash
npm install
npm run dev
```

## Production Build

```bash
npm run build
npm run preview
```

## One-Command Deployment

After committing changes, run:

```bash
npm run deploy
```

This runs linting, builds the app, and pushes `main` to the `anaemia-pulse` remote. GitHub Actions then publishes the latest build to GitHub Pages.

## GitHub Repository Setup

Recommended repository name: `AnaemiaPulse`

```bash
git init
git add .
git commit -m "feat: migrate Streamlit dashboard to React"
gh repo create AnaemiaPulse --public --source=. --remote=origin --push
```

If the repository already exists:

```bash
git remote add origin https://github.com/<your-username>/AnaemiaPulse.git
git branch -M main
git push -u origin main
```

## GitHub Pages Deployment

The app is configured for the GitHub Pages repo path:

```js
base: '/AnaemiaPulse/'
```

Routing uses `HashRouter`, so direct page refreshes work on GitHub Pages without a custom 404 fallback.

To enable deployment:

1. Push the repository to GitHub as `AnaemiaPulse`.
2. Open GitHub repository settings.
3. Go to **Pages**.
4. Set **Source** to **GitHub Actions**.
5. Push to `main`.

The workflow at `.github/workflows/deploy.yml` installs dependencies, builds the production app, uploads the `dist` artifact, and publishes to GitHub Pages.

Expected URL:

```text
https://<your-username>.github.io/AnaemiaPulse/
```
