import { X } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { createPortal } from "react-dom";

export default function Modal({
  open,
  onClose,
  heading,
  children,
}: {
  open: boolean;
  onClose: () => void;
  heading: string;
  children: React.ReactNode;
}) {
  return createPortal(
    <AnimatePresence>
      {open && (
        <motion.div
          key="modal"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className="fixed inset-0 z-100 flex items-center justify-center"
        >
          {/* 🔹 Backdrop */}
          <div className="absolute inset-0 bg-black/50" onClick={onClose} />

          {/* 🔸 Modal Content */}
          <div className="bg-background border-border relative z-110 max-h-7/8 w-[90%] max-w-150 overflow-x-hidden rounded-2xl border p-10">
            <X
              className="text-secondary-foreground/70 hover:text-secondary-foreground/40 absolute top-5 right-5 size-6 cursor-pointer"
              onClick={onClose}
            />
            <p className="text-foreground mb-10 text-xl font-bold">{heading}</p>
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
  );
}
