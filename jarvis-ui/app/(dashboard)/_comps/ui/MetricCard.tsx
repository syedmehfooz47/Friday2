// jarvis-ui/app/(dashboard)/_comps/ui/MetricCard.tsx

import { memo } from "react";
import { BarChart3, LineChart, type LucideIcon } from "lucide-react";

// Define a specific type for the allowed color values
type MetricColor = 'cyan' | 'green' | 'blue' | 'purple';

export const MetricCard = memo(function MetricCard({ title, value, icon: Icon, trend, color, detail }: { title: string; value: number; icon: LucideIcon; trend: "up" | "down" | "stable"; color: MetricColor; detail: string }) {
    const colorClasses: Record<MetricColor, string> = {
        cyan: "border-cyan-500/30 text-cyan-600 dark:text-cyan-500",
        green: "border-green-500/30 text-green-600 dark:text-green-500",
        blue: "border-blue-500/30 text-blue-600 dark:text-blue-500",
        purple: "border-purple-500/30 text-purple-600 dark:text-purple-500",
    };
    const gradientClasses: Record<MetricColor, string> = {
        cyan: "from-cyan-500 to-blue-500",
        green: "from-green-500 to-emerald-500",
        blue: "from-blue-500 to-indigo-500",
        purple: "from-purple-500 to-pink-500",
    }
    const trendIcons = {
        up: <BarChart3 className="h-4 w-4 text-amber-500" />,
        down: <BarChart3 className="h-4 w-4 rotate-180 text-green-500" />,
        stable: <LineChart className="h-4 w-4 text-blue-500" />,
    }

 return (
    <div className={`bg-white/20 dark:bg-black/10 rounded-2xl border ${colorClasses[color]} p-4 relative overflow-hidden`}>
        <div className="flex items-center justify-between mb-2"><div className="text-sm text-slate-500 dark:text-slate-400">{title}</div><Icon className={`h-5 w-5 ${colorClasses[color]}`} /></div>
        <div className="text-2xl font-bold mb-1 bg-gradient-to-r bg-clip-text text-transparent from-slate-800 to-slate-500 dark:from-slate-100 dark:to-slate-300">{value}%</div>
        <div className="text-xs text-slate-400 dark:text-slate-500">{detail}</div>
        <div className="absolute bottom-2 right-2 flex items-center">{trendIcons[trend]}</div>
        <div className={`absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-gradient-to-r opacity-20 blur-xl ${gradientClasses[color]}`}></div>
    </div>
 )
});