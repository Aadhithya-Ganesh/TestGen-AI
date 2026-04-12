import { useState } from "react";
import { parseDiff } from "../utils/DiffParser";

export default function DiffViewer({ tests }: { tests: any[] }) {
  const [activeFile, setActiveFile] = useState(0);

  if (!tests || tests.length === 0) return null;

  const file = tests[activeFile];
  const parsedLines = parseDiff(file.diff);

  const added = parsedLines.filter((l) => l.type === "added").length;
  const removed = parsedLines.filter((l) => l.type === "removed").length;

  return (
    <div className="bg-card border-border mt-10 rounded-2xl border">
      {/* Tabs */}
      <div className="border-border flex overflow-x-auto border-b">
        {tests.map((f, i) => (
          <button
            key={i}
            onClick={() => setActiveFile(i)}
            className={`px-4 py-2 text-sm whitespace-nowrap ${
              i === activeFile
                ? "border-primary border-b-2 font-semibold"
                : "text-muted-foreground"
            }`}
          >
            {f.filename.split("/").pop()}
          </button>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 text-sm">
        <p>
          Modified file <span className="text-green-500">+{added}</span>{" "}
          <span className="text-red-500">-{removed}</span>
        </p>
      </div>

      {/* Diff */}
      <div className="max-h-[500px] overflow-auto font-mono text-sm">
        {parsedLines.map((line, i) => (
          <div
            key={i}
            className={`flex px-4 py-0.5 ${
              line.type === "added"
                ? "bg-green-500/10 text-green-400"
                : line.type === "removed"
                  ? "bg-red-500/10 text-red-400"
                  : "text-muted-foreground"
            }`}
          >
            <span className="w-10 opacity-50 select-none">
              {line.lineNumber}
            </span>

            <span>
              {line.type === "added" && "+"}
              {line.type === "removed" && "-"}
              {line.content}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
