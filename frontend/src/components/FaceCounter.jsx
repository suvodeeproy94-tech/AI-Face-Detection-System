/*
  This component shows the current face count.
  It receives the latest count from the webcam detection component.
*/

import { ShieldCheck, Users } from "lucide-react";

function FaceCounter({ faceCount, latestResult }) {
  const modelName = latestResult?.model_name || "Waiting for model";
  const confidence = latestResult?.average_confidence || 0;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">Current Faces</p>
          <p className="mt-2 text-5xl font-bold tracking-tight text-slate-950">
            {faceCount}
          </p>
        </div>

        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800">
          <Users size={24} />
        </div>
      </div>

      <div className="mt-5 rounded-md bg-slate-50 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          <ShieldCheck size={17} />
          Detection Status
        </div>

        <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-xs font-medium text-slate-500">Confidence</p>
            <p className="mt-1 font-bold text-slate-950">{confidence}%</p>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Model</p>
            <p className="mt-1 font-bold leading-5 text-slate-950">{modelName}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default FaceCounter;
