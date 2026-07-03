"use client";

interface FiltrosProps {
  oficinas: string[];
  filtros: {
    fechaInicio: string;
    fechaFin: string;
    oficina: string;
  };
  onChange: (key: string, value: string) => void;
}

export default function FiltrosDashboard({ oficinas, filtros, onChange }: FiltrosProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-4 items-end">
      <div className="flex flex-col gap-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Desde</label>
        <input
          type="date"
          value={filtros.fechaInicio}
          onChange={(e) => onChange("fechaInicio", e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Hasta</label>
        <input
          type="date"
          value={filtros.fechaFin}
          onChange={(e) => onChange("fechaFin", e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Oficina</label>
        <select
          value={filtros.oficina}
          onChange={(e) => onChange("oficina", e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[180px]"
        >
          <option value="">Todas las oficinas</option>
          {oficinas.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      </div>
      <button
        onClick={() => {
          onChange("fechaInicio", "");
          onChange("fechaFin", "");
          onChange("oficina", "");
        }}
        className="px-4 py-2 text-sm text-gray-500 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
      >
        Limpiar filtros
      </button>
    </div>
  );
}
