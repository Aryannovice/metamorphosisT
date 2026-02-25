import { Fingerprint, CheckCircle, XCircle, Copy, ExternalLink } from "lucide-react";
import { useState } from "react";

function HashRow({ label, value, accent = "text-accent-cyan" }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (!value) return null;

  return (
    <div className="flex items-start justify-between gap-2 py-1.5 border-b border-gray-800/50 last:border-0">
      <div className="min-w-0 flex-1">
        <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-0.5">
          {label}
        </p>
        <p className={`text-xs mono break-all ${accent}`}>
          {value.slice(0, 16)}…{value.slice(-16)}
        </p>
      </div>
      <button
        onClick={handleCopy}
        className="shrink-0 p-1 rounded hover:bg-gray-700/50 transition-colors"
        title="Copy full hash"
      >
        {copied ? (
          <CheckCircle size={12} className="text-accent-green" />
        ) : (
          <Copy size={12} className="text-gray-500" />
        )}
      </button>
    </div>
  );
}

export default function DataHavenProof({ proof }) {
  const [expanded, setExpanded] = useState(false);

  if (!proof) {
    return (
      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            DataHaven Verification
          </h3>
          <span className="badge bg-gray-700/50 text-gray-400">
            Not connected
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <XCircle size={14} />
          <span>DataHaven service unavailable — no verification proof</span>
        </div>
      </div>
    );
  }

  const verified = proof.verified;

  return (
    <div className="card space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          DataHaven Verification
        </h3>
        {verified ? (
          <span className="badge bg-accent-green/10 text-accent-green">
            Verified
          </span>
        ) : (
          <span className="badge bg-accent-amber/10 text-accent-amber">
            Pending
          </span>
        )}
      </div>

      {/* Verification summary */}
      <div
        className={`flex items-center gap-3 p-3 rounded-lg border ${
          verified
            ? "bg-accent-green/5 border-accent-green/20"
            : "bg-accent-amber/5 border-accent-amber/20"
        }`}
      >
        <div
          className={`p-2 rounded-lg ${
            verified
              ? "bg-accent-green/10 ring-1 ring-accent-green/30"
              : "bg-accent-amber/10 ring-1 ring-accent-amber/30"
          }`}
        >
          <Fingerprint
            size={20}
            className={verified ? "text-accent-green" : "text-accent-amber"}
          />
        </div>
        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-semibold ${
              verified ? "text-accent-green" : "text-accent-amber"
            }`}
          >
            {verified ? "Cryptographically Verified" : "Unverified"}
          </p>
          <p className="text-[10px] text-gray-500 mono mt-0.5">
            {proof.chain || "datahaven-v1"} • {proof.algorithm || "SHA-256"}
          </p>
        </div>
      </div>

      {/* Log ID & Timestamp */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-0.5">
            Log ID
          </p>
          <p className="text-xs mono text-gray-300">
            {proof.log_id?.slice(0, 8)}…
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-0.5">
            Timestamp
          </p>
          <p className="text-xs mono text-gray-300">
            {proof.timestamp
              ? new Date(proof.timestamp).toLocaleTimeString()
              : "—"}
          </p>
        </div>
      </div>

      {/* Content hash (always visible) */}
      <div className="p-2.5 rounded-lg bg-surface">
        <HashRow
          label="Content Hash (SHA-256)"
          value={proof.content_hash}
          accent="text-accent-cyan"
        />
      </div>

      {/* Expand/collapse for full proof chain */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-[11px] text-accent-blue hover:text-accent-blue/80 transition-colors"
      >
        <ExternalLink size={12} />
        {expanded ? "Hide full proof chain" : "Show full proof chain"}
      </button>

      {expanded && (
        <div className="p-2.5 rounded-lg bg-surface space-y-0.5 animate-in">
          <HashRow
            label="Merkle Leaf"
            value={proof.merkle_leaf}
            accent="text-accent-purple"
          />
          <HashRow
            label="Merkle Root"
            value={proof.merkle_root}
            accent="text-accent-purple"
          />
          <HashRow
            label="HMAC Signature"
            value={proof.signature}
            accent="text-accent-amber"
          />
        </div>
      )}

      {/* Status */}
      <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1 border-t border-gray-800/50">
        <span>
          Status:{" "}
          <span className="text-accent-green font-medium uppercase">
            {proof.status || "stored"}
          </span>
        </span>
        <span className="mono">{proof.chain || "datahaven-v1"}</span>
      </div>
    </div>
  );
}
