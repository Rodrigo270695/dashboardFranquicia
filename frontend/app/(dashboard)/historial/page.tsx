"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { cargasApi, type CargaResponse } from "@/lib/api";

export default function HistorialPage() {
  const [cargas, setCargas] = useState<CargaResponse[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargasApi.listar().then(setCargas).catch(() => {}).finally(() => setCargando(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Historial de Cargas</h1>
        <p className="text-sm text-slate-400 mt-1">Registro de todos los archivos Excel subidos</p>
      </div>

      {cargando ? (
        <div className="text-center py-20 text-slate-500 animate-pulse">Cargando historial...</div>
      ) : cargas.length === 0 ? (
        <div className="text-center py-20 text-slate-500">
          <p className="text-5xl mb-4">📭</p>
          <p>Aún no se han subido archivos</p>
          <Link href="/upload" className="mt-4 inline-block bg-sky-600 text-white px-4 py-2 rounded-lg text-sm">
            Subir primer archivo
          </Link>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800 border-b border-slate-700">
              <tr>
                {["#", "Archivo", "Fecha", "Total", "Nuevos", "Duplicados", "Errores"].map((h, i) => (
                  <th key={h} className={`px-4 py-3 text-xs font-semibold text-slate-400 uppercase ${i >= 3 ? "text-right" : "text-left"}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {cargas.map((c) => (
                <tr key={c.id} className="hover:bg-slate-800/50 transition">
                  <td className="px-4 py-3 text-slate-500">{c.id}</td>
                  <td className="px-4 py-3 font-medium text-white">{c.nombre_archivo}</td>
                  <td className="px-4 py-3 text-slate-400">{new Date(c.fecha_carga).toLocaleString("es-PE")}</td>
                  <td className="px-4 py-3 text-right text-slate-300">{c.registros_totales.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-emerald-400 font-medium">{c.registros_nuevos.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-amber-400">{c.registros_duplicados.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-red-400">{c.registros_con_error.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
