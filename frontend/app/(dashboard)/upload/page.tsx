"use client";

import { useState, useRef } from "react";
import { cargasApi } from "@/lib/api";

type TipoArchivo = "tickets" | "ventas";

const TIPOS: { id: TipoArchivo; label: string; descripcion: string; icono: string }[] = [
  { id: "tickets", label: "Tickets de Atención", descripcion: "Reporte de turnos y atención al cliente", icono: "🎫" },
  { id: "ventas", label: "Ventas", descripcion: "Reporte de operaciones y ventas", icono: "💼" },
];

export default function UploadPage() {
  const [tipo, setTipo] = useState<TipoArchivo | null>(null);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [estado, setEstado] = useState<"idle" | "cargando" | "exito" | "error">("idle");
  const [resultado, setResultado] = useState<Record<string, unknown> | null>(null);
  const [mensajeError, setMensajeError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleTipo = (t: TipoArchivo) => {
    setTipo(t);
    setArchivo(null);
    setEstado("idle");
    setResultado(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleSubir = async () => {
    if (!archivo || !tipo) return;
    setEstado("cargando");
    try {
      const res = tipo === "tickets"
        ? await cargasApi.subirTickets(archivo)
        : await cargasApi.subirVentas(archivo);
      setResultado(res);
      setEstado("exito");
      setArchivo(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setMensajeError(err.response?.data?.detail ?? "Error al procesar el archivo");
      setEstado("error");
    }
  };

  const tipoSeleccionado = TIPOS.find((t) => t.id === tipo);

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Cargar Archivo Excel</h1>
        <p className="text-sm text-slate-400 mt-1">Selecciona el tipo de archivo y súbelo al sistema</p>
      </div>

      <div>
        <p className="text-sm font-medium text-slate-400 mb-3">¿Qué archivo vas a cargar?</p>
        <div className="grid grid-cols-2 gap-4">
          {TIPOS.map((t) => (
            <button
              key={t.id}
              onClick={() => handleTipo(t.id)}
              className={`border rounded-xl p-5 text-left transition ${
                tipo === t.id
                  ? "border-sky-500 bg-sky-500/10 text-sky-300"
                  : "border-slate-700 bg-slate-900 text-slate-400 hover:border-slate-600"
              }`}
            >
              <div className="text-3xl mb-2">{t.icono}</div>
              <p className="font-semibold text-sm text-white">{t.label}</p>
              <p className="text-xs opacity-70 mt-1">{t.descripcion}</p>
            </button>
          ))}
        </div>
      </div>

      {tipo && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
          <p className="text-sm text-slate-300">
            Cargando: <span className="font-bold text-white">{tipoSeleccionado?.label}</span>
          </p>

          <div
            className="border-2 border-dashed border-slate-700 rounded-xl p-10 text-center cursor-pointer hover:border-sky-500 hover:bg-sky-500/5 transition"
            onClick={() => inputRef.current?.click()}
          >
            <div className="text-4xl mb-2">📂</div>
            <p className="text-slate-300 font-medium text-sm">Haz clic para seleccionar el archivo</p>
            <p className="text-slate-500 text-xs mt-1">Formatos: .xlsx, .xls</p>
            {archivo && <p className="mt-3 text-sky-400 font-medium text-sm">{archivo.name}</p>}
          </div>

          <input ref={inputRef} type="file" accept=".xlsx,.xls" onChange={(e) => setArchivo(e.target.files?.[0] ?? null)} className="hidden" />

          <button
            onClick={handleSubir}
            disabled={!archivo || estado === "cargando"}
            className="w-full bg-sky-600 hover:bg-sky-500 text-white py-3 rounded-lg font-semibold disabled:opacity-50 transition"
          >
            {estado === "cargando" ? "Procesando..." : `Subir ${tipoSeleccionado?.label}`}
          </button>

          {estado === "exito" && resultado && (
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-5 space-y-2 text-sm text-emerald-300">
              <p className="font-semibold">Archivo procesado correctamente</p>
              <p>Total: <strong>{String(resultado.registros_totales)}</strong></p>
              <p>Nuevos: <strong>{String(resultado.registros_nuevos)}</strong></p>
              <p>Duplicados: <strong>{String(resultado.registros_duplicados)}</strong></p>
              <p>Errores: <strong>{String(resultado.registros_con_error)}</strong></p>
            </div>
          )}

          {estado === "error" && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm">{mensajeError}</div>
          )}
        </div>
      )}
    </div>
  );
}
