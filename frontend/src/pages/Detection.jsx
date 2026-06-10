/*
  This page connects all detection dashboard components.
  It stores the latest result and fetches saved statistics from Flask.
*/

import { useEffect, useState } from "react";
import DetectionHistory from "../components/DetectionHistory.jsx";
import DetectionStats from "../components/DetectionStats.jsx";
import FaceCounter from "../components/FaceCounter.jsx";
import WebcamFeed from "../components/WebcamFeed.jsx";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const emptyStats = {
  total_frames: 0,
  total_faces: 0,
  average_confidence: 0,
  average_processing_time_ms: 0,
  highest_face_count: 0,
};

function Detection() {
  const [latestResult, setLatestResult] = useState(null);
  const [savedStats, setSavedStats] = useState(emptyStats);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    refreshDashboardData();
  }, []);

  async function refreshDashboardData() {
    await Promise.all([fetchStats(), fetchHistory()]);
  }

  async function fetchStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/detection/stats`);
      const responseData = await response.json();

      if (responseData.success) {
        setSavedStats(responseData.data);
      }
    } catch (error) {
      setSavedStats(emptyStats);
    }
  }

  async function fetchHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/detection/history?limit=8`);
      const responseData = await response.json();

      if (responseData.success) {
        setHistory(responseData.data);
      }
    } catch (error) {
      setHistory([]);
    }
  }

  async function resetDetectionData() {
    try {
      await fetch(`${API_BASE_URL}/api/detection/reset`, {
        method: "POST",
      });

      setLatestResult(null);
      await refreshDashboardData();
    } catch (error) {
      setSavedStats(emptyStats);
      setHistory([]);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
            Detection Dashboard
          </p>
          <h2 className="mt-2 text-3xl font-bold text-slate-950">
            Live Face Detection
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            The frontend captures webcam frames and the Flask backend detects
            faces using OpenCV.
          </p>
        </div>

        <button className="btn btn-secondary" type="button" onClick={resetDetectionData}>
          Reset Statistics
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_0.8fr]">
        <WebcamFeed
          onDetectionResult={setLatestResult}
          onStatsRefresh={refreshDashboardData}
        />

        <div className="space-y-4">
          <FaceCounter faceCount={latestResult?.face_count || 0} />

          <section className="rounded-md border border-slate-200 bg-white p-5">
            <h3 className="text-base font-bold text-slate-950">
              Stored Summary
            </h3>

            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <SummaryItem label="Total Faces" value={savedStats.total_faces} />
              <SummaryItem
                label="Highest Count"
                value={savedStats.highest_face_count}
              />
              <SummaryItem
                label="Average Confidence"
                value={`${savedStats.average_confidence}%`}
              />
              <SummaryItem
                label="Average Time"
                value={`${savedStats.average_processing_time_ms} ms`}
              />
            </div>
          </section>
        </div>
      </div>

      <DetectionStats latestResult={latestResult} savedStats={savedStats} />
      <DetectionHistory history={history} />
    </div>
  );
}

function SummaryItem({ label, value }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-bold text-slate-950">{value}</p>
    </div>
  );
}

export default Detection;
