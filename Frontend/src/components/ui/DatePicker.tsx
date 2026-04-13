import { Calendar, ChevronLeft, ChevronRight } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { AnimatePresence, motion } from "motion/react";

interface DatePickerProps {
  value?: string;
  onChange: (date: string) => void;
  placeholder?: string;
  disabled?: boolean;
  size?: "sm" | "md" | "lg";
}

function DatePicker({
  value,
  onChange,
  placeholder = "Select date",
  disabled = false,
  size = "md",
}: DatePickerProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const today = new Date();
  const [month, setMonth] = useState(today.getMonth());
  const [year] = useState(today.getFullYear());

  const sizeClasses = {
    sm: "text-sm px-3 py-2",
    md: "text-sm px-4 py-2.5",
    lg: "text-base px-4 py-3",
  };

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

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const days = [];
  for (let i = 0; i < firstDay; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);

  const handleSelect = (day: number | undefined) => {
    const selected = new Date(year, month, day);
    onChange(selected.toISOString().split("T")[0]);
    setOpen(false);
  };

  const formatted =
    value &&
    new Date(value).toLocaleDateString(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
    });

  return (
    <div ref={ref} className="relative w-full">
      {/* Trigger */}
      <button
        disabled={disabled}
        onClick={() => setOpen((o) => !o)}
        className={`${sizeClasses[size]} border-border bg-background text-foreground flex w-full items-center justify-between gap-2 rounded-lg border py-3 font-bold transition ${
          disabled ? "cursor-not-allowed opacity-50" : "hover:bg-accent"
        }`}
      >
        <div className="ml-2 flex items-center gap-2">
          <Calendar size={16} />
          <span>{formatted || placeholder}</span>
        </div>
      </button>

      <AnimatePresence>
        {open && !disabled && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="border-border bg-background absolute -top-100 z-300 mt-2 w-full rounded-lg border p-4 shadow-lg"
          >
            {/* Month Controls */}
            <div className="text-foreground mb-10 flex items-center justify-between">
              <button
                onClick={() => setMonth((m) => (m === 0 ? 11 : m - 1))}
                className="hover:bg-accent rounded p-1"
              >
                <ChevronLeft size={16} />
              </button>

              <span className="text-sm font-bold">
                {new Date(year, month).toLocaleString("default", {
                  month: "long",
                })}{" "}
                {year}
              </span>

              <button
                onClick={() => setMonth((m) => (m === 11 ? 0 : m + 1))}
                className="hover:bg-accent rounded p-1"
              >
                <ChevronRight size={16} />
              </button>
            </div>

            {/* Weekdays */}
            <div className="text-muted-foreground mb-5 grid grid-cols-7 gap-6 text-center text-xs font-bold">
              {["S", "M", "T", "W", "T", "F", "S"].map((d, index) => (
                <span key={index}>{d}</span>
              ))}
            </div>

            {/* Days */}
            <AnimatePresence mode="wait">
              <motion.div
                key={`${month}-${year}`}
                className="grid grid-cols-7 gap-2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                {days.map((day, i) => {
                  if (!day) {
                    return <div key={i} />;
                  }

                  const dateObj = new Date(year, month, day);
                  const iso = dateObj.toISOString().split("T")[0];

                  const isSelected = value === iso;

                  const isToday =
                    day === today.getDate() &&
                    month === today.getMonth() &&
                    year === today.getFullYear();

                  return (
                    <button
                      key={i}
                      onClick={() => handleSelect(day)}
                      className={`text-foreground hover:bg-accent rounded-md p-3 text-sm font-bold transition ${
                        isSelected ? "bg-accent text-foreground" : ""
                      } ${isToday && !isSelected ? "border-border border" : ""}`}
                    >
                      {day}
                    </button>
                  );
                })}
              </motion.div>
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default DatePicker;
