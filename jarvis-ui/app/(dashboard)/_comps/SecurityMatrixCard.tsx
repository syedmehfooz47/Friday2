import { memo } from "react";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Shield } from "lucide-react";
import { FrostedCard } from "./ui/FrostedCard";

interface SecurityMatrixCardProps {
  securityLevel: number;
}

export const SecurityMatrixCard = memo(function SecurityMatrixCard({ securityLevel }: SecurityMatrixCardProps) {
  return (
    <FrostedCard>
      <CardHeader className="pb-2"><CardTitle className="text-slate-800 dark:text-slate-100 flex items-center text-base"><Shield className="mr-2 h-5 w-5 text-green-500" />Security Matrix</CardTitle></CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between"><div className="text-sm text-slate-500 dark:text-slate-400">Threat Analysis</div><Badge className="bg-green-500/20 text-green-400 border-green-500/50">Active</Badge></div>
          <div className="flex items-center justify-between"><div className="text-sm text-slate-500 dark:text-slate-400">Data Encryption</div><Badge className="bg-green-500/20 text-green-400 border-green-500/50">Active</Badge></div>
          <div className="flex items-center justify-between"><div className="text-sm text-slate-500 dark:text-slate-400">Firewall Integrity</div><Badge className="bg-green-500/20 text-green-400 border-green-500/50">Active</Badge></div>
          <div className="flex items-center justify-between"><div className="text-sm text-slate-500 dark:text-slate-400">Threat Database</div><div className="text-sm text-cyan-600 dark:text-cyan-400">Updated <span className="text-slate-400 dark:text-slate-500">12 min ago</span></div></div>
          <div className="pt-2 mt-2 border-t border-slate-900/10 dark:border-slate-50/10">
            <div className="flex items-center justify-between mb-2"><div className="text-sm font-medium">Security Level</div><div className="text-sm text-cyan-600 dark:text-cyan-400">{securityLevel}%</div></div>
            <Progress value={securityLevel} className="h-2 bg-slate-900/10 dark:bg-slate-50/10"><div className="h-full bg-gradient-to-r from-green-500 to-cyan-500 rounded-full" style={{ width: `${securityLevel}%` }} /></Progress>
          </div>
        </div>
      </CardContent>
    </FrostedCard>
  );
});
