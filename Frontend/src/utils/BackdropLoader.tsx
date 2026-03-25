export default function BackdropLoader() {
  return (
    <div className="fixed inset-0 z-200 flex items-center justify-center bg-black/40">
      <div className="border-primary h-12 w-12 animate-spin rounded-full border-4 border-t-transparent"></div>
    </div>
  );
}
