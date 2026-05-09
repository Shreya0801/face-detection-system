import React from 'react';
import { useWebcamStream } from '../hooks/useWebcamStream';

const STREAM = (process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/stream';

export default function VideoPanel() {
  const { videoRef, canvasRef, isStreaming, roiData, error, fps, startStream, stopStream } =
    useWebcamStream();
  const face = roiData?.face;

  return (
    <div className="video-panel">
      {/* Hidden — used only for frame capture */}
      <video  ref={videoRef}  style={{ display: 'none' }} playsInline muted />
      <canvas ref={canvasRef} width={640} height={480}   style={{ display: 'none' }} />

      {/* Annotated stream from backend */}
      <div className="stream-wrapper">
        <img className="stream-img" src={STREAM} alt="Annotated stream" />

        {face && (
          <div className="roi-badge">
            <span className="dot" />
            {`x:${face.x}  y:${face.y}  ${face.width}×${face.height}  ${(face.confidence*100).toFixed(0)}%`}
          </div>
        )}
        {!face && isStreaming && (
          <div className="roi-badge roi-badge--none">No face detected</div>
        )}
      </div>

      <div className="controls">
        {!isStreaming
          ? <button className="btn btn--start" onClick={startStream}>▶ Start camera</button>
          : <button className="btn btn--stop"  onClick={stopStream}>■ Stop</button>
        }
        {isStreaming && <span className="fps-label">{fps} fps</span>}
      </div>

      {error && <p className="error-msg">{error}</p>}
    </div>
  );
}
