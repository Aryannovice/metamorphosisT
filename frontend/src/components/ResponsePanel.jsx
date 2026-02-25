import { MessageSquare } from "lucide-react";

export default function ResponsePanel({ response }) {
  if (!response) return null;

  return (
    <div className="card space-y-3">
      <div className="flex items-center gap-2">
        <MessageSquare size={14} className="text-blue-600" />
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          AI Response
        </h3>
      </div>

      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap max-h-64 overflow-y-auto">
        {response}
      </div>
    </div>
  );
}
