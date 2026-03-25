function DropdownItem({ icon: Icon, label, danger = false, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 px-4 py-3 text-sm transition-colors ${
        danger
          ? "text-destructive hover:bg-destructive/10"
          : "text-foreground hover:bg-accent"
      }`}
    >
      <Icon size={16} />
      {label}
    </button>
  );
}

export default DropdownItem;
