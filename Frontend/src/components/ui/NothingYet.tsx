import { motion } from "motion/react";
import type { ComponentType } from "react";

interface NothingYetProps {
  icon: ComponentType<{ className?: string }>;
  heading: string;
  description: string;
}

function NothingYet({ icon: Icon, heading, description }: NothingYetProps) {
  return (
    <motion.div
      className="py-12 text-center"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Icon className="text-muted-foreground mx-auto mb-3 h-12 w-12" />
      <h3 className="text-foreground mb-1 text-lg font-medium">{heading}</h3>
      <p className="text-muted-foreground mb-4 text-sm">{description}</p>
    </motion.div>
  );
}

export default NothingYet;
