"use client";

import { Fragment, useEffect, useState, useCallback } from "react";
import { efectividadApi, type ValidacionTienda } from "@/lib/api";

const CATEGORIAS: Record<string, string[]> = {
  Consulta: ["consulta", "consulta hogar"],
  Compras: ["compras", "compras hogar", "compras ruc 20"],
  Reclamos: ["reclamo", "reclamo hogar"],
};

function agruparPorCategoria(botones: ValidacionTienda["botones"]) {
  const out: Record<string, number> = { Consulta: 0, Compras: 0, Reclamos: 0, Otros: 0 };
  for (const b of botones) {
    const key = b.boton.toLowerCase();
    let asignado = false;
    for (const [cat, vals] of Object.entries(CATEGORIAS)) {
      if (vals.includes(key)) { out[cat] += b.total; asignado = true; break; }
    }
    if (!asignado) out["Otros"] += b.total;
  }
  return out;
}

export default function ValidacionPage() {
  const [filtros, setFiltros] = useState({ fechaInicio: "", fechaFin: "" });
  const [datos, setDatos] = useState<ValidacionTienda[]>([]);
  const [cargando, setCargando] = useState(true);
  const [expandida, setExpandida] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    setCargando(true);
    const params: Record<string, string> = {};
    if (filtros.fechaInicio) params.fecha_inicio = filtros.fechaInicio;
    if (filtros.fechaFin) params.fecha_fin = filtros.fechaFin;
    try { setDatos(await efectividadApi.validacion(params)); }
    catch { setDatos([]); }
    finally { setCargando(false); }
  }, [filtros]);

  useEffect(() => { cargar(); }, [cargar]);

  const totalGeneral = datos.reduce((a, t) => a + t.total_tickets, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Validación de Datos</h1>
        <p className="text-sm text-slate-400 mt-1">Desglose de tickets por tienda — para cruzar con Excel</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 flex flex-wrap gap-4 items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-slate-400">Desde</label>
          <input type="date" value={filtros.fechaInicio} onChange={(e) => setFiltros((p) => ({ ...p, fechaInicio: e.target.value }))}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-slate-400">Hasta</label>
          <input type="date" value={filtros.fechaFin} onChange={(e) => setFiltros((p) => ({ ...p, fechaFin: e.target.value }))}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500" />
        </div>
        <button onClick={() => setFiltros({ fechaInicio: "", fechaFin: "" })} className="px-4 py-2 text-sm text-slate-400 border border-slate-700 rounded-lg hover:bg-slate-800">Limpiar</button>
        <button onClick={cargar} className="px-5 py-2 text-sm bg-sky-600 text-white rounded-lg hover:bg-sky-500 font-medium">Aplicar</button>
        {!cargando && (
          <div className="ml-auto text-sm text-slate-400">
            <strong className="text-white">{datos.length}</strong> tiendas ·{" "}
            <strong className="text-white">{totalGeneral.toLocaleString()}</strong> tickets
          </div>
        )}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {cargando ? (
          <div className="text-center py-16 text-slate-500 animate-pulse">Cargando...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-slate-800 text-slate-300 text-xs uppercase">
                  <th className="px-4 py-3 text-left">Tienda</th>
                  <th className="px-4 py-3 text-center">Consulta</th>
                  <th className="px-4 py-3 text-center">Compras</th>
                  <th className="px-4 py-3 text-center">Reclamos</th>
                  <th className="px-4 py-3 text-center">Otros</th>
                  <th className="px-4 py-3 text-center">Total</th>
                  <th className="px-4 py-3 text-center">Período</th>
                </tr>
              </thead>
              <tbody>
                {datos.map((t, i) => {
                  const cats = agruparPorCategoria(t.botones);
                  const isOpen = expandida === t.tienda;
                  return (
                    <Fragment key={t.tienda}>
                      <tr
                        className={`border-b border-slate-800 cursor-pointer hover:bg-slate-800/50 ${i % 2 === 0 ? "" : "bg-slate-900/50"}`}
                        onClick={() => setExpandida(isOpen ? null : t.tienda)}
                      >
                        <td className="px-4 py-3 font-medium text-white">
                          <span className={`text-slate-500 text-xs mr-2 inline-block transition-transform ${isOpen ? "rotate-90" : ""}`}>▶</span>
                          {t.tienda}
                        </td>
                        <td className="px-4 py-3 text-center text-sky-400">{cats.Consulta.toLocaleString()}</td>
                        <td className="px-4 py-3 text-center text-emerald-400">{cats.Compras.toLocaleString()}</td>
                        <td className="px-4 py-3 text-center text-rose-400">{cats.Reclamos.toLocaleString()}</td>
                        <td className="px-4 py-3 text-center text-slate-500">{cats.Otros.toLocaleString()}</td>
                        <td className="px-4 py-3 text-center font-bold text-white">{t.total_tickets.toLocaleString()}</td>
                        <td className="px-4 py-3 text-center text-xs text-slate-500">{t.desde} — {t.hasta}</td>
                      </tr>
                      {isOpen && (
                        <tr className="bg-slate-800/30">
                          <td colSpan={7} className="px-8 py-3">
                            <div className="flex flex-wrap gap-2">
                              {t.botones.map((b) => (
                                <span key={b.boton} className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300">
                                  <span className="font-semibold">{b.boton}</span>
                                  <span className="ml-1.5 text-sky-400 font-bold">{b.total.toLocaleString()}</span>
                                </span>
                              ))}
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
