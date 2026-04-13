import { CircleCheck } from "lucide-react";
import { motion } from "framer-motion";

interface CustomCheckboxProps {
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
}

function CustomCheckbox({ checked, onChange, label }: CustomCheckboxProps) {
  return (
    <label className="flex cursor-pointer items-center gap-2">
      {/* Hidden real checkbox */}
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="sr-only"
      />

      {/* Custom UI */}
      <motion.div
        initial={false}
        animate={{
          "--check-bg": checked ? "var(--color-primary)" : "transparent",
          "--check-border": checked
            ? "var(--color-primary)"
            : "var(--color-border)",
        }}
        style={{
          backgroundColor: "var(--check-bg)",
          borderColor: "var(--check-border)",
        }}
        className="flex h-6 w-6 items-center justify-center rounded-full border"
      >
        {checked && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 500, damping: 30 }}
          >
            <CircleCheck size={16} className="text-primary-foreground" />
          </motion.div>
        )}
      </motion.div>

      {/* Text */}
      <span
        className={`text-sm ${
          checked ? "text-primary" : "text-muted-foreground"
        }`}
      >
        {label}
      </span>
    </label>
  );
}

export default CustomCheckbox;
