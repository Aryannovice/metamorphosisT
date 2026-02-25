import { useState } from "react";
import { Activity } from "lucide-react";
import { sendPrompt } from "./api";
import PromptInput from "./components/PromptInput";
import ResponsePanel from "./components/ResponsePanel";
import PrivacyMeter from "./components/PrivacyMeter";
import TokenStats from "./components/TokenStats";
import CostTracker from "./components/CostTracker";
import RedactionLog from "./components/RedactionLog";
import RoutingInfo from "./components/RoutingInfo";
import LatencyBreakdown from "./components/LatencyBreakdown";
import GuardrailsPanel from "./components/GuardrailsPanel";

const EMPTY_RESULT = {
  response: "",
  privacy_level: "BALANCED",
  token_stats: { original: 0, compressed: 0, saved: 0, compression_ratio: 0 },
  estimated_cost: 0,
  redaction: { count: 0, types: {} },
  route: "LOCAL",
  model_used: "",
  latency: {
    input_guardrails_ms: 0,
    pii_ms: 0,
    memory_ms: 0,
    compression_ms: 0,
    inference_ms: 0,
    output_guardrails_ms: 0,
    total_ms: 0,
  },
  guardrails: { input_blocked: false, output_filtered: false },
};

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const handleSubmit = async (prompt, mode, cloudProvider) => {
    setLoading(true);
    setError("");
    try {
      const data = await sendPrompt(prompt, mode, cloudProvider);
      setResult(data);
      setHistory((prev) => [
        { prompt, mode, timestamp: new Date(), ...data },
        ...prev.slice(0, 19),
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const r = result || EMPTY_RESULT;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent-blue/10 ring-1 ring-accent-blue/30">
              <Activity size={20} className="text-accent-blue" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">Metamorphosis</h1>
              <p className="text-xs text-gray-500">AI Optimization Gateway</p>
            </div>
          </div>

          {result && (
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span className="mono">ID: {result.request_id?.slice(0, 8)}…</span>
              <span className="mono">{r.latency.total_ms.toFixed(0)}ms</span>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 px-6 py-6">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left column — input + response */}
          <div className="lg:col-span-5 space-y-5">
            <PromptInput onSubmit={handleSubmit} isLoading={loading} />

            {error && (
              <div className="card border-accent-red/30 bg-accent-red/5 text-accent-red text-sm">
                {error}
              </div>
            )}

            <ResponsePanel response={r.response} />

            {/* Request history */}
            {history.length > 0 && (
              <div className="card space-y-3">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Recent Requests
                </h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {history.map((h, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between text-xs px-3 py-2 rounded-lg bg-surface"
                    >
                      <span className="text-gray-300 truncate max-w-[200px]">
                        {h.prompt}
                      </span>
                      <div className="flex items-center gap-3 text-gray-500 shrink-0">
                        <span className="badge bg-gray-700/50">{h.mode}</span>
                        <span className="mono">{h.route}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right column — dashboard panels */}
          <div className="lg:col-span-7 space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <PrivacyMeter level={r.privacy_level} />
              <RoutingInfo route={r.route} model={r.model_used} />
            </div>

            <GuardrailsPanel guardrails={r.guardrails} route={r.route} />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <TokenStats stats={r.token_stats} />
              <div className="space-y-5">
                <CostTracker cost={r.estimated_cost} route={r.route} />
                <RedactionLog redaction={r.redaction} />
              </div>
            </div>

            <LatencyBreakdown latency={r.latency} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 px-6 py-3 text-center text-xs text-gray-600">
        Metamorphosis Gateway — Privacy-first AI optimization
      </footer>
    </div>
  );
}
