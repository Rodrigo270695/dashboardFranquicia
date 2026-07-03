import axios from "axios";
import { clearSession, getToken } from "./auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes("/auth/login");
    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      !isLoginRequest
    ) {
      clearSession();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export interface LoginResponse {
  access_token: string;
  token_type: string;
  username: string;
}

export const authApi = {
  login: (username: string, password: string) =>
    api
      .post<LoginResponse>("/auth/login", { username, password })
      .then((r) => r.data),
};

export interface ResumenKPI {
  total_turnos: number;
  turnos_atendidos: number;
  turnos_derivados: number;
  promedio_espera_min: number | null;
  promedio_atencion_min: number | null;
  oficinas_activas: number;
}

export interface PuntoTendencia {
  periodo: string;
  total_turnos: number;
  promedio_espera_min: number | null;
}

export interface ItemDimension {
  nombre: string;
  total: number;
  promedio_espera_min: number | null;
}

export interface PuntoHora {
  hora: number;
  total: number;
}

export interface CargaResponse {
  id: number;
  nombre_archivo: string;
  registros_totales: number;
  registros_nuevos: number;
  registros_duplicados: number;
  registros_con_error: number;
  fecha_carga: string;
}

export const statsApi = {
  resumen: (params?: Record<string, string>) =>
    api.get<ResumenKPI>("/stats/resumen", { params }).then((r) => r.data),

  tendencia: (params?: Record<string, string>) =>
    api.get<PuntoTendencia[]>("/stats/tendencia", { params }).then((r) => r.data),

  porOficina: (params?: Record<string, string>) =>
    api.get<ItemDimension[]>("/stats/por-oficina", { params }).then((r) => r.data),

  porServicio: (params?: Record<string, string>) =>
    api.get<ItemDimension[]>("/stats/por-servicio", { params }).then((r) => r.data),

  porSegmento: (params?: Record<string, string>) =>
    api.get<ItemDimension[]>("/stats/por-segmento", { params }).then((r) => r.data),

  porBoton: (params?: Record<string, string>) =>
    api.get<ItemDimension[]>("/stats/por-boton", { params }).then((r) => r.data),

  porHora: (params?: Record<string, string>) =>
    api.get<PuntoHora[]>("/stats/por-hora", { params }).then((r) => r.data),
};

export const filtrosApi = {
  oficinas: () => api.get<string[]>("/filtros/oficinas").then((r) => r.data),
  servicios: () => api.get<string[]>("/filtros/servicios").then((r) => r.data),
  segmentos: () => api.get<string[]>("/filtros/segmentos").then((r) => r.data),
};

export interface MetricaCategoria {
  atenciones: number;
  q_post: number;
  efectividad: number;
}

export interface FilaEfectividad {
  tienda: string;
  region: string;
  consulta: MetricaCategoria;
  compras: MetricaCategoria;
  reclamos: MetricaCategoria;
}

export interface BotonResumen {
  boton: string;
  total: number;
}

export interface ValidacionTienda {
  tienda: string;
  total_tickets: number;
  botones: BotonResumen[];
  desde: string;
  hasta: string;
}

export interface RangoFechas {
  fecha_inicio: string;
  fecha_fin: string;
  fecha_min: string;
  fecha_max: string;
  max_turnos: string | null;
  max_ventas: string | null;
}

export const efectividadApi = {
  obtener: (params?: Record<string, string>) =>
    api.get<FilaEfectividad[]>("/stats/efectividad", { params }).then((r) => r.data),
  validacion: (params?: Record<string, string>) =>
    api.get<ValidacionTienda[]>("/stats/validacion", { params }).then((r) => r.data),
  rangoFechas: () =>
    api.get<RangoFechas>("/stats/rango-fechas").then((r) => r.data),
};

export const cargasApi = {
  listar: () => api.get<CargaResponse[]>("/cargas").then((r) => r.data),
  subirTickets: (archivo: File) => {
    const form = new FormData();
    form.append("archivo", archivo);
    return api.post("/cargas/upload", form).then((r) => r.data);
  },
  subirVentas: (archivo: File) => {
    const form = new FormData();
    form.append("archivo", archivo);
    return api.post("/ventas/upload", form).then((r) => r.data);
  },
};
