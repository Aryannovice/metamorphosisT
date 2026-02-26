import { Timer } from "lucide-react";

const STAGES = [
  { key: "input_guardrails_ms", label: "Input guardrails", color: "#f97316" },
  { key: "pii_ms", label: "PII masking", color: "#ef4444" },
  { key: "memory_ms", label: "Memory retrieval", color: "#a855f7" },
  { key: "compression_ms", label: "Compression", color: "#3b82f6" },
  { key: "inference_ms", label: "Inference", color: "#22c55e" },
  { key: "output_guardrails_ms", label: "Output guardrails", color: "#06b6d4" },
];

function clampMs(value) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) return 0;
  return n;
}

function formatMs(ms) {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
  return `${ms.toFixed(0)}ms`;
}

export default function LatencyBreakdown({ latency }) {
  const safeLatency = latency || {};
  const rows = STAGES.map((s) => ({
    label: s.label,
    color: s.color,
    ms: clampMs(safeLatency[s.key]),
  }));

  const stagesSum = rows.reduce((acc, r) => acc + r.ms, 0);
  const totalMs = clampMs(
    safeLatency.total_ms != null ? safeLatency.total_ms : stagesSum
  );
  const otherMs = Math.max(0, totalMs - stagesSum);
  const fullRows =
    otherMs > 0
      ? [
          ...rows,
          { label: "Other", color: "#94a3b8", ms: otherMs, isOther: true },
        ]
      : rows;

  return (
    <div className="card space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wider">
            Latency Breakdown
          </h3>
          <p className="mt-1 text-xs text-gray-500">
            Each stage shows time and share of total.
          </p>
        </div>
        <div className="flex items-center gap-2 text-gray-500">
          <Timer size={14} className="text-gray-400" />
          <span className="mono text-sm font-semibold tabular-nums text-gray-700">
            {formatMs(totalMs)}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {fullRows.map((r) => {
          const pct = totalMs > 0 ? (r.ms / totalMs) * 100 : 0;
          const barPct = r.ms > 0 ? Math.max(pct, 1.5) : 0; // keep tiny stages visible

          return (
            <div key={r.label} className="space-y-1.5">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="h-2.5 w-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: r.color }}
                    aria-hidden="true"
                  />
                  <span
                    className={`text-sm font-medium truncate ${
                      r.isOther ? "text-gray-600" : "text-gray-800"
                    }`}
                    title={r.label}
                  >
                    {r.label}
                  </span>
                </div>

                <div className="flex items-baseline gap-2 shrink-0">
                  <span className="mono text-sm font-semibold tabular-nums text-gray-800">
                    {formatMs(r.ms)}
                  </span>
                  <span className="mono text-xs tabular-nums text-gray-500">
                    {pct.toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden ring-1 ring-gray-200">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${barPct}%`,
                    backgroundColor: r.color,
                  }}
                  role="img"
                  aria-label={`${r.label}: ${formatMs(r.ms)} (${pct.toFixed(
                    0
                  )}% of total)`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
