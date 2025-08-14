// @ts-check
import React, { useEffect, useState } from "react";
import { fetchSettings, updateSettings } from "../../core/api/client";

export default function Settings() {
  const [settings, setSettings] = useState({ volume: 1, dark_mode: false });
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetchSettings().then(setSettings).catch(console.error);
  }, []);

  const handleChange = (e) => {
    const { name, type, checked, value } = e.target;
    setSettings((s) => ({
      ...s,
      [name]: type === "checkbox" ? checked : parseFloat(value),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateSettings(settings)
      .then(() => setStatus("Saved"))
      .catch(() => setStatus("Error"));
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">Volume: {settings.volume}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            name="volume"
            value={settings.volume}
            onChange={handleChange}
            className="w-full"
          />
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="dark_mode"
            name="dark_mode"
            checked={settings.dark_mode}
            onChange={handleChange}
            className="mr-2"
          />
          <label htmlFor="dark_mode">Dark Mode</label>
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-indigo-600 text-white rounded"
        >
          Save
        </button>
        {status && <p className="text-sm text-gray-500">{status}</p>}
      </form>
    </div>
  );
}
