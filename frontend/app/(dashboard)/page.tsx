"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { efectividadApi, type FilaEfectividad, type RangoFechas } from "@/lib/api";
import EfectividadTable from "@/components/efectividad/EfectividadTable";

function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent: string;
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 sm:p-5 relative overflow-hidden">
      <div className={`absolute top-0 left-0 w-1 h-full ${accent}`} />
      <p className="text-[10px] sm:text-xs font-medium text-slate-400 uppercase tracking-wide">{label}</p>
      <p className="text-lg sm:text-2xl font-bold text-white mt-1">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [filtros, setFiltros] = useState({ fechaInicio: "", fechaFin: "" });
  const [rango, setRango] = useState<RangoFechas | null>(null);
  const [datos, setDatos] = useState<FilaEfectividad[]>([]);
  const [cargando, setCargando] = useState(true);
  const [rangoListo, setRangoListo] = useState(false);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    const params: Record<string, string> = {};
    if (filtros.fechaInicio) params.fecha_inicio = filtros.fechaInicio;
    if (filtros.fechaFin) params.fecha_fin = filtros.fechaFin;
    try {
      setDatos(await efectividadApi.obtener(params));
    } catch {
      setDatos([]);
    } finally {
      setCargando(false);
    }
  }, [filtros]);

  useEffect(() => {
    efectividadApi
      .rangoFechas()
      .then((r) => {
        setRango(r);
        setFiltros({ fechaInicio: r.fecha_inicio, fechaFin: r.fecha_fin });
      })
      .catch(() => {
        const hoy = new Date();
        const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
          .toISOString()
          .slice(0, 10);
        const hoyTexto = hoy.toISOString().slice(0, 10);
        setFiltros({ fechaInicio: inicioMes, fechaFin: hoyTexto });
      })
      .finally(() => setRangoListo(true));
  }, []);

  useEffect(() => {
    if (rangoListo) cargarDatos();
  }, [cargarDatos, rangoListo]);

  const resumen = useMemo(() => {
    const atenciones = datos.reduce(
      (a, f) => a + f.consulta.atenciones + f.compras.atenciones + f.reclamos.atenciones,
      0
    );
    const qpost = datos.reduce(
      (a, f) => a + f.consulta.q_post + f.compras.q_post + f.reclamos.q_post,
      0
    );
    const efGlobal =
      atenciones > 0 ? Math.round((qpost / atenciones) * 1000) / 10 : 0;
    return { tiendas: datos.length, atenciones, qpost, efGlobal };
  }, [datos]);

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-white">Dashboard de Efectividad</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Consulta · Compras · Reclamos — cruce tickets × ventas
        </p>
      </div>

      {/* KPIs */}
      {!cargando && datos.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <StatCard label="Tiendas" value={String(resumen.tiendas)} accent="bg-sky-500" />
          <StatCard
            label="Atenciones"
            value={resumen.atenciones.toLocaleString()}
            accent="bg-indigo-500"
          />
          <StatCard
            label="Q_post"
            value={resumen.qpost.toLocaleString()}
            sub="Estados válidos"
            accent="bg-emerald-500"
          />
          <StatCard
            label="Efectividad global"
            value={`${resumen.efGlobal}%`}
            accent="bg-amber-500"
          />
        </div>
      )}

      {/* Filtros */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl px-4 sm:px-5 py-4 flex flex-col sm:flex-row sm:flex-wrap gap-3 sm:gap-4 sm:items-end">
        <div className="grid grid-cols-2 gap-3 sm:flex sm:gap-4 flex-1">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-400">Desde</label>
            <input
              type="date"
              value={filtros.fechaInicio}
              onChange={(e) => setFiltros((p) => ({ ...p, fechaInicio: e.target.value }))}
              min={rango?.fecha_min}
              max={rango?.fecha_max}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-400">Hasta</label>
            <input
              type="date"
              value={filtros.fechaFin}
              onChange={(e) => setFiltros((p) => ({ ...p, fechaFin: e.target.value }))}
              min={filtros.fechaInicio || rango?.fecha_min}
              max={rango?.fecha_max}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
        </div>
        {rango && (
          <p className="text-xs text-slate-500 sm:order-last sm:w-full">
            Mes actual disponible: {rango.fecha_inicio} al {rango.fecha_max}
            {rango.max_turnos && ` · Tickets hasta ${rango.max_turnos}`}
            {rango.max_ventas && ` · Ventas hasta ${rango.max_ventas}`}
          </p>
        )}
        <div className="flex gap-2 sm:gap-3">
          <button
            onClick={() =>
              setFiltros({
                fechaInicio: rango?.fecha_inicio ?? "",
                fechaFin: rango?.fecha_fin ?? "",
              })
            }
            className="flex-1 sm:flex-none px-4 py-2 text-sm text-slate-400 border border-slate-700 rounded-lg hover:bg-slate-800 transition"
          >
            Limpiar
          </button>
          <button
            onClick={cargarDatos}
            className="flex-1 sm:flex-none px-5 py-2 text-sm bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition font-medium"
          >
            Aplicar
          </button>
        </div>
      </div>

      <EfectividadTable datos={datos} cargando={cargando} />
    </div>
  );
}
