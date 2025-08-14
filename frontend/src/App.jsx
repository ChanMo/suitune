// @ts-check
import React from "react";
import { createRoot } from "react-dom/client";
import Router from "./router.jsx";
import "./styles/index.css";

function App() {
  return <Router />;
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
