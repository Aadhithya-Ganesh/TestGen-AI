import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { FlaskConical } from "lucide-react";

function Logo() {
  return (
    <Link to={`/`}>
      <div className="flex w-fit items-center gap-2">
        <motion.div
          className="bg-primary rounded-lg p-2"
          whileHover={{ rotate: -10 }}
        >
          <FlaskConical className="text-background h-5 w-5 md:h-6 md:w-6" />
        </motion.div>
        <p className="text-foreground text-xl font-bold">TestGen AI</p>
      </div>
    </Link>
  );
}

export default Logo;
