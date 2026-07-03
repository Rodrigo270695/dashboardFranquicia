"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import type { ItemDimension } from "@/lib/api";

interface Props {
  datos: ItemDimension[];
  titulo: string;
  color?: string;
  horizontal?: boolean;
}

export default function GraficaBarras({ datos, titulo, color = "#3b82f6", horizontal = false }: Props) {
  const top10 = datos.slice(0, 10);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-700 mb-4">{titulo}</h3>
      <ResponsiveContainer width="100%" height={260}>
        {horizontal ? (
          <BarChart data={top10} layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis type="number" tick={{ fontSize: 11 }} />
            <YAxis dataKey="nombre" type="category" tick={{ fontSize: 10 }} width={80} />
            <Tooltip />
            <Bar dataKey="total" name="Turnos" fill={color} radius={[0, 4, 4, 0]} />
          </BarChart>
        ) : (
          <BarChart data={top10} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="nombre" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="total" name="Turnos" fill={color} radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
