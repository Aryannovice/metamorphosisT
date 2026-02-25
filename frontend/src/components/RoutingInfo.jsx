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
          <div className="p-2.5 rounded-lg bg-accent-red/10 ring-1 ring-accent-red/30">
            <Ban size={22} className="text-accent-red" />
          </div>
          <div>
            <p className="text-lg font-bold text-accent-red">Blocked</p>
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
              ? "bg-accent-cyan/10 ring-accent-cyan/30"
              : "bg-accent-purple/10 ring-accent-purple/30"
          }`}
        >
          {isLocal ? (
            <Cpu size={22} className="text-accent-cyan" />
          ) : (
            <Cloud size={22} className="text-accent-purple" />
          )}
        </div>
        <div>
          <p
            className={`text-lg font-bold ${
              isLocal ? "text-accent-cyan" : "text-accent-purple"
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
