"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { PuntoTendencia } from "@/lib/api";

interface Props {
  datos: PuntoTendencia[];
  agrupacion: string;
  onAgrupacionChange: (v: string) => void;
}

export default function GraficaTendencia({ datos, agrupacion, onAgrupacionChange }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-gray-700">Tendencia de Turnos</h3>
        <select
          value={agrupacion}
          onChange={(e) => onAgrupacionChange(e.target.value)}
          className="text-xs border border-gray-300 rounded-lg px-2 py-1 focus:outline-none"
        >
          <option value="dia">Por día</option>
          <option value="semana">Por semana</option>
          <option value="mes">Por mes</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={datos} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="periodo" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="total_turnos"
            name="Total turnos"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
