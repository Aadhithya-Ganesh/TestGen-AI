import { Outlet, useLoaderData } from "react-router-dom";
import { motion } from "motion/react";
import Navbar from "../components/Navbar";

function NavbarLayout() {
  const user = useLoaderData();

  return (
    <div className="flex min-h-screen">
      <motion.div
        transition={{ type: "spring", stiffness: 260, damping: 30 }}
        className="bg-background flex flex-1 flex-col"
      >
        <Navbar user={user} />
        <div className="bg-background m-auto mb-20 w-full max-w-300 grow px-5 py-7 md:mb-0">
          <Outlet context={{ user }} />
        </div>
      </motion.div>
    </div>
  );
}

export default NavbarLayout;
