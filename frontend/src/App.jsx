import { useState } from "react";
import { Activity, Sparkles } from "lucide-react";
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
import WalletConnect from "./components/WalletConnect";
import DataHavenStoragePanel from "./components/DataHavenStoragePanel";
import { DataHavenProvider } from "./context/DataHavenContext";

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

// Simple hash function for generating proof hashes
async function hashText(text) {
  if (!text) return null;
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function AppContent() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [promptHash, setPromptHash] = useState(null);
  const [responseHash, setResponseHash] = useState(null);

  const handleSubmit = async (prompt, mode, cloudProvider) => {
    setLoading(true);
    setError("");
    try {
      const data = await sendPrompt(prompt, mode, cloudProvider);
      setResult(data);
      
      // Generate hashes for the proof
      const pHash = await hashText(prompt);
      const rHash = await hashText(data.response);
      setPromptHash(pHash);
      setResponseHash(rHash);
      
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
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
              <Activity size={22} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
                Metamorphosis
                <span className="text-xs font-normal px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                  Beta
                </span>
              </h1>
              <p className="text-xs text-gray-500">AI Optimization Gateway with DataHaven Verification</p>
            </div>
          </div>

          {result && (
            <div className="flex items-center gap-4 text-xs text-gray-500 bg-gray-100 px-3 py-2 rounded-lg">
              <span className="mono font-medium text-gray-700">ID: {result.request_id?.slice(0, 8)}…</span>
              <div className="w-px h-4 bg-gray-300" />
              <span className="mono font-medium text-gray-700">{r.latency.total_ms.toFixed(0)}ms</span>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 px-6 py-6">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left column — input + response */}
          <div className="lg:col-span-5 space-y-5">
            <PromptInput onSubmit={handleSubmit} isLoading={loading} />

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
                {error}
              </div>
            )}

            <ResponsePanel response={r.response} />

            {/* Request history */}
            {history.length > 0 && (
              <div className="card">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                  Recent Requests
                </h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {history.map((h, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between text-xs px-3 py-2 rounded-lg bg-gray-50 border border-gray-100"
                    >
                      <span className="text-gray-700 truncate max-w-[200px]">
                        {h.prompt}
                      </span>
                      <div className="flex items-center gap-3 text-gray-500 shrink-0">
                        <span className="badge bg-gray-200 text-gray-700">{h.mode}</span>
                        <span className="mono text-gray-600">{h.route}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right column — dashboard panels */}
          <div className="lg:col-span-7 space-y-5">
            {/* DataHaven Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <WalletConnect />
              <DataHavenStoragePanel 
                promptHash={promptHash}
                responseHash={responseHash}
                gatewayResponse={result}
              />
            </div>

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
      <footer className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-500" />
            <span>Metamorphosis Gateway — Privacy-first AI optimization with blockchain verification</span>
          </div>
          <span className="text-gray-400">Powered by DataHaven</span>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <DataHavenProvider>
      <AppContent />
    </DataHavenProvider>
  );
}
