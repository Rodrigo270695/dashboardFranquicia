"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { setSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      const data = await authApi.login(username, password);
      setSession(data.access_token, data.username);
      router.push("/");
      router.refresh();
    } catch {
      setError("Usuario o contraseña incorrectos");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-sky-950 to-indigo-950 p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-20 w-72 h-72 bg-sky-500 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-indigo-600 rounded-full blur-3xl" />
        </div>
        <div className="relative">
          <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur flex items-center justify-center text-white font-bold text-xl border border-white/20">
            DF
          </div>
        </div>
        <div className="relative space-y-4">
          <h2 className="text-4xl font-bold text-white leading-tight">
            Dashboard de<br />Efectividad
          </h2>
          <p className="text-slate-300 text-lg max-w-md">
            Cruce de tickets y ventas por tienda. Consulta, Compras y Reclamos en un solo lugar.
          </p>
        </div>
        <p className="relative text-slate-500 text-sm">Dashboard Franquicia © 2026</p>
      </div>

      {/* Formulario */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-950">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 items-center justify-center text-white font-bold text-xl mb-4">
              DF
            </div>
            <h1 className="text-2xl font-bold text-white">Dashboard Franquicia</h1>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
            <h2 className="text-xl font-semibold text-white mb-1">Iniciar sesión</h2>
            <p className="text-sm text-slate-400 mb-6">Ingresa tus credenciales para continuar</p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Usuario</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition"
                  placeholder="admin"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Contraseña</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={cargando}
                className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-medium py-2.5 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-sky-500/20"
              >
                {cargando ? "Ingresando…" : "Ingresar"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
