import { useEffect, useRef, useState } from "react";
import { AudioPlayer, MicStreamer } from "./voice";

const WS_URL = import.meta.env.VITE_BACKEND_WS_URL ?? "ws://localhost:8000/ws/voice";

type SessionState = "idle" | "connecting" | "ready" | "listening" | "thinking" | "speaking" | "error" | "closed";

type TranscriptTurn = { speaker: "user" | "agent"; text: string };

const RISK_LABELS: Record<string, string> = {
  observation: "Observation",
  low_risk_inspection: "Low-risk inspection",
  lockout_required: "Lockout required",
  specialist_required: "Specialist required",
  dangerous_condition: "Dangerous condition",
};

export default function VoicePanel() {
  const [state, setState] = useState<SessionState>("idle");
  const [turns, setTurns] = useState<TranscriptTurn[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [riskTier, setRiskTier] = useState<string>("observation");

  const wsRef = useRef<WebSocket | null>(null);
  const micRef = useRef<MicStreamer | null>(null);
  const playerRef = useRef<AudioPlayer | null>(null);
  const partialTextRef = useRef<{ user: string; agent: string }>({ user: "", agent: "" });

  useEffect(() => {
    return () => {
      stopSession();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    };
  }, []);

  function appendTurn(turn: TranscriptTurn) {
    setTurns((prev) => [...prev, turn]);
  }

  async function startSession() {
    setErrorMessage(null);
    setTurns([]);
    setRiskTier("observation");
    setState("connecting");

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    playerRef.current = new AudioPlayer();

    ws.onopen = async () => {
      try {
        const mic = new MicStreamer((chunk) => {
          if (ws.readyState === WebSocket.OPEN) ws.send(chunk);
        });
        await mic.start();
        micRef.current = mic;
      } catch (err) {
        setErrorMessage(err instanceof Error ? err.message : "microphone permission denied");
        setState("error");
        ws.close();
      }
    };

    ws.onmessage = (event) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let msg: any;
      try {
        msg = JSON.parse(event.data);
      } catch {
        console.error("received malformed message from /ws/voice:", event.data);
        return;
      }
      try {
        switch (msg.type) {
          case "state":
            setState(msg.value);
            break;
          case "transcript.user.delta":
            partialTextRef.current.user = msg.text;
            break;
          case "transcript.user":
            appendTurn({ speaker: "user", text: msg.text });
            partialTextRef.current.user = "";
            break;
          case "transcript.agent.delta":
            partialTextRef.current.agent += msg.text;
            break;
          case "transcript.agent":
            appendTurn({ speaker: "agent", text: msg.text });
            partialTextRef.current.agent = "";
            break;
          case "audio":
            playerRef.current?.playBase64Pcm(msg.data);
            break;
          case "barge_in":
            playerRef.current?.stopAll();
            break;
          case "risk_tier":
            setRiskTier(msg.value);
            break;
          case "error":
            setErrorMessage(msg.message);
            setState("error");
            break;
          case "ended":
            setState("closed");
            break;
        }
      } catch (err) {
        console.error("error handling /ws/voice message:", msg.type, err);
      }
    };

    ws.onerror = () => {
      setErrorMessage("WebSocket connection failed");
      setState("error");
    };

    ws.onclose = () => {
      // Use the functional updater so we read the live state, not the
      // value closed over when startSession() was called.
      setState((s) => (s === "idle" || s === "error" ? s : "closed"));
    };
  }

  function stopSession() {
    micRef.current?.close();
    micRef.current = null;
    playerRef.current?.close();
    playerRef.current = null;
    wsRef.current?.close();
    wsRef.current = null;
    setState("idle");
    setRiskTier("observation");
  }

  const isLive = state !== "idle" && state !== "closed" && state !== "error";
  const isElevatedRisk = riskTier !== "observation" && riskTier !== "low_risk_inspection";

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Voice session</h2>
        <span className={`state-badge ${isLive ? "is-active" : ""} ${state === "error" ? "is-error" : ""}`}>
          {state}
        </span>
      </div>

      <div className="button-row">
        {isLive ? (
          <button onClick={stopSession}>Stop voice session</button>
        ) : (
          <button className="primary" onClick={startSession}>
            Start voice session
          </button>
        )}
      </div>

      {isLive && (
        <p style={{ margin: "0 0 0.75rem" }}>
          Risk: <span className={`state-badge ${isElevatedRisk ? "is-error" : ""}`}>{RISK_LABELS[riskTier] ?? riskTier}</span>
        </p>
      )}

      {errorMessage && <p className="error-text">Error: {errorMessage}</p>}

      <div className="transcript">
        {turns.length === 0 && <p className="transcript-empty">No conversation yet — start a session and speak.</p>}
        {turns.map((turn, i) => (
          <p key={i} className={`transcript-turn ${turn.speaker}`}>
            <span className="speaker">{turn.speaker === "user" ? "You" : "FieldSense"}</span>
            {turn.text}
          </p>
        ))}
      </div>
    </section>
  );
}
