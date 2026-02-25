import { Server, Cloud, Cpu, Ban } from "lucide-react";

export default function RoutingInfo({ route, model }) {
  const isLocal = route === "LOCAL";
  const blocked = route === "BLOCKED";

  if (blocked) {
    return (
      <div className="card space-y-3">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Routing Decision
        </h3>
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-red-50 ring-1 ring-red-200">
            <Ban size={22} className="text-red-600" />
          </div>
          <div>
            <p className="text-lg font-bold text-red-600">Blocked</p>
            <p className="text-xs text-gray-500">Input rejected by guardrails</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card space-y-3">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        Routing Decision
      </h3>

      <div className="flex items-center gap-3">
        <div
          className={`p-2.5 rounded-lg ring-1 ${
            isLocal
              ? "bg-cyan-50 ring-cyan-200"
              : "bg-purple-50 ring-purple-200"
          }`}
        >
          {isLocal ? (
            <Cpu size={22} className="text-cyan-600" />
          ) : (
            <Cloud size={22} className="text-purple-600" />
          )}
        </div>
        <div>
          <p
            className={`text-lg font-bold ${
              isLocal ? "text-cyan-600" : "text-purple-600"
            }`}
          >
            {isLocal ? "Local Inference" : "Cloud Inference"}
          </p>
          <p className="text-xs text-gray-500 mono">{model}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Server size={12} />
        <span>
          {isLocal
            ? "Processed entirely on your machine via Ollama"
            : "Sent to cloud API with PII masking applied"}
        </span>
      </div>
    </div>
  );
}
