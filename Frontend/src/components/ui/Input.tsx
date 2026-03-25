import { cloneElement, createElement, useState } from "react";
import type { ReactElement } from "react";
import { Eye, EyeOff } from "lucide-react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
  icon?: ReactElement;
  label?: string;
  type?: string;
  error?: string;
  info?: string;
}

function Input({
  className = "",
  icon,
  label,
  type = "text",
  error,
  info,
  ...props
}: InputProps) {
  const [visible, setVisible] = useState(false);

  const isPassword = type === "password";
  const inputType = isPassword ? (visible ? "text" : "password") : type;

  const leftIcon =
    icon &&
    cloneElement(icon, {
      className:
        "pointer-events-none text-muted-foreground absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2",
    } as any);

  const rightIcon =
    isPassword &&
    createElement(visible ? EyeOff : Eye, {
      className:
        "absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 cursor-pointer text-muted-foreground hover:text-foreground transition-colors",
      onClick: () => setVisible((v) => !v),
    });

  return (
    <div className="space-y-1">
      {label && (
        <label className="text-foreground text-sm font-bold">{label}</label>
      )}

      <div className="relative">
        {leftIcon}
        {rightIcon}

        <input
          type={inputType}
          className={`bg-background caret-primary ${error ? "border-destructive" : "border-input"} text-foreground placeholder:text-muted-foreground ring-offset-background focus-visible:ring-ring mt-3 flex h-12 w-full rounded-md border px-3 py-2 pl-10 ${icon ? "pl-12" : ""} ${isPassword ? "pr-10" : ""} focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm ${className} `}
          {...props}
        />
      </div>
      {info && (
        <p className="text-muted-foreground mt-2 ml-2 text-xs font-bold sm:text-sm">
          {info}
        </p>
      )}
      {error && (
        <p className="text-destructive mt-2 ml-2 text-xs font-bold sm:text-sm">
          {error}
        </p>
      )}
    </div>
  );
}

export default Input;
