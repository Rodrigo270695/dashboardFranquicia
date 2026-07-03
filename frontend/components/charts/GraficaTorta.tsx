"use client";

import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import type { ItemDimension } from "@/lib/api";

const COLORES = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316", "#84cc16"];

interface Props {
  datos: ItemDimension[];
  titulo: string;
}

export default function GraficaTorta({ datos, titulo }: Props) {
  const top8 = datos.slice(0, 8);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-700 mb-4">{titulo}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={top8}
            dataKey="total"
            nameKey="nombre"
            cx="50%"
            cy="50%"
            outerRadius={90}
            label={({ nombre, percent }) => `${(percent * 100).toFixed(0)}%`}
            labelLine={false}
          >
            {top8.map((_, i) => (
              <Cell key={i} fill={COLORES[i % COLORES.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => [v.toLocaleString(), "Turnos"]} />
          <Legend iconType="circle" iconSize={10} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
