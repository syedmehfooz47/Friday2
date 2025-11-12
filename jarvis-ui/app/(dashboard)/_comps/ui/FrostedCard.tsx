import { memo } from "react";
import { Card } from "@/components/ui/card";

export const FrostedCard = memo(function FrostedCard({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <Card
      className={`
        bg-white/40 dark:bg-slate-900/40
        backdrop-blur-2xl
        border border-white/50 dark:border-white/10
        rounded-3xl
        shadow-lg dark:shadow-black/20
        ${className}
      `}
      {...props}
    />
  );
});
