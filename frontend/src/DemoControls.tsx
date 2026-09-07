import { useEffect, useState } from "react";
import { api, type Scenario } from "./api";

const ASSET_ID = "AC-104";

const SCENARIOS: { value: Scenario; label: string }[] = [
  { value: "normal", label: "Normal" },
  { value: "overheating", label: "Overheating" },
  { value: "dangerous_vibration", label: "Dangerous vibration" },
  { value: "low_pressure", label: "Low discharge pressure" },
];

export default function DemoControls() {
  const [active, setActive] = useState<Scenario | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getScenario(ASSET_ID)
      .then((r) => setActive(r.scenario))
      .catch(() => setActive(null));
  }, []);

  async function select(scenario: Scenario) {
    setError(null);
    try {
      const r = await api.setScenario(ASSET_ID, scenario);
      setActive(r.scenario);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Demo controls</h2>
        <span className="hint">sets AC-104's simulated panel reading</span>
      </div>

      <div className="button-row">
        {SCENARIOS.map((s) => (
          <button key={s.value} className={active === s.value ? "primary" : ""} onClick={() => select(s.value)}>
            {s.label}
          </button>
        ))}
      </div>

      {error && <p className="error-text">Error: {error}</p>}
    </section>
  );
}
