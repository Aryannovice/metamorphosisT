import { ShieldCheck, ShieldAlert, ShieldOff } from "lucide-react";

const LEVELS = {
  BLOCKED: {
    icon: ShieldOff,
    label: "Blocked",
    desc: "Input rejected by guardrails",
    color: "text-accent-red",
    bg: "bg-accent-red/10",
    ring: "ring-accent-red/30",
    bar: "bg-accent-red",
    pct: 0,
  },
  HIGH: {
    icon: ShieldCheck,
    label: "High Privacy",
    desc: "All processing local",
    color: "text-accent-green",
    bg: "bg-accent-green/10",
    ring: "ring-accent-green/30",
    bar: "bg-accent-green",
    pct: 100,
  },
  BALANCED: {
    icon: ShieldAlert,
    label: "Balanced",
    desc: "PII masked before cloud",
    color: "text-accent-blue",
    bg: "bg-accent-blue/10",
    ring: "ring-accent-blue/30",
    bar: "bg-accent-blue",
    pct: 60,
  },
  CLOUD_HEAVY: {
    icon: ShieldOff,
    label: "Cloud Heavy",
    desc: "Sent to cloud API",
    color: "text-accent-amber",
    bg: "bg-accent-amber/10",
    ring: "ring-accent-amber/30",
    bar: "bg-accent-amber",
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

      <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
          style={{ width: `${cfg.pct}%` }}
        />
      </div>
    </div>
  );
}
