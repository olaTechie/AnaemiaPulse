import { motion } from 'framer-motion';

export default function Page({ eyebrow, title, description, actions, children }) {
  return (
    <motion.div
      className="page"
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      <section className="page-hero">
        <div>
          {eyebrow && <p className="eyebrow">{eyebrow}</p>}
          <h1>{title}</h1>
          {description && <p>{description}</p>}
        </div>
        {actions && <div className="hero-actions">{actions}</div>}
      </section>
      {children}
    </motion.div>
  );
}
