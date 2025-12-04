import { memo, useState, useEffect } from "react";
import { CardContent } from "@/components/ui/card";
import { FrostedCard } from "./ui/FrostedCard";

interface SystemTimeCardProps {
  currentTime: Date;
}

const formatTime = (date: Date) => date.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
const formatDate = (date: Date) => date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });

export const SystemTimeCard = memo(function SystemTimeCard({ currentTime }: SystemTimeCardProps) {
  // Use client-side state to prevent hydration mismatch
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  // Show placeholder during SSR, actual time after hydration
  const displayTime = mounted ? formatTime(currentTime) : "--:--:--";
  const displayDate = mounted ? formatDate(currentTime) : "--- --, ----";

  return (
    <FrostedCard className="overflow-hidden">
      <CardContent className="p-0">
        <div className="p-6 border-b border-slate-900/10 dark:border-slate-50/10">
          <div className="text-center">
            <div className="text-xs text-slate-500 dark:text-slate-500 mb-1 font-mono">SYSTEM TIME</div>
            <div className="text-3xl font-mono text-cyan-600 dark:text-cyan-400 mb-1" suppressHydrationWarning>{displayTime}</div>
            <div className="text-sm text-slate-500 dark:text-slate-400" suppressHydrationWarning>{displayDate}</div>
          </div>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white/20 dark:bg-black/20 rounded-xl p-3 border border-white/30 dark:border-white/10">
              <div className="text-xs text-slate-500 dark:text-slate-500 mb-1">Uptime</div>
              <div className="text-sm font-mono text-slate-700 dark:text-slate-200">14d 06:42:18</div>
            </div>
            <div className="bg-white/20 dark:bg-black/20 rounded-xl p-3 border border-white/30 dark:border-white/10">
              <div className="text-xs text-slate-500 dark:text-slate-500 mb-1">Time Zone</div>
              <div className="text-sm font-mono text-slate-700 dark:text-slate-200">UTC-08:00</div>
            </div>
          </div>
        </div>
      </CardContent>
    </FrostedCard>
  );
});
