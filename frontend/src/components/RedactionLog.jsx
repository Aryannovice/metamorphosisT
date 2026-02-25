import { EyeOff } from "lucide-react";

const TYPE_COLORS = {
  EMAIL: "bg-red-50 text-red-600 border border-red-200",
  NAME: "bg-purple-50 text-purple-600 border border-purple-200",
  PHONE: "bg-amber-50 text-amber-600 border border-amber-200",
  SSN: "bg-rose-50 text-rose-600 border border-rose-200",
  CREDIT_CARD: "bg-orange-50 text-orange-600 border border-orange-200",
  ORG: "bg-blue-50 text-blue-600 border border-blue-200",
  LOCATION: "bg-cyan-50 text-cyan-600 border border-cyan-200",
  IP_ADDRESS: "bg-teal-50 text-teal-600 border border-teal-200",
};

export default function RedactionLog({ redaction }) {
  const entries = Object.entries(redaction.types || {});

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Redaction Log
        </h3>
        <span className="badge bg-purple-50 text-purple-600 border border-purple-200">
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
              className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-50"
            >
              <span
                className={`badge ${
                  TYPE_COLORS[type] || "bg-gray-100 text-gray-600 border border-gray-200"
                }`}
              >
                {type}
              </span>
              <span className="mono text-sm font-medium text-gray-700">
                {count}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
