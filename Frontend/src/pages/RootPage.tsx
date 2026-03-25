import { motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";
import ScrollToTop from "../utils/ScrollToTop";

function RootPage() {
  const location = useLocation();

  return (
    <div className="bg-background">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
      >
        <ScrollToTop />
        <Outlet />
      </motion.div>
    </div>
  );
}

export default RootPage;
