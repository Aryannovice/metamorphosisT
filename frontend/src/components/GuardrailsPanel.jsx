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
          <span className="badge bg-accent-red/10 text-accent-red">
            Input blocked
          </span>
        ) : outputFiltered ? (
          <span className="badge bg-accent-amber/10 text-accent-amber">
            Output filtered
          </span>
        ) : (
          <span className="badge bg-accent-green/10 text-accent-green">
            Passed
          </span>
        )}
      </div>

      <div className="space-y-2">
        {blocked ? (
          <div className="flex items-start gap-2 p-2 rounded-lg bg-accent-red/5 border border-accent-red/20">
            <ShieldX size={16} className="text-accent-red shrink-0 mt-0.5" />
            <div className="text-xs text-gray-300">
              <p className="font-medium text-accent-red">Input blocked</p>
              <p className="mt-0.5 text-gray-400">
                {guardrails.input_reason || "Prompt rejected by safety filters."}
              </p>
            </div>
          </div>
        ) : outputFiltered ? (
          <div className="flex items-start gap-2 p-2 rounded-lg bg-accent-amber/5 border border-accent-amber/20">
            <ShieldAlert size={16} className="text-accent-amber shrink-0 mt-0.5" />
            <div className="text-xs text-gray-300">
              <p className="font-medium text-accent-amber">Output filtered</p>
              <p className="mt-0.5 text-gray-400">
                Model response was sanitized for safety.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <ShieldCheck size={16} className="text-accent-green" />
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
