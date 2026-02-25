import { ShieldCheck, ShieldAlert, ShieldX, Lock } from "lucide-react";

export default function GuardrailsPanel({ guardrails, route }) {
  const blocked = route === "BLOCKED";
  const outputFiltered = guardrails?.output_filtered;
  const inputBlocked = guardrails?.input_blocked;

  if (!guardrails) return null;

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Guardrails
        </h3>
        {blocked ? (
          <span className="badge bg-red-50 text-red-600 border border-red-200">
            Input blocked
          </span>
        ) : outputFiltered ? (
          <span className="badge bg-amber-50 text-amber-600 border border-amber-200">
            Output filtered
          </span>
        ) : (
          <span className="badge bg-emerald-50 text-emerald-600 border border-emerald-200">
            Passed
          </span>
        )}
      </div>

      <div className="space-y-2">
        {blocked ? (
          <div className="flex items-start gap-2 p-2 rounded-lg bg-red-50 border border-red-200">
            <ShieldX size={16} className="text-red-600 shrink-0 mt-0.5" />
            <div className="text-xs text-gray-700">
              <p className="font-medium text-red-600">Input blocked</p>
              <p className="mt-0.5 text-gray-500">
                {guardrails.input_reason || "Prompt rejected by safety filters."}
              </p>
            </div>
          </div>
        ) : outputFiltered ? (
          <div className="flex items-start gap-2 p-2 rounded-lg bg-amber-50 border border-amber-200">
            <ShieldAlert size={16} className="text-amber-600 shrink-0 mt-0.5" />
            <div className="text-xs text-gray-700">
              <p className="font-medium text-amber-600">Output filtered</p>
              <p className="mt-0.5 text-gray-500">
                Model response was sanitized for safety.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <ShieldCheck size={16} className="text-emerald-600" />
            <span>
              Input and output passed safety checks (injection, toxicity,
              harmful content).
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 text-[11px] text-gray-500">
        <Lock size={10} />
        <span>Input: injection + toxicity • Output: harmful content filter</span>
      </div>
    </div>
  );
}
