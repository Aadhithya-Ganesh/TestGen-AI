import { motion } from "framer-motion";

export default function Switch({
  checked,
  onChange,
  size = "md", // sm | md | lg
  disabled = false,
  onColor = "bg-primary",
  offColor = "bg-background",
}) {
  const sizes = {
    sm: { track: "w-9 h-5", knob: "w-4 h-4" },
    md: { track: "w-12 h-6", knob: "w-5 h-5" },
    lg: { track: "w-16 h-8", knob: "w-7 h-7" },
  };

  const { track, knob } = sizes[size];

  const toggle = () => {
    if (!disabled) onChange(!checked);
  };

  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-disabled={disabled}
      tabIndex={disabled ? -1 : 0}
      onClick={toggle}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          toggle();
        }
      }}
      className={`border-border relative inline-flex items-center rounded-full border transition-colors ${track} ${checked ? onColor : offColor} ${checked ? "justify-end" : "justify-start"} ${disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"} focus-visible:ring-primary focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none`}
    >
      <motion.span
        layout
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
        className={`rounded-full bg-white shadow ${knob}`}
        style={{ margin: "2px" }}
      />
    </button>
  );
}
