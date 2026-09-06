import { useEffect, useRef, useState } from "react";

const WS_URL = import.meta.env.VITE_BACKEND_DASHBOARD_WS_URL ?? "ws://localhost:8000/ws/dashboard";

type ToolCallEvent = {
  type: "tool_call";
  tool_name: string;
  args: Record<string, unknown>;
  result: { status: string; result?: unknown; error?: string };
  session_id: string;
};

export default function Dashboard() {
  const [events, setEvents] = useState<ToolCallEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "tool_call") {
          setEvents((prev) => [msg, ...prev].slice(0, 50));
        }
      } catch {
        console.error("malformed dashboard message:", event.data);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <section style={{ marginTop: "2rem", borderTop: "1px solid #ccc", paddingTop: "1rem" }}>
      <h2>M3 — Live tool call feed (dashboard)</h2>
      {events.length === 0 && <p>No tool calls yet.</p>}
      {events.map((e, i) => (
        <div key={i} style={{ marginBottom: "0.75rem", fontFamily: "monospace", fontSize: "0.85rem" }}>
          <div>
            <strong>{e.tool_name}</strong> [{e.session_id}] — {e.result.status}
          </div>
          <div>args: {JSON.stringify(e.args)}</div>
          <div>result: {JSON.stringify(e.result.result ?? e.result.error)}</div>
        </div>
      ))}
    </section>
  );
}
