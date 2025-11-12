// File: jarvis-ui/app/(dashboard)/_comps/SystemOverviewCard.tsx

"use client";
import { memo } from "react";
import { useJarvisStore } from "@/app/store/jarvisStore";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Activity, Cpu, HardDrive, Wifi } from "lucide-react";
import { FrostedCard } from "./ui/FrostedCard";
import { MetricCard } from "./ui/MetricCard";
import { PerformanceChart } from "./ui/PerformanceChart";

const ProcessRowDetailedCompact = memo(function ProcessRowDetailedCompact({ pid, name, cpu, memory }: { pid: string; name: string; cpu: number; memory: number }) {
    return (
        <div className="py-2 px-3 text-xs hover:bg-white/20 dark:hover:bg-black/20 rounded-lg">
            <div className="flex justify-between items-center mb-1">
                <span className="text-slate-700 dark:text-slate-300 font-medium truncate pr-2">{name}</span>
                <span className="text-slate-500 dark:text-slate-500 flex-shrink-0">ID: {pid}</span>
            </div>
            <div className="flex justify-between items-center text-slate-500 dark:text-slate-400">
                <span>Cognition: <span className="text-cyan-600 dark:text-cyan-400">{cpu}%</span></span>
                <span>Memory: <span className="text-purple-600 dark:text-purple-400">{memory} MB</span></span>
            </div>
        </div>
    );
});

const StorageItemCompact = memo(function StorageItem({ name, total, used, type }: { name: string; total: number; used: number; type: string; }) {
    const percentage = Math.round((used / total) * 100);
    return (
        <div className="bg-white/20 dark:bg-black/10 rounded-xl p-3 border border-white/30 dark:border-white/10">
            <div className="flex items-center justify-between mb-2"><div className="text-sm text-slate-700 dark:text-slate-300">{name}</div><Badge variant="outline" className="bg-white/40 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 border-slate-400/50 dark:border-slate-600/50 text-xs">{type}</Badge></div>
            <div className="mb-2">
                <div className="flex items-center justify-between mb-1"><div className="text-xs text-slate-400 dark:text-slate-500">{used} GB / {total} GB</div><div className="text-xs text-slate-500 dark:text-slate-400">{percentage}%</div></div>
                <Progress value={percentage} className="h-1.5 bg-slate-900/10 dark:bg-slate-50/10"><div className={`h-full rounded-full ${percentage > 90 ? "bg-red-500" : percentage > 70 ? "bg-amber-500" : "bg-cyan-500"}`} style={{ width: `${percentage}%` }} /></Progress>
            </div>
            <div className="flex items-center justify-between text-xs"><div className="text-slate-400 dark:text-slate-500">Free: {total - used} GB</div><Button variant="ghost" size="sm" className="h-6 text-xs px-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100">Details</Button></div>
        </div>
    )
});

export const SystemOverviewCard = memo(function SystemOverviewCard() {
    const { systemMetrics } = useJarvisStore();

    return (
        <FrostedCard className="overflow-hidden">
            <CardHeader className="border-b border-slate-900/10 dark:border-slate-50/10 pb-3">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-slate-800 dark:text-slate-100 flex items-center text-base">
                        <Activity className="mr-2 h-5 w-5 text-cyan-500" />System Overview
                    </CardTitle>
                    <Badge variant="outline" className="bg-transparent text-cyan-500 dark:text-cyan-400 border-cyan-500/30 dark:border-cyan-500/50 text-xs">
                        <div className="h-1.5 w-1.5 rounded-full bg-cyan-500 mr-1 animate-pulse"></div>
                        LIVE
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
                <div className="grid grid-cols-1 gap-4">
                    <MetricCard title="Cognitive Load" value={systemMetrics.cpuUsage} icon={Cpu} trend="up" color="cyan" detail="Active Analysis" />
                    <MetricCard title="Active Memory" value={systemMetrics.memoryUsage} icon={HardDrive} trend="stable" color="purple" detail="System RAM Usage" />
                    <MetricCard title="Data Stream" value={systemMetrics.networkStatus} icon={Wifi} trend="down" color="blue" detail="Relative I/O" />
                </div>
                <div className="pt-4 border-t border-slate-900/10 dark:border-slate-50/10">
                    <Tabs defaultValue="activity" className="w-full">
                        <TabsList className="grid w-full grid-cols-3 bg-white/40 dark:bg-slate-900/40 p-1 rounded-xl">
                            <TabsTrigger value="activity" className="data-[state=active]:bg-white/70 dark:data-[state=active]:bg-black/20 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 text-slate-600 dark:text-slate-300 text-xs">Activity</TabsTrigger>
                            <TabsTrigger value="tasks" className="data-[state=active]:bg-white/70 dark:data-[state=active]:bg-black/20 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 text-slate-600 dark:text-slate-300 text-xs">Tasks</TabsTrigger>
                            <TabsTrigger value="storage" className="data-[state=active]:bg-white/70 dark:data-[state=active]:bg-black/20 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 text-slate-600 dark:text-slate-300 text-xs">Storage</TabsTrigger>
                        </TabsList>
                        <TabsContent value="activity" className="mt-4">
                            <div className="h-48 w-full relative bg-white/20 dark:bg-black/10 rounded-2xl border border-white/30 dark:border-white/10 overflow-hidden">
                                <PerformanceChart />
                                <div className="absolute bottom-2 right-2 bg-white/40 dark:bg-black/40 backdrop-blur-md rounded-lg px-2 py-1 border border-white/50 dark:border-white/10">
                                    <div className="text-xs text-slate-500 dark:text-slate-400">System Load</div>
                                    <div className="text-sm font-mono text-cyan-600 dark:text-cyan-400">{systemMetrics.cpuUsage}%</div>
                                </div>
                            </div>
                        </TabsContent>
                        <TabsContent value="tasks" className="mt-4 text-xs">
                            <div className="bg-transparent rounded-2xl border border-white/30 dark:border-white/10 overflow-hidden">
                                <div className="divide-y divide-white/20 dark:divide-white/5">
                                    <ProcessRowDetailedCompact pid="1024" name="Analyzing market data" cpu={12.4} memory={345} />
                                    <ProcessRowDetailedCompact pid="1842" name="Drafting email" cpu={8.7} memory={128} />
                                    <ProcessRowDetailedCompact pid="2156" name="Optimizing travel" cpu={5.2} memory={96} />
                                    <ProcessRowDetailedCompact pid="3012" name="Monitoring network" cpu={3.8} memory={84} />
                                </div>
                            </div>
                        </TabsContent>
                        <TabsContent value="storage" className="mt-4">
                            <div className="grid grid-cols-2 gap-3">
                                <StorageItemCompact name="Core Data" total={512} used={324} type="SSD" />
                                <StorageItemCompact name="User Data" total={2048} used={1285} type="HDD" />
                            </div>
                        </TabsContent>
                    </Tabs>
                </div>
            </CardContent>
        </FrostedCard>
    );
});