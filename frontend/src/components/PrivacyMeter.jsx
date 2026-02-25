import { ShieldCheck, ShieldAlert, ShieldOff } from "lucide-react";

const LEVELS = {
  BLOCKED: {
    icon: ShieldOff,
    label: "Blocked",
    desc: "Input rejected by guardrails",
    color: "text-red-600",
    bg: "bg-red-50",
    ring: "ring-red-200",
    bar: "bg-red-500",
    pct: 0,
  },
  HIGH: {
    icon: ShieldCheck,
    label: "High Privacy",
    desc: "All processing local",
    color: "text-emerald-600",
    bg: "bg-emerald-50",
    ring: "ring-emerald-200",
    bar: "bg-emerald-500",
    pct: 100,
  },
  BALANCED: {
    icon: ShieldAlert,
    label: "Balanced",
    desc: "PII masked before cloud",
    color: "text-blue-600",
    bg: "bg-blue-50",
    ring: "ring-blue-200",
    bar: "bg-blue-500",
    pct: 60,
  },
  CLOUD_HEAVY: {
    icon: ShieldOff,
    label: "Cloud Heavy",
    desc: "Sent to cloud API",
    color: "text-amber-600",
    bg: "bg-amber-50",
    ring: "ring-amber-200",
    bar: "bg-amber-500",
    pct: 25,
  },
};

export default function PrivacyMeter({ level }) {
  const cfg = LEVELS[level] || LEVELS.BALANCED;
  const Icon = cfg.icon;

  return (
    <div className="card space-y-3">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        Privacy Meter
      </h3>

      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-lg ${cfg.bg} ring-1 ${cfg.ring}`}>
          <Icon size={22} className={cfg.color} />
        </div>
        <div>
          <p className={`text-lg font-bold ${cfg.color}`}>{cfg.label}</p>
          <p className="text-xs text-gray-500">{cfg.desc}</p>
        </div>
      </div>

      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
          style={{ width: `${cfg.pct}%` }}
        />
      </div>
    </div>
  );
}
