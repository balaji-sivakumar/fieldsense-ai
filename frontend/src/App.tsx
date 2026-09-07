import { useState } from "react";
import { api, type Asset, type ManualResult, type Telemetry, type WorkOrder } from "./api";
import VoicePanel from "./VoicePanel";
import Dashboard from "./Dashboard";
import "./App.css";

const ASSET_ID = "AC-104";

export default function App() {
  const [asset, setAsset] = useState<Asset | null>(null);
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [manual, setManual] = useState<ManualResult | null>(null);
  const [workOrder, setWorkOrder] = useState<WorkOrder | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run<T>(fn: () => Promise<T>, onSuccess: (value: T) => void) {
    setError(null);
    try {
      onSuccess(await fn());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>FieldSense AI</h1>
        <p className="subtitle">Asset {ASSET_ID} — technician tools, voice session, and live operations feed</p>
      </header>

      <div className="layout">
        <div className="column">
          <section className="panel">
            <div className="panel-header">
              <h2>Asset tools</h2>
              <span className="hint">M1 — direct REST calls</span>
            </div>

            <div className="button-row">
              <button onClick={() => run(() => api.getAsset(ASSET_ID), setAsset)}>Load asset details</button>
              <button
                onClick={() =>
                  run(() => api.getLiveTelemetry(ASSET_ID), (r) => r.status === "ok" && setTelemetry(r.result))
                }
              >
                Get live telemetry
              </button>
              <button
                onClick={() =>
                  run(() => api.searchManual("ACX-200", "E27"), (r) => r.status === "ok" && setManual(r.result))
                }
              >
                Search manual (fault E27)
              </button>
              <button
                onClick={() =>
                  run(
                    () => api.createWorkOrder(ASSET_ID, "Compressor will not start, fault E27", "high"),
                    (r) => r.status === "ok" && setWorkOrder(r.result),
                  )
                }
              >
                Create work order
              </button>
            </div>

            {asset && <pre>{JSON.stringify(asset, null, 2)}</pre>}
            {telemetry && <pre>{JSON.stringify(telemetry, null, 2)}</pre>}
            {manual && <pre>{JSON.stringify(manual, null, 2)}</pre>}
            {workOrder && <pre>{JSON.stringify(workOrder, null, 2)}</pre>}
            {error && <p className="error-text">Error: {error}</p>}
          </section>

          <VoicePanel />
        </div>

        <div className="column">
          <Dashboard />
        </div>
      </div>
    </div>
  );
}
