import { useState, useEffect, useCallback } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function useROIHistory() {
  const [records, setRecords] = useState([]);
  const [total,   setTotal]   = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API}/roi?limit=20`);
      if (!resp.ok) throw new Error('fetch failed');
      const data = await resp.json();
      setRecords(data.items);
      setTotal(data.total);
    } catch (_) {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchRecords();
    const id = setInterval(fetchRecords, 3000);
    return () => clearInterval(id);
  }, [fetchRecords]);

  return { records, total, loading };
}
