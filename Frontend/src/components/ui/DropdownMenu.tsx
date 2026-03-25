import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";

function DropdownMenu({ open, onClose, children, triggerRef }) {
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target) &&
        triggerRef?.current &&
        !triggerRef.current.contains(e.target)
      ) {
        onClose();
      }
    }

    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open, onClose, triggerRef]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          ref={menuRef}
          initial={{ opacity: 0, y: -8, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -6, scale: 0.95 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
          className="border-border bg-card absolute top-12 right-0 z-50 w-56 rounded-xl border shadow-xl"
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default DropdownMenu;
