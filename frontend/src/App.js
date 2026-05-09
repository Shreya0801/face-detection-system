import React from 'react';
import VideoPanel from './components/VideoPanel';
import ROITable   from './components/ROITable';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Face Detection — Live Stream</h1>
        <span className="badge">MediaPipe · Pillow · FastAPI · PostgreSQL</span>
      </header>
      <main className="app-main">
        <VideoPanel />
        <ROITable />
      </main>
    </div>
  );
}
