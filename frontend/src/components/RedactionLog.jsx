import { EyeOff } from "lucide-react";

const TYPE_COLORS = {
  EMAIL: "bg-red-500/10 text-red-400",
  NAME: "bg-purple-500/10 text-purple-400",
  PHONE: "bg-amber-500/10 text-amber-400",
  SSN: "bg-rose-500/10 text-rose-400",
  CREDIT_CARD: "bg-orange-500/10 text-orange-400",
  ORG: "bg-blue-500/10 text-blue-400",
  LOCATION: "bg-cyan-500/10 text-cyan-400",
  IP_ADDRESS: "bg-teal-500/10 text-teal-400",
};

export default function RedactionLog({ redaction }) {
  const entries = Object.entries(redaction.types || {});

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Redaction Log
        </h3>
        <span className="badge bg-accent-purple/10 text-accent-purple">
          {redaction.count} masked
        </span>
      </div>

      {entries.length === 0 ? (
        <div className="flex items-center gap-2 text-gray-500 text-sm py-2">
          <EyeOff size={14} />
          <span>No PII detected</span>
        </div>
      ) : (
        <div className="space-y-2">
          {entries.map(([type, count]) => (
            <div
              key={type}
              className="flex items-center justify-between px-3 py-2 rounded-lg bg-surface"
            >
              <span
                className={`badge ${
                  TYPE_COLORS[type] || "bg-gray-500/10 text-gray-400"
                }`}
              >
                {type}
              </span>
              <span className="mono text-sm font-medium text-gray-300">
                {count}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
