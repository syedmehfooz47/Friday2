// jarvis-ui/app/(dashboard)/_comps/PriorityAlertsCard.tsx

"use client";

import { memo, useState, useEffect } from "react";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Info, CheckCircle2, Download, AlertTriangle, Terminal, Wrench } from "lucide-react";
import { FrostedCard } from "./ui/FrostedCard";
import { ScrollArea } from "@/components/ui/scroll-area";

interface AlertItemType {
    id: string;
    type: "info" | "warning" | "error" | "success" | "update" | "log" | "tool";
    title: string;
    time: string;
    description: string;
    rawTimestamp: string;
}

const alertStyles: Record<AlertItemType['type'] | 'default', { icon: React.ElementType, color: string }> = {
    info: { icon: Info, color: "text-blue-500 dark:text-blue-400 bg-blue-500/10 border-blue-500/30" },
    warning: { icon: AlertTriangle, color: "text-amber-500 dark:text-amber-400 bg-amber-500/10 border-amber-500/30" },
    error: { icon: AlertCircle, color: "text-red-500 dark:text-red-400 bg-red-500/10 border-red-500/30" },
    success: { icon: CheckCircle2, color: "text-green-500 dark:text-green-400 bg-green-500/10 border-green-500/30" },
    update: { icon: Download, color: "text-cyan-500 dark:text-cyan-400 bg-cyan-500/10 border-cyan-500/30" },
    log: { icon: Terminal, color: "text-gray-500 dark:text-gray-400 bg-gray-500/10 border-gray-500/30 dark:bg-gray-400/10 dark:border-gray-400/30"},
    tool: { icon: Wrench, color: "text-purple-500 dark:text-purple-400 bg-purple-500/10 border-purple-500/30"},
    default: { icon: AlertCircle, color: "text-gray-500 bg-gray-500/10 border-gray-500/30" }
};

const AlertItem = memo(function AlertItem({ alert }: { alert: AlertItemType }) {
    const style = alertStyles[alert.type] || alertStyles.default;
    const Icon = style.icon;
    const colorClasses = style.color;

    return (
        <div className="flex items-start space-x-3 p-2 rounded-lg hover:bg-white/20 dark:hover:bg-black/10 transition-colors duration-150">
            <div className={`mt-1 p-1 rounded-full ${colorClasses.split(" ")[1]} ${colorClasses.split(" ")[2]}`}>
                <Icon className={`h-3.5 w-3.5 ${colorClasses.split(" ")[0]}`} />
            </div>
            <div className="flex-1 overflow-hidden">
                <div className="flex items-center justify-between">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate pr-2" title={alert.title}>{alert.title}</div>
                    <div className="text-xs text-slate-400 dark:text-slate-500 flex-shrink-0">{alert.time}</div>
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5" title={alert.description}>{alert.description}</div>
            </div>
        </div>
    )
});

export const PriorityAlertsCard = memo(function PriorityAlertsCard() {
    const [alerts, setAlerts] = useState<AlertItemType[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const mockRawAlerts = [
            { id: "tool_1", type: "tool" as const, title: "Tool: generate_pdf", description: "Generating 'Market Analysis Report'...", timestamp: new Date(Date.now() - 1 * 60000).toISOString() },
            { id: "warn_1", type: "warning" as const, title: "High CPU Load", description: "Cognitive load reached 85%.", timestamp: new Date(Date.now() - 3 * 60000).toISOString() },
            { id: "log_1", type: "log" as const, title: "Backend Log", description: "Weather module initialized.", timestamp: new Date(Date.now() - 5 * 60000).toISOString() },
            { id: "tool_2", type: "success" as const, title: "Tool: email_send", description: "Email sent successfully to boss@example.com", timestamp: new Date(Date.now() - 10 * 60000).toISOString() },
            { id: "error_1", type: "error" as const, title: "Telegram Error", description: "Failed to send message: Timeout", timestamp: new Date(Date.now() - 15 * 60000).toISOString() },
            { id: "update_1", type: "update" as const, title: "Contact Added", description: "New contact 'Alice' saved.", timestamp: new Date(Date.now() - 20 * 60000).toISOString() },
            { id: "tool_3", type: "tool" as const, title: "Tool: open_file", description: "Opening 'Report_Q3.pdf'...", timestamp: new Date(Date.now() - 25 * 60000).toISOString() },
            { id: "log_2", type: "log" as const, title: "System", description: "WebSocket connection established.", timestamp: new Date(Date.now() - 30 * 60000).toISOString() },
        ];

        const formattedAlerts: AlertItemType[] = mockRawAlerts.map(a => ({
            id: a.id,
            type: a.type,
            title: a.title,
            description: a.description,
            time: new Date(a.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            rawTimestamp: a.timestamp,
        })).sort((a, b) => new Date(b.rawTimestamp).getTime() - new Date(a.rawTimestamp).getTime());

        setAlerts(formattedAlerts);
        setIsLoading(false);
    }, []);

    return (
        <FrostedCard className="flex flex-col h-full min-h-[200px]">
            <CardHeader className="pb-2 flex-shrink-0 border-b border-slate-200 dark:border-white/10">
                <CardTitle className="text-slate-800 dark:text-slate-100 flex items-center text-base font-semibold">
                    <AlertTriangle className="mr-2 h-5 w-5 text-amber-500" />
                    Priority Alerts & Logs
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-grow overflow-hidden p-2">
                {isLoading ? (
                    <div className="flex justify-center items-center h-full text-slate-500 dark:text-slate-400 animate-pulse">Loading alerts...</div>
                ) : alerts.length === 0 ? (
                    <div className="flex justify-center items-center h-full text-slate-500 dark:text-slate-400 text-sm">No recent alerts or logs.</div>
                ) : (
                    <ScrollArea className="h-full pr-2">
                        <div className="space-y-1">
                            {alerts.map((alert) => (
                                <AlertItem key={alert.id} alert={alert} />
                            ))}
                        </div>
                    </ScrollArea>
                )}
            </CardContent>
        </FrostedCard>
    );
});