import { useEffect, useState } from "react";

const BASE_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";
const POLL_INTERVAL_MS = 30_000;

type Health = {
  status: "ok" | "degraded";
  database: string;
  manual_search: string;
  voice: string;
};

export default function SystemStatus() {
  const [health, setHealth] = useState<Health | null>(null);
  const [unreachable, setUnreachable] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const res = await fetch(`${BASE_URL}/health`);
        const body = await res.json();
        if (!cancelled) {
          setHealth(body);
          setUnreachable(false);
        }
      } catch {
        if (!cancelled) setUnreachable(true);
      }
    }

    check();
    const id = setInterval(check, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (unreachable) {
    return (
      <div className="status-banner status-banner-error">
        Backend unreachable — the server may be down or still starting up.
      </div>
    );
  }

  if (!health || health.status === "ok") return null;

  const problems: string[] = [];
  if (health.database !== "ok") problems.push("database");
  if (health.manual_search !== "ok") problems.push("manual search");
  if (health.voice !== "configured") problems.push("voice");

  return (
    <div className="status-banner status-banner-error">
      Degraded: {problems.join(", ")} unavailable. Some features may not work.
    </div>
  );
}
