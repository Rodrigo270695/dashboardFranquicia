"use client";

interface KPICardProps {
  titulo: string;
  valor: string | number;
  subtitulo?: string;
  icono: React.ReactNode;
  color: "azul" | "verde" | "naranja" | "rojo" | "morado" | "gris";
}

const colores = {
  azul: "bg-blue-50 border-blue-200 text-blue-700",
  verde: "bg-emerald-50 border-emerald-200 text-emerald-700",
  naranja: "bg-orange-50 border-orange-200 text-orange-700",
  rojo: "bg-red-50 border-red-200 text-red-700",
  morado: "bg-purple-50 border-purple-200 text-purple-700",
  gris: "bg-gray-50 border-gray-200 text-gray-700",
};

export default function KPICard({ titulo, valor, subtitulo, icono, color }: KPICardProps) {
  return (
    <div className={`rounded-xl border-2 p-5 ${colores[color]} flex items-center gap-4`}>
      <div className="text-3xl">{icono}</div>
      <div>
        <p className="text-sm font-medium opacity-70">{titulo}</p>
        <p className="text-2xl font-bold">{valor}</p>
        {subtitulo && <p className="text-xs opacity-60 mt-0.5">{subtitulo}</p>}
      </div>
    </div>
  );
}
