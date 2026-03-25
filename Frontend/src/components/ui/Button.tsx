import { motion } from "motion/react";
import type { ReactNode } from "react";
import type { HTMLMotionProps } from "motion/react";

interface ButtonProps extends HTMLMotionProps<"button"> {
  children: ReactNode;
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
}

function Button({
  children,
  className = "",
  disabled = false,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <motion.button
      type={type}
      disabled={disabled}
      className={`border-border flex cursor-pointer items-center justify-center gap-2 rounded-lg border px-5 py-2 text-xs font-semibold transition-all ease-in hover:opacity-90 sm:text-sm md:text-base ${className}`}
      whileHover={disabled ? undefined : { scale: 1.05 }}
      {...props}
    >
      {children}
    </motion.button>
  );
}

export default Button;
