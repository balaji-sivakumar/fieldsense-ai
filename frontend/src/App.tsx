import { useState } from "react";
import { api, type Asset, type ManualResult, type Telemetry, type WorkOrder } from "./api";
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
    <main style={{ maxWidth: 480, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>FieldSense AI — M1 slice</h1>
      <p>
        Asset: <strong>{ASSET_ID}</strong>
      </p>

      <button onClick={() => run(() => api.getAsset(ASSET_ID), setAsset)}>Load asset details</button>
      {asset && <pre>{JSON.stringify(asset, null, 2)}</pre>}

      <button onClick={() => run(() => api.getLiveTelemetry(ASSET_ID), (r) => r.status === "ok" && setTelemetry(r.result))}>
        Get live telemetry
      </button>
      {telemetry && <pre>{JSON.stringify(telemetry, null, 2)}</pre>}

      <button
        onClick={() =>
          run(() => api.searchManual("ACX-200", "E27"), (r) => r.status === "ok" && setManual(r.result))
        }
      >
        Search manual (fault E27)
      </button>
      {manual && <pre>{JSON.stringify(manual, null, 2)}</pre>}

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
      {workOrder && <pre>{JSON.stringify(workOrder, null, 2)}</pre>}

      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}
    </main>
  );
}
