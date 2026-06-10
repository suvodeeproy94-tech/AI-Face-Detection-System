/*
  This file controls the main frontend screen.
  It keeps page switching simple so the project is easy to explain.
*/

import { useState } from "react";
import Navbar from "./components/Navbar.jsx";
import Detection from "./pages/Detection.jsx";
import Home from "./pages/Home.jsx";

function App() {
  const [activePage, setActivePage] = useState("detection");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <Navbar activePage={activePage} onPageChange={setActivePage} />

      <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {activePage === "home" ? <Home /> : <Detection />}
      </main>
    </div>
  );
}

export default App;
