// @ts-check
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./app/home";
import Favorites from "./app/favorites";
import Search from "./app/search";
import Settings from "./app/settings";
import Now from "./app/now";

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
