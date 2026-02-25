import { useState } from "react";
import { Send, Shield, Scale, Zap, Cloud } from "lucide-react";

const MODES = [
  {
    value: "STRICT",
    label: "Strict",
    desc: "Local-only, max privacy",
    icon: Shield,
    color: "text-emerald-600",
    bg: "bg-emerald-50 border-emerald-200",
  },
  {
    value: "BALANCED",
    label: "Balanced",
    desc: "Smart routing, PII masked",
    icon: Scale,
    color: "text-blue-600",
    bg: "bg-blue-50 border-blue-200",
  },
  {
    value: "PERFORMANCE",
    label: "Performance",
    desc: "Cloud-first, fastest",
    icon: Zap,
    color: "text-amber-600",
    bg: "bg-amber-50 border-amber-200",
  },
];

const CLOUD_PROVIDERS = [
  { value: "GROQ", label: "Groq", desc: "Free, ultra-fast" },
  { value: "OPENAI", label: "OpenAI", desc: "GPT models" },
];

export default function PromptInput({ onSubmit, isLoading }) {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState("BALANCED");
  const [cloudProvider, setCloudProvider] = useState("GROQ");

  const showCloudPicker = mode !== "STRICT";

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit(prompt.trim(), mode, cloudProvider);
  };

  return (
    <div className="card space-y-4">
      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
        Routing Mode
      </h2>

      <div className="grid grid-cols-3 gap-3">
        {MODES.map((m) => {
          const Icon = m.icon;
          const selected = mode === m.value;
          return (
            <button
              key={m.value}
              onClick={() => setMode(m.value)}
              className={`flex flex-col items-center gap-1.5 p-3 rounded-lg border text-center transition-all cursor-pointer ${
                selected
                  ? `${m.bg} border`
                  : "border-gray-200 hover:border-gray-300 bg-white"
              }`}
            >
              <Icon size={18} className={selected ? m.color : "text-gray-400"} />
              <span
                className={`text-sm font-medium ${
                  selected ? m.color : "text-gray-600"
                }`}
              >
                {m.label}
              </span>
              <span className="text-[11px] text-gray-500">{m.desc}</span>
            </button>
          );
        })}
      </div>

      {showCloudPicker && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <Cloud size={12} />
            <span className="font-semibold uppercase tracking-wider">
              Cloud Provider
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {CLOUD_PROVIDERS.map((p) => {
              const selected = cloudProvider === p.value;
              return (
                <button
                  key={p.value}
                  onClick={() => setCloudProvider(p.value)}
                  className={`px-3 py-2 rounded-lg border text-center transition-all cursor-pointer ${
                    selected
                      ? "bg-purple-50 border-purple-200 text-purple-700"
                      : "border-gray-200 hover:border-gray-300 text-gray-600 bg-white"
                  }`}
                >
                  <span className="text-sm font-medium">{p.label}</span>
                  <span className="text-[11px] text-gray-500 ml-1.5">
                    — {p.desc}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="relative">
        <textarea
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt…"
          className="w-full bg-gray-50 rounded-lg border border-gray-200 px-4 py-3 pr-14 text-sm text-gray-800 placeholder-gray-400 resize-none focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all"
        />
        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="absolute right-3 bottom-3 p-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Send size={16} />
          )}
        </button>
      </form>
    </div>
  );
}
