-- Minimal schema stub
CREATE TABLE IF NOT EXISTS analyses (
  id INTEGER PRIMARY KEY,
  code TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
