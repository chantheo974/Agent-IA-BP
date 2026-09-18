import React, { lazy, Suspense } from "react";
import ReactDOM from "react-dom/client";
import "@glideapps/glide-data-grid/dist/index.css";
import "./cockpit/app/globals.css";
import "./style.css";
import "./connected/style.css";
import App from "./App";
import { RouterProvider } from "./cockpit/router";
const DemoCockpit = lazy(() => import("./cockpit/DemoCockpit"));

const demo = window.location.pathname === "/demo" || window.location.pathname.startsWith("/demo/");
const atelier = window.location.pathname === "/atelier" || window.location.pathname.startsWith("/atelier/");
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode>
  {demo ? <Suspense fallback={<p>Ouverture de la démonstration…</p>}><DemoCockpit /></Suspense> : atelier ? <div className="legacy-ui"><App /></div> : <RouterProvider><App cockpit /></RouterProvider>}
</React.StrictMode>);
