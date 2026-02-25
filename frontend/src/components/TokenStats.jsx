import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Coins } from "lucide-react";

export default function TokenStats({ stats }) {
  const data = [
    { name: "Original", value: stats.original, fill: "#6366f1" },
    { name: "Compressed", value: stats.compressed, fill: "#3b82f6" },
    { name: "Saved", value: stats.saved, fill: "#22c55e" },
  ];

  const pct = stats.compression_ratio
    ? (stats.compression_ratio * 100).toFixed(1)
    : "0";

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Token Stats
        </h3>
        <span className="badge bg-accent-green/10 text-accent-green">
          {pct}% saved
        </span>
      </div>

      <ResponsiveContainer width="100%" height={120}>
        <BarChart data={data} barSize={32}>
          <XAxis
            dataKey="name"
            tick={{ fill: "#6b7280", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis hide />
          <Tooltip
            contentStyle={{
              background: "#1a1d27",
              border: "1px solid #374151",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-2 text-center">
        {data.map((d) => (
          <div key={d.name}>
            <p className="mono text-lg font-bold" style={{ color: d.fill }}>
              {d.value}
            </p>
            <p className="text-[10px] text-gray-500 uppercase">{d.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
