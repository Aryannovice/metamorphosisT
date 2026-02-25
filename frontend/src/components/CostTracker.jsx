import { DollarSign, TrendingDown } from "lucide-react";

export default function CostTracker({ cost, route }) {
  const isFree = route === "LOCAL";

  return (
    <div className="card space-y-3">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        Estimated Cost
      </h3>

      <div className="flex items-center gap-3">
        <div
          className={`p-2.5 rounded-lg ring-1 ${
            isFree
              ? "bg-emerald-50 ring-emerald-200"
              : "bg-amber-50 ring-amber-200"
          }`}
        >
          {isFree ? (
            <TrendingDown size={22} className="text-emerald-600" />
          ) : (
            <DollarSign size={22} className="text-amber-600" />
          )}
        </div>
        <div>
          <p
            className={`text-2xl mono font-bold ${
              isFree ? "text-emerald-600" : "text-amber-600"
            }`}
          >
            {isFree ? "FREE" : `$${cost.toFixed(6)}`}
          </p>
          <p className="text-xs text-gray-500">
            {isFree ? "Local inference — zero cost" : "Cloud API usage"}
          </p>
        </div>
      </div>
    </div>
  );
}
