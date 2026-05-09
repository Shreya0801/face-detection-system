import { useRef, useState, useCallback, useEffect } from 'react';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/feed';
const FPS = 15;
const SESSION_ID = `session_${Date.now()}`;

export function useWebcamStream() {
  const videoRef    = useRef(null);
  const canvasRef   = useRef(null);
  const wsRef       = useRef(null);
  const intervalRef = useRef(null);
  const fpsRef      = useRef({ count: 0, last: Date.now() });

  const [isStreaming, setIsStreaming] = useState(false);
  const [roiData,     setRoiData]     = useState(null);
  const [error,       setError]       = useState(null);
  const [fps,         setFps]         = useState(0);

  const stopStream = useCallback(() => {
    clearInterval(intervalRef.current);
    if (wsRef.current)            { wsRef.current.close(); wsRef.current = null; }
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    setFps(0);
  }, []);

  const startStream = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      const ws = new WebSocket(`${WS_URL}?session_id=${SESSION_ID}`);
      ws.binaryType = 'arraybuffer';
      wsRef.current = ws;

      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          setRoiData(msg);
          const c = fpsRef.current;
          c.count++;
          const now = Date.now();
          if (now - c.last >= 1000) { setFps(c.count); c.count = 0; c.last = now; }
        } catch (_) {}
      };

      ws.onerror = () => setError('WebSocket error — is the backend running?');
      ws.onclose = () => setIsStreaming(false);

      await new Promise((resolve, reject) => {
        ws.onopen = resolve;
        setTimeout(() => reject(new Error('WebSocket connect timeout')), 5000);
      });

      const canvas = canvasRef.current;
      const ctx    = canvas?.getContext('2d');

      intervalRef.current = setInterval(() => {
        if (!videoRef.current || !canvas || ws.readyState !== WebSocket.OPEN) return;
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(
          (blob) => { if (blob) blob.arrayBuffer().then(buf => ws.send(buf)); },
          'image/jpeg', 0.8,
        );
      }, 1000 / FPS);

      setIsStreaming(true);
    } catch (err) {
      setError(err.message || 'Failed to start stream');
      stopStream();
    }
  }, [stopStream]);

  useEffect(() => () => stopStream(), [stopStream]);

  return { videoRef, canvasRef, isStreaming, roiData, error, fps, startStream, stopStream };
}
