"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Menu,
  X,
  LayoutDashboard,
  Upload,
  CheckCircle2,
  History,
  LogOut,
  User,
  type LucideIcon,
} from "lucide-react";
import { clearSession, getUsername } from "@/lib/auth";

const NAV: { href: string; label: string; short: string; icon: LucideIcon }[] = [
  { href: "/", label: "Dashboard", short: "Inicio", icon: LayoutDashboard },
  { href: "/upload", label: "Subir Excel", short: "Subir", icon: Upload },
  { href: "/validacion", label: "Validación", short: "Validar", icon: CheckCircle2 },
  { href: "/historial", label: "Historial", short: "Historial", icon: History },
];

interface Props {
  children: React.ReactNode;
}

function NavLink({
  item,
  active,
  onClick,
  compact = false,
}: {
  item: (typeof NAV)[0];
  active: boolean;
  onClick?: () => void;
  compact?: boolean;
}) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={`flex items-center gap-3 rounded-xl text-sm font-medium transition-all ${
        compact ? "flex-col gap-1 py-2 px-1" : "px-3 py-2.5"
      } ${
        active
          ? compact
            ? "text-sky-400"
            : "bg-sky-500/15 text-sky-400 border border-sky-500/30"
          : compact
            ? "text-slate-500 hover:text-slate-300"
            : "text-slate-400 hover:text-white hover:bg-slate-800"
      }`}
    >
      <Icon className={compact ? "w-5 h-5" : "w-4 h-4 shrink-0"} strokeWidth={active ? 2.5 : 2} />
      <span className={compact ? "text-[10px] leading-tight" : ""}>{compact ? item.short : item.label}</span>
    </Link>
  );
}

export default function AppShell({ children }: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const [username, setUsername] = useState("Usuario");

  useEffect(() => {
    setUsername(getUsername() ?? "Usuario");
  }, []);

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const handleLogout = () => {
    clearSession();
    router.push("/login");
  };

  const isActive = (href: string) => pathname === href;

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Overlay móvil */}
      {menuOpen && (
        <button
          type="button"
          aria-label="Cerrar menú"
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={() => setMenuOpen(false)}
        />
      )}

      {/* Sidebar — drawer en móvil, fijo en desktop */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-slate-900 border-r border-slate-800 shadow-2xl transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          menuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-slate-800 shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-linear-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-sky-500/20 shrink-0">
              DF
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-white text-sm truncate">Dashboard Franquicia</p>
              <p className="text-xs text-slate-400">Efectividad Post</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setMenuOpen(false)}
            className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            aria-label="Cerrar menú"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navegación */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-600">
            Menú
          </p>
          {NAV.map((item) => (
            <NavLink
              key={item.href}
              item={item}
              active={isActive(item.href)}
              onClick={() => setMenuOpen(false)}
            />
          ))}
        </nav>

        {/* Usuario + Salir — siempre al fondo del sidebar */}
        <div className="shrink-0 border-t border-slate-800 p-4 space-y-3 bg-slate-900">
          <div className="flex items-center gap-3 px-2">
            <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0">
              <User className="w-4 h-4 text-slate-400" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[10px] text-slate-500 uppercase tracking-wide">Sesión activa</p>
              <p className="text-sm text-white font-medium truncate">{username}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-red-500/15 border border-slate-700 hover:border-red-500/40 text-slate-300 hover:text-red-400 text-sm font-medium transition-all"
          >
            <LogOut className="w-4 h-4" />
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Contenido principal */}
      <div className="lg:ml-72 flex flex-col min-h-screen">
        {/* Header móvil */}
        <header className="lg:hidden sticky top-0 z-30 flex items-center gap-3 px-4 py-3 bg-slate-900/95 backdrop-blur-md border-b border-slate-800">
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="p-2 -ml-1 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 transition"
            aria-label="Abrir menú"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-white text-sm truncate">Dashboard Franquicia</p>
            <p className="text-[10px] text-slate-500 truncate">
              {NAV.find((n) => isActive(n.href))?.label ?? "Efectividad Post"}
            </p>
          </div>
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0">
            <User className="w-3.5 h-3.5 text-slate-400" />
          </div>
        </header>

        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-4 lg:py-6 pb-[calc(5rem+env(safe-area-inset-bottom))] lg:pb-6">
          {children}
        </main>
      </div>

      {/* Barra inferior fija — solo móvil */}
      <nav
        className="lg:hidden fixed bottom-0 inset-x-0 z-30 bg-slate-900/95 backdrop-blur-md border-t border-slate-800"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        <div className="grid grid-cols-4 px-1 pt-1">
          {NAV.map((item) => (
            <NavLink
              key={item.href}
              item={item}
              active={isActive(item.href)}
              compact
            />
          ))}
        </div>
      </nav>
    </div>
  );
}
