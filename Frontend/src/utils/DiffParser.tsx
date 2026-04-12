export function parseDiff(diff: string) {
  const lines = diff.split("\n");

  let lineNumber = 1;

  return lines
    .filter(
      (line) =>
        !line.startsWith("diff --git") &&
        !line.startsWith("index") &&
        !line.startsWith("---") &&
        !line.startsWith("+++") &&
        !line.startsWith("@@"),
    )
    .map((line) => {
      if (line.startsWith("+")) {
        return {
          type: "added",
          lineNumber: lineNumber++,
          content: line.slice(1),
        };
      }

      if (line.startsWith("-")) {
        return {
          type: "removed",
          lineNumber: lineNumber++,
          content: line.slice(1),
        };
      }

      return {
        type: "normal",
        lineNumber: lineNumber++,
        content: line,
      };
    });
}
