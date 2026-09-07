const BASE_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export type Asset = {
  asset_id: string;
  model: string;
  site_id: string;
  manufacturer: string;
};

export type ToolResult<T> =
  | { status: "ok"; result: T }
  | { status: "error"; error: string };

export type Telemetry = {
  asset_id: string;
  temperature_f: number;
  vibration_mm_s: number;
  discharge_pressure_psi: number;
};

export type ManualResult = {
  asset_model: string;
  document: string;
  section: string;
  page: number;
  content_type: string;
  text: string;
};

export type WorkOrder = {
  work_order_id: number;
  asset_id: string;
  problem: string;
  priority: string;
  status: string;
};

async function getAsset(assetId: string): Promise<Asset> {
  const res = await fetch(`${BASE_URL}/assets/${assetId}`);
  if (!res.ok) {
    const body = await res.json();
    throw new Error(body.detail ?? "failed to fetch asset");
  }
  return res.json();
}

export type Scenario = "normal" | "overheating" | "dangerous_vibration" | "low_pressure";

async function getScenario(assetId: string): Promise<{ asset_id: string; scenario: Scenario }> {
  const res = await fetch(`${BASE_URL}/simulator/scenario/${assetId}`);
  return res.json();
}

async function setScenario(assetId: string, scenario: Scenario): Promise<{ asset_id: string; scenario: Scenario }> {
  const res = await fetch(`${BASE_URL}/simulator/scenario`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ asset_id: assetId, scenario }),
  });
  if (!res.ok) {
    const body = await res.json();
    throw new Error(body.detail ?? "failed to set scenario");
  }
  return res.json();
}

async function callTool<T>(path: string, payload: object): Promise<ToolResult<T>> {
  const res = await fetch(`${BASE_URL}/tools/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export const api = {
  getAsset,
  getLiveTelemetry: (assetId: string) => callTool<Telemetry>("get_live_telemetry", { asset_id: assetId }),
  searchManual: (assetModel: string, faultCode: string) =>
    callTool<ManualResult>("search_manual", { asset_model: assetModel, fault_code: faultCode }),
  createWorkOrder: (assetId: string, problem: string, priority: string) =>
    callTool<WorkOrder>("create_work_order", { asset_id: assetId, problem, priority }),
  getScenario,
  setScenario,
};
