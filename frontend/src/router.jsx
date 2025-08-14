// @ts-check
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./app/home/index.jsx";
import Favorites from "./app/favorites/index.jsx";
import Search from "./app/search/index.jsx";
import Settings from "./app/settings/index.jsx";
import Now from "./app/now/index.jsx";

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/favorites" element={<Favorites />} />
        <Route path="/search" element={<Search />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/now" element={<Now />} />
      </Routes>
    </BrowserRouter>
  );
}
