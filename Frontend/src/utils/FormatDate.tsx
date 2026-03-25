export function formatDate(dateString: string): string {
  if (!dateString) return "";

  const date = new Date(dateString);

  return `${date.toLocaleString("en-US", {
    month: "short",
  })}, ${date.getDate().toString().padStart(2, "0")} ${date.getFullYear()}`;
}
