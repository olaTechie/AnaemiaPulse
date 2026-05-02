import { motion } from 'framer-motion';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';

export function MetricCard({ label, value, detail, tone = 'neutral' }) {
  return (
    <motion.article className={`metric-card ${tone}`} whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </motion.article>
  );
}

export function SectionCard({ title, subtitle, children, action }) {
  return (
    <motion.section
      className="section-card"
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.4 }}
    >
      <div className="section-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </motion.section>
  );
}

export function Delta({ value }) {
  const positive = value >= 0;
  return (
    <span className={`delta ${positive ? 'positive' : 'negative'}`}>
      {positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
      {Math.abs(value)}%
    </span>
  );
}
