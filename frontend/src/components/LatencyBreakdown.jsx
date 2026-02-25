import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Timer } from "lucide-react";

const STAGE_COLORS = {
  "Input Guard": "#f97316",
  PII: "#ef4444",
  Memory: "#a855f7",
  Compression: "#3b82f6",
  Inference: "#22c55e",
  "Output Guard": "#06b6d4",
};

export default function LatencyBreakdown({ latency }) {
  const data = [
    {
      name: "Input Guard",
      ms: latency.input_guardrails_ms || 0,
      fill: STAGE_COLORS["Input Guard"],
    },
    { name: "PII", ms: latency.pii_ms || 0, fill: STAGE_COLORS.PII },
    { name: "Memory", ms: latency.memory_ms || 0, fill: STAGE_COLORS.Memory },
    {
      name: "Compression",
      ms: latency.compression_ms || 0,
      fill: STAGE_COLORS.Compression,
    },
    {
      name: "Inference",
      ms: latency.inference_ms || 0,
      fill: STAGE_COLORS.Inference,
    },
    {
      name: "Output Guard",
      ms: latency.output_guardrails_ms || 0,
      fill: STAGE_COLORS["Output Guard"],
    },
  ];

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Latency Breakdown
        </h3>
        <div className="flex items-center gap-1.5 text-gray-400">
          <Timer size={13} />
          <span className="mono text-sm font-medium">
            {latency.total_ms.toFixed(0)}ms
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={110}>
        <BarChart data={data} layout="vertical" barSize={16}>
          <XAxis type="number" hide />
          <YAxis
            dataKey="name"
            type="category"
            tick={{ fill: "#6b7280", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={85}
          />
          <Tooltip
            formatter={(val) => [`${val.toFixed(1)} ms`]}
            contentStyle={{
              background: "#1a1d27",
              border: "1px solid #374151",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Bar dataKey="ms" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
