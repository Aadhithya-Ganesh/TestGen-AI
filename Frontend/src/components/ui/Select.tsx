import { ChevronDown } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { AnimatePresence, motion } from "motion/react";

interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options?: Array<{ value: string; label: string }>;
  placeholder?: string;
  label: string;
  disabled?: boolean;
  size?: "sm" | "md" | "lg";
}

function Select({
  value,
  label,
  onChange,
  options = [],
  placeholder = "Select",
  disabled = false,
  size = "md",
}: SelectProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const selected = options.find((o) => o.value === value);

  // close on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const sizeClasses = {
    sm: "text-sm px-3 py-2",
    md: "text-sm px-4 py-2.5",
    lg: "text-base px-4 py-3",
  };

  return (
    <div ref={ref} className="relative w-full">
      {label && (
        <label className="text-foreground mb-3 block text-sm font-bold">
          {label}
        </label>
      )}
      {/* Trigger */}
      <button
        disabled={disabled}
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={` ${sizeClasses[size]} border-border bg-background text-foreground flex w-full items-center justify-between gap-2 rounded-lg border py-3 font-bold transition ${disabled ? "cursor-not-allowed opacity-50" : "hover:bg-accent"} `}
      >
        <span className="ml-7">{selected ? selected.label : placeholder}</span>
        <ChevronDown
          size={16}
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      <AnimatePresence>
        {/* Dropdown */}
        {open && !disabled && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="border-border bg-background absolute z-50 mt-2 w-full overflow-hidden rounded-lg border shadow-lg"
          >
            {options.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  onChange(opt.value);
                  setOpen(false);
                }}
                className={`hover:bg-accent text-foreground w-full px-4 py-2 text-left text-sm font-bold ${opt.value === value ? "bg-accent font-medium" : ""} `}
              >
                {opt.label}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default Select;
