import React from 'react';
import { useROIHistory } from '../hooks/useROIHistory';

export default function ROITable() {
  const { records, total, loading } = useROIHistory();

  return (
    <div className="roi-panel">
      <h2>Detection history <span className="total-badge">{total} total</span></h2>
      {loading && records.length === 0 && <p className="muted">Loading…</p>}

      <div className="table-scroll">
        <table className="roi-table">
          <thead>
            <tr><th>Frame</th><th>x</th><th>y</th><th>w</th><th>h</th><th>Conf.</th><th>Time</th></tr>
          </thead>
          <tbody>
            {records.map(r => (
              <tr key={r.id}>
                <td>{r.frame_id}</td>
                <td>{r.x}</td><td>{r.y}</td>
                <td>{r.width}</td><td>{r.height}</td>
                <td>
                  <span className="conf-pill"
                    style={{ background: `hsl(${Math.round(r.confidence*120)},70%,38%)` }}>
                    {(r.confidence*100).toFixed(0)}%
                  </span>
                </td>
                <td className="muted">{new Date(r.detected_at).toLocaleTimeString()}</td>
              </tr>
            ))}
            {records.length === 0 && !loading && (
              <tr><td colSpan={7} className="muted" style={{textAlign:'center'}}>
                No detections yet — start the camera
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
