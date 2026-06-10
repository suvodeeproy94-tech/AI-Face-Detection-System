/*
  This page explains the project in a short and clear way.
  The main working screen is still the Detection page.
*/

import { CheckCircle2 } from "lucide-react";

function Home() {
  const projectPoints = [
    "Detects faces from a live webcam feed.",
    "Draws bounding boxes around every detected face.",
    "Counts multiple faces in real time.",
    "Shows estimated confidence and processing time.",
    "Stores simple detection history in SQLite.",
  ];

  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-md border border-slate-200 bg-white p-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
          Project Overview
        </p>
        <h2 className="mt-3 text-3xl font-bold text-slate-950">
          AI-Based Real-Time Face Detection System
        </h2>
        <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
          This web application uses React for the user interface and Flask with
          OpenCV for face detection. The browser captures webcam frames, sends
          them to the backend, and receives face box data for live display.
        </p>
      </div>

      <div className="rounded-md border border-slate-200 bg-white p-6">
        <h3 className="text-lg font-bold text-slate-950">Main Features</h3>

        <ul className="mt-4 space-y-3">
          {projectPoints.map((point) => (
            <li className="flex gap-3 text-sm text-slate-700" key={point}>
              <CheckCircle2 className="mt-0.5 shrink-0 text-emerald-700" size={18} />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

export default Home;
