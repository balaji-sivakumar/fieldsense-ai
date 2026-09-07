import { useEffect, useRef, useState } from "react";

const WS_URL = import.meta.env.VITE_BACKEND_DASHBOARD_WS_URL ?? "ws://localhost:8000/ws/dashboard";

type ToolCallEvent = {
  type: "tool_call";
  tool_name: string;
  args: Record<string, unknown>;
  result: { status: string; result?: unknown; error?: string };
  session_id: string;
};

type ScenarioChangeEvent = {
  type: "scenario_change";
  asset_id: string;
  scenario: string;
};

type FeedEvent = ToolCallEvent | ScenarioChangeEvent;

export default function Dashboard() {
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "tool_call" || msg.type === "scenario_change") {
          setEvents((prev) => [msg, ...prev].slice(0, 50));
        }
      } catch {
        console.error("malformed dashboard message:", event.data);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Live operations feed</h2>
        <span className="hint">every tool call and scenario change, audited</span>
      </div>

      <div className="tool-feed">
        {events.length === 0 && <p className="tool-feed-empty">No activity yet.</p>}
        {events.map((e, i) =>
          e.type === "scenario_change" ? (
            <div key={i} className="tool-call-entry">
              <div className="tool-call-head">
                <span className="tool-name">scenario_change</span>
                <span className="tool-status ok">{e.scenario}</span>
              </div>
              <div className="tool-line">asset: {e.asset_id}</div>
            </div>
          ) : (
            <div key={i} className="tool-call-entry">
              <div className="tool-call-head">
                <span className="tool-name">{e.tool_name}</span>
                <span className={`tool-status ${e.result.status === "ok" ? "ok" : "error"}`}>{e.result.status}</span>
              </div>
              <div className="tool-line">session: {e.session_id}</div>
              <div className="tool-line">args: {JSON.stringify(e.args)}</div>
              <div className="tool-line">result: {JSON.stringify(e.result.result ?? e.result.error)}</div>
            </div>
          ),
        )}
      </div>
    </section>
  );
}
