/*
  This component shows the current face count.
  It receives the latest count from the webcam detection component.
*/

import { Users } from "lucide-react";

function FaceCounter({ faceCount }) {
  return (
    <section className="rounded-md border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">Current Faces</p>
          <p className="mt-2 text-4xl font-bold text-slate-950">{faceCount}</p>
        </div>

        <div className="flex h-12 w-12 items-center justify-center rounded-md bg-emerald-100 text-emerald-800">
          <Users size={24} />
        </div>
      </div>
    </section>
  );
}

export default FaceCounter;
