/*
  This component shows the top navigation bar.
  It lets the user switch between project overview and live detection.
*/

import { Activity, Camera, Home } from "lucide-react";

function Navbar({ activePage, onPageChange }) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-emerald-700 text-white">
            <Camera size={22} />
          </div>

          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
              AI Face Detection
            </p>
            <h1 className="text-lg font-bold text-slate-950">
              Real-Time Webcam Detection System
            </h1>
          </div>
        </div>

        <nav className="flex gap-2">
          <button
            className={getButtonClass(activePage === "home")}
            type="button"
            onClick={() => onPageChange("home")}
          >
            <Home size={18} />
            Overview
          </button>

          <button
            className={getButtonClass(activePage === "detection")}
            type="button"
            onClick={() => onPageChange("detection")}
          >
            <Activity size={18} />
            Detection
          </button>
        </nav>
      </div>
    </header>
  );
}

function getButtonClass(isActive) {
  const baseClass =
    "inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition";

  if (isActive) {
    return `${baseClass} bg-slate-950 text-white`;
  }

  return `${baseClass} border border-slate-200 bg-white text-slate-700 hover:bg-slate-100`;
}

export default Navbar;
