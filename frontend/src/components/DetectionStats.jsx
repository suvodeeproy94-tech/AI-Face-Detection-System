/*
  This component displays live detection statistics.
  The data comes from the Flask backend after each webcam frame is processed.
*/

import { BarChart3, Clock, Database, Gauge } from "lucide-react";

function DetectionStats({ latestResult, savedStats }) {
  const averageConfidence = latestResult?.average_confidence || 0;
  const processingTime = latestResult?.processing_time_ms || 0;
  const modelName = latestResult?.model_name || "Waiting for detection";

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard
        icon={<Gauge size={22} />}
        label="Frame Confidence"
        value={`${averageConfidence}%`}
        tone="emerald"
      />

      <StatCard
        icon={<Clock size={22} />}
        label="Processing Time"
        value={`${processingTime} ms`}
        tone="amber"
      />

      <StatCard
        icon={<BarChart3 size={22} />}
        label="Total Frames"
        value={savedStats.total_frames}
        tone="sky"
      />

      <StatCard
        icon={<Database size={22} />}
        label="Model"
        value={modelName}
        tone="slate"
      />
    </section>
  );
}

function StatCard({ icon, label, value, tone }) {
  const toneClass = {
    amber: "bg-amber-100 text-amber-800",
    emerald: "bg-emerald-100 text-emerald-800",
    sky: "bg-sky-100 text-sky-800",
    slate: "bg-slate-100 text-slate-800",
  };

  return (
    <article className="rounded-md border border-slate-200 bg-white p-5">
      <div className="flex items-start gap-4">
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-md ${toneClass[tone]}`}
        >
          {icon}
        </div>

        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-2 break-words text-xl font-bold text-slate-950">
            {value}
          </p>
        </div>
      </div>
    </article>
  );
}

export default DetectionStats;
