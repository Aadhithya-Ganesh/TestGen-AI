import type { ReactElement } from "react";

type CardsProps = {
  heading: string;
  icon: ReactElement;
  description: string;
};

function Cards({ heading, icon, description }: CardsProps) {
  return (
    <div className="bg-card border-border flex flex-col gap-3 rounded-xl border py-5 pr-10 pl-5">
      <div className="bg-primary/20 w-fit rounded-xl p-3">{icon}</div>
      <p className="text-foreground font-bold">{heading}</p>
      <p className="text-muted-foreground text-sm">{description}</p>
    </div>
  );
}

export default Cards;
