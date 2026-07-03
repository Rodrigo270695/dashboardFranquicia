"use client";

import { Fragment, useMemo } from "react";
import type { FilaEfectividad, MetricaCategoria } from "@/lib/api";

interface Props {
  datos: FilaEfectividad[];
  cargando: boolean;
}

function colorEfectividad(pct: number): string {
  if (pct <= 0) return "text-slate-500";
  if (pct >= 40) return "text-emerald-400 font-bold";
  if (pct >= 25) return "text-amber-400 font-bold";
  return "text-rose-400 font-bold";
}

function bgEfectividad(pct: number): string {
  if (pct <= 0) return "";
  if (pct >= 40) return "bg-emerald-500/10";
  if (pct >= 25) return "bg-amber-500/10";
  return "bg-rose-500/10";
}

function CeldaMetrica({ m, dark = false }: { m: MetricaCategoria; dark?: boolean }) {
  const bg = dark ? "" : bgEfectividad(m.efectividad);
  const color = dark ? "text-slate-200" : colorEfectividad(m.efectividad);
  return (
    <Fragment>
      <td className={`px-3 py-2.5 text-center text-sm ${bg} ${color}`}>
        {m.efectividad > 0 ? `${m.efectividad}%` : "—"}
      </td>
      <td className={`px-3 py-2.5 text-center text-sm ${dark ? "text-slate-300" : "text-slate-300"}`}>
        {m.atenciones > 0 ? m.atenciones.toLocaleString() : "—"}
      </td>
      <td className={`px-3 py-2.5 text-center text-sm ${dark ? "text-slate-300" : "text-slate-400"}`}>
        {m.q_post > 0 ? m.q_post.toLocaleString() : "—"}
      </td>
    </Fragment>
  );
}

function sumarCategoria(
  filas: FilaEfectividad[],
  cat: "consulta" | "compras" | "reclamos"
): MetricaCategoria {
  const aten = filas.reduce((a, f) => a + f[cat].atenciones, 0);
  const q = filas.reduce((a, f) => a + f[cat].q_post, 0);
  const ef = aten > 0 ? Math.round((q / aten) * 1000) / 10 : 0;
  return { atenciones: aten, q_post: q, efectividad: ef };
}

export default function EfectividadTable({ datos, cargando }: Props) {
  const grupos = useMemo(() => {
    const mapa: Record<string, FilaEfectividad[]> = {};
    for (const fila of datos) {
      const key = fila.region?.trim() || "Sin Región";
      if (!mapa[key]) mapa[key] = [];
      mapa[key].push(fila);
    }
    return Object.entries(mapa).sort(([a], [b]) => a.localeCompare(b));
  }, [datos]);

  const totalGeneral = {
    consulta: sumarCategoria(datos, "consulta"),
    compras: sumarCategoria(datos, "compras"),
    reclamos: sumarCategoria(datos, "reclamos"),
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 sm:px-5 py-3 sm:py-4 border-b border-slate-800 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
        <div>
          <h2 className="text-sm sm:text-base font-bold text-white">Efectividad Post-Atención</h2>
          <p className="text-[10px] sm:text-xs text-slate-500 mt-0.5 leading-relaxed">
            Q_post = ventas con estado válido y operación Postpago válida
          </p>
        </div>
        <div className="flex flex-wrap gap-3 text-[10px] sm:text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-emerald-500/30 border border-emerald-500 inline-block" />
            ≥ 40%
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-500/30 border border-amber-500 inline-block" />
            25–39%
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-rose-500/30 border border-rose-500 inline-block" />
            &lt; 25%
          </span>
        </div>
      </div>

      {cargando ? (
        <div className="text-center py-20 text-slate-500 text-sm animate-pulse">Calculando efectividad…</div>
      ) : datos.length === 0 ? (
        <div className="text-center py-20 text-slate-500 text-sm">
          Sin datos. Sube archivos de tickets y ventas para ver la efectividad.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr>
                <th rowSpan={2} className="sticky left-0 z-20 bg-slate-800 text-slate-200 px-3 sm:px-4 py-3 text-left text-[10px] sm:text-xs font-bold uppercase whitespace-nowrap min-w-[140px] sm:min-w-[220px] border-b border-slate-700">
                  Tienda
                </th>
                <th colSpan={3} className="bg-sky-600/80 text-white px-3 py-2 text-center text-xs font-bold uppercase tracking-wide">
                  Consulta
                </th>
                <th colSpan={3} className="bg-emerald-600/80 text-white px-3 py-2 text-center text-xs font-bold uppercase tracking-wide">
                  Compras
                </th>
                <th colSpan={3} className="bg-rose-600/80 text-white px-3 py-2 text-center text-xs font-bold uppercase tracking-wide">
                  Reclamos
                </th>
              </tr>
              <tr className="bg-slate-800 text-slate-400 text-xs border-b border-slate-700">
                {(["CONSULTA", "COMPRAS", "RECLAMOS"] as const).map((cat) => (
                  <Fragment key={cat}>
                    <th className="px-3 py-2 text-center font-medium">Efectiv.</th>
                    <th className="px-3 py-2 text-center font-medium">Atenciones</th>
                    <th className="px-3 py-2 text-center font-medium">Q_post</th>
                  </Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {grupos.map(([region, filas]) => {
                const subConsulta = sumarCategoria(filas, "consulta");
                const subCompras = sumarCategoria(filas, "compras");
                const subReclamos = sumarCategoria(filas, "reclamos");

                return (
                  <Fragment key={region}>
                    <tr className="bg-slate-800/60">
                      <td colSpan={10} className="sticky left-0 bg-slate-800/60 px-4 py-1.5 text-xs font-bold text-slate-400 uppercase tracking-wider">
                        {region}
                      </td>
                    </tr>
                    {filas.map((fila, i) => (
                      <tr
                        key={fila.tienda}
                        className={`border-b border-slate-800/80 hover:bg-slate-800/40 transition-colors ${
                          i % 2 === 0 ? "" : "bg-slate-900/40"
                        }`}
                      >
                        <td className="sticky left-0 bg-inherit px-4 py-2.5 text-sm text-white font-medium whitespace-nowrap max-w-xs truncate">
                          {fila.tienda}
                        </td>
                        <CeldaMetrica m={fila.consulta} />
                        <CeldaMetrica m={fila.compras} />
                        <CeldaMetrica m={fila.reclamos} />
                      </tr>
                    ))}
                    <tr className="bg-slate-800/30 border-t border-slate-700">
                      <td className="sticky left-0 bg-slate-800/30 px-4 py-2 text-xs font-bold text-slate-400 uppercase">
                        Total {region}
                      </td>
                      <CeldaMetrica m={subConsulta} />
                      <CeldaMetrica m={subCompras} />
                      <CeldaMetrica m={subReclamos} />
                    </tr>
                  </Fragment>
                );
              })}
              <tr className="bg-slate-800 border-t-2 border-sky-500/50">
                <td className="sticky left-0 bg-slate-800 px-4 py-3 text-xs font-bold text-white uppercase tracking-wide">
                  Total General
                </td>
                <CeldaMetrica m={totalGeneral.consulta} dark />
                <CeldaMetrica m={totalGeneral.compras} dark />
                <CeldaMetrica m={totalGeneral.reclamos} dark />
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
