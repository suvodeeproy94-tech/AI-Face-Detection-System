/*
  This component handles the live webcam.
  It captures frames, sends them to Flask, and draws face boxes on the canvas.
*/

import { Camera, Play, RefreshCw, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function WebcamFeed({ onDetectionResult, onStatsRefresh }) {
  const videoRef = useRef(null);
  const captureCanvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const isSendingFrameRef = useRef(false);

  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!isCameraActive || !isDetecting) {
      return undefined;
    }

    const detectionInterval = window.setInterval(() => {
      captureAndDetectFrame();
    }, 700);

    return () => {
      window.clearInterval(detectionInterval);
    };
  }, [isCameraActive, isDetecting]);

  async function startCamera() {
    setErrorMessage("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user",
        },
        audio: false,
      });

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      setIsCameraActive(true);
      setIsDetecting(true);
    } catch (error) {
      setErrorMessage(
        "Camera access failed. Please allow webcam permission in the browser.",
      );
    }
  }

  function stopCamera() {
    const videoElement = videoRef.current;
    const stream = videoElement?.srcObject;

    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }

    if (videoElement) {
      videoElement.srcObject = null;
    }

    clearOverlayCanvas();
    setIsCameraActive(false);
    setIsDetecting(false);
    onDetectionResult(null);
  }

  async function captureAndDetectFrame() {
    if (isSendingFrameRef.current || !videoRef.current) {
      return;
    }

    const videoElement = videoRef.current;

    if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
      return;
    }

    isSendingFrameRef.current = true;

    try {
      const frame = captureCurrentFrame(videoElement);
      const detectionResult = await sendFrameToBackend(frame);

      drawDetectionBoxes(detectionResult);
      onDetectionResult(detectionResult);
      onStatsRefresh();
      setErrorMessage("");
    } catch (error) {
      setErrorMessage(error.message || "Detection request failed.");
    } finally {
      isSendingFrameRef.current = false;
    }
  }

  function captureCurrentFrame(videoElement) {
    const canvas = captureCanvasRef.current;
    const context = canvas.getContext("2d");

    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.78);
  }

  async function sendFrameToBackend(frame) {
    let response;

    try {
      response = await fetch(`${API_BASE_URL}/api/detection/frame`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ frame }),
      });
    } catch (error) {
      throw new Error(
        "Detection request failed. Please restart Flask backend and refresh the page.",
      );
    }

    const responseData = await response.json();

    if (!response.ok || !responseData.success) {
      throw new Error(responseData.message || "Detection failed.");
    }

    return responseData.data;
  }

  function drawDetectionBoxes(detectionResult) {
    const canvas = overlayCanvasRef.current;
    const context = canvas.getContext("2d");

    canvas.width = detectionResult.frame_width;
    canvas.height = detectionResult.frame_height;
    context.clearRect(0, 0, canvas.width, canvas.height);

    detectionResult.faces.forEach((face) => {
      drawSingleFaceBox(context, face);
    });
  }

  function drawSingleFaceBox(context, face) {
    const label = `ID ${face.tracking_id} | ${face.confidence}%`;

    context.lineWidth = 4;
    context.strokeStyle = "#10b981";
    context.strokeRect(face.x, face.y, face.width, face.height);

    context.fillStyle = "#0f172a";
    context.fillRect(face.x, Math.max(face.y - 32, 0), 120, 28);

    context.fillStyle = "#ffffff";
    context.font = "16px Arial";
    context.fillText(label, face.x + 8, Math.max(face.y - 11, 20));
  }

  function clearOverlayCanvas() {
    const canvas = overlayCanvasRef.current;

    if (!canvas) {
      return;
    }

    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
  }

  return (
    <section className="rounded-md border border-slate-200 bg-white p-5">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-950">
            Live Webcam Detection
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Start the camera and the backend will detect faces in real time.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {!isCameraActive ? (
            <button className="btn btn-primary" type="button" onClick={startCamera}>
              <Play size={18} />
              Start Camera
            </button>
          ) : (
            <button className="btn btn-danger" type="button" onClick={stopCamera}>
              <Square size={18} />
              Stop Camera
            </button>
          )}

          <button
            className="btn btn-secondary"
            type="button"
            disabled={!isCameraActive}
            onClick={() => setIsDetecting((currentValue) => !currentValue)}
          >
            {isDetecting ? <Square size={18} /> : <RefreshCw size={18} />}
            {isDetecting ? "Pause" : "Resume"}
          </button>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-md bg-slate-950">
        {!isCameraActive && (
          <div className="absolute inset-0 z-10 flex min-h-[320px] flex-col items-center justify-center gap-3 text-slate-300">
            <Camera size={48} />
            <p className="text-center text-sm font-medium">
              Webcam preview will appear here.
            </p>
          </div>
        )}

        <video
          ref={videoRef}
          className="block min-h-[320px] w-full bg-slate-950 object-fill"
          muted
          playsInline
        />

        <canvas
          ref={overlayCanvasRef}
          className="pointer-events-none absolute inset-0 h-full w-full"
        />
      </div>

      {errorMessage && (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          {errorMessage}
        </p>
      )}

      <canvas ref={captureCanvasRef} className="hidden" />
    </section>
  );
}

export default WebcamFeed;
