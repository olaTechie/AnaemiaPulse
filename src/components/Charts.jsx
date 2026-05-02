import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts';

const palette = ['#1f6f78', '#d36b4a', '#7c5c3f', '#5d8f68', '#c59a32', '#3f5175', '#b45d7a'];

export function TrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <ComposedChart data={data}>
        <CartesianGrid stroke="#eadfce" strokeDasharray="4 6" />
        <XAxis dataKey="year" tickLine={false} axisLine={false} />
        <YAxis yAxisId="left" tickLine={false} axisLine={false} />
        <YAxis yAxisId="right" orientation="right" tickLine={false} axisLine={false} />
        <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e8dcc8' }} />
        <Legend />
        <Area yAxisId="left" type="monotone" dataKey="publications" fill="#1f6f7822" stroke="#1f6f78" strokeWidth={3} />
        <Line yAxisId="right" type="monotone" dataKey="citations" stroke="#d36b4a" strokeWidth={3} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function HorizontalBars({ data, dataKey = 'value', labelKey = 'name', height = 360 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={[...data].reverse()} layout="vertical" margin={{ left: 24, right: 24 }}>
        <CartesianGrid stroke="#eadfce" strokeDasharray="4 6" horizontal={false} />
        <XAxis type="number" axisLine={false} tickLine={false} />
        <YAxis dataKey={labelKey} type="category" width={150} axisLine={false} tickLine={false} tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e8dcc8' }} />
        <Bar dataKey={dataKey} radius={[0, 8, 8, 0]}>
          {data.map((_, index) => (
            <Cell key={index} fill={palette[index % palette.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MiniArea({ data }) {
  return (
    <ResponsiveContainer width="100%" height={110}>
      <AreaChart data={data}>
        <Area type="monotone" dataKey="publications" fill="#1f6f7824" stroke="#1f6f78" strokeWidth={3} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function BubbleChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={360}>
      <ScatterChart margin={{ left: 8, right: 24, top: 20, bottom: 20 }}>
        <CartesianGrid stroke="#eadfce" strokeDasharray="4 6" />
        <XAxis dataKey="publications" name="Publications" axisLine={false} tickLine={false} />
        <YAxis dataKey="citations" name="Citations" axisLine={false} tickLine={false} />
        <ZAxis dataKey="citations" range={[80, 900]} />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: 12, border: '1px solid #e8dcc8' }} />
        <Scatter data={data} fill="#d36b4a" />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

export function WordCloud({ words }) {
  const max = Math.max(...words.map((item) => item.value), 1);
  return (
    <div className="word-cloud">
      {words.map((word, index) => (
        <span
          key={`${word.name}-${index}`}
          style={{
            fontSize: `${0.85 + (word.value / max) * 2.2}rem`,
            color: palette[index % palette.length],
          }}
        >
          {word.name}
        </span>
      ))}
    </div>
  );
}
