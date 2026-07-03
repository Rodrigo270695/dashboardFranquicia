"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import type { PuntoHora } from "@/lib/api";

interface Props {
  datos: PuntoHora[];
}

export default function GraficaHoras({ datos }: Props) {
  const datosFormateados = datos.map((d) => ({
    ...d,
    hora_label: `${String(d.hora).padStart(2, "0")}:00`,
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-700 mb-4">Turnos por hora del día</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={datosFormateados} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="hora_label" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip labelFormatter={(l) => `Hora: ${l}`} formatter={(v: number) => [v, "Turnos"]} />
          <Bar dataKey="total" name="Turnos" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
