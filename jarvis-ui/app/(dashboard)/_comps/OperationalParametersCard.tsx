// jarvis-ui/app/(dashboard)/_comps/OperationalParametersCard.tsx

"use client";

import { memo, useState, useEffect, useCallback } from "react";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Radio, Lock, Zap, Moon, Sun } from "lucide-react";
import { FrostedCard } from "./ui/FrostedCard";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import { getBrightness, setBrightness, changeTheme } from "@/app/services/api";

export const OperationalParametersCard = memo(function OperationalParametersCard() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [brightness, setBrightnessState] = useState<number[]>([50]);
  const [isBrightnessLoading, setIsBrightnessLoading] = useState(true);
  const [energySaver, setEnergySaver] = useState(false);
  const [highAlert, setHighAlert] = useState(true);

  // Fetch initial brightness
  const fetchInitialBrightness = useCallback(async () => {
    setIsBrightnessLoading(true);
    try {
      const result = await getBrightness();
      if (result.brightness !== undefined) {
        setBrightnessState([result.brightness]);
      } else {
        console.warn("Could not fetch initial brightness:", result.error);
      }
    } catch (error) {
      console.error("Error fetching brightness:", error);
    } finally {
      setIsBrightnessLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitialBrightness();
  }, [fetchInitialBrightness]);

  // Handler for brightness slider changes
  const handleBrightnessChange = async (value: number[]) => {
    const newBrightness = value[0];
    setBrightnessState([newBrightness]);

    try {
      const result = await setBrightness(newBrightness);
      if (result.success) {
        console.log("Brightness updated:", result.message);
      } else {
        toast.error('Failed to set brightness', { description: result.error });
        // Revert on error
        await fetchInitialBrightness();
      }
    } catch (error: any) {
      toast.error('Failed to set brightness', { description: error.message });
      await fetchInitialBrightness();
    }
  };

  // Handler for Windows theme toggle switch
  const handleThemeToggle = async (isDark: boolean) => {
    const newOsTheme = isDark ? 'dark' : 'light';
    
    // DO NOT change UI theme - only change Windows OS theme
    // The UI theme is controlled by the user in the theme toggle (Header.tsx)

    try {
      const result = await changeTheme(newOsTheme);

      if (result.success) {
        toast.success(`Windows theme changed to ${newOsTheme} mode`);
      } else if (result.error && result.error.includes("not available")) {
        toast.info("Windows theme control not available on this system.");
      } else {
        toast.error('Failed to change Windows theme', { description: result.error });
      }
    } catch (error: any) {
      toast.error('Failed to change Windows theme', { description: error.message });
    }
  };

  const isCurrentlyDark = resolvedTheme === 'dark';

  return (
    <FrostedCard>
      <CardHeader className="pb-3">
        <CardTitle className="text-slate-800 dark:text-slate-100 text-base font-semibold">
          System Controls
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-5">
          {/* Windows Dark/Light Mode Switch */}
          <div className="flex items-center justify-between">
            <Label htmlFor="theme-switch" className="flex items-center text-sm text-slate-600 dark:text-slate-300 cursor-pointer">
              {isCurrentlyDark ? (
                <Moon className="text-cyan-500 dark:text-cyan-400 mr-2 h-4 w-4" />
              ) : (
                <Sun className="text-cyan-500 dark:text-cyan-400 mr-2 h-4 w-4" />
              )}
              Windows Theme
            </Label>
            <Switch
              id="theme-switch"
              checked={isCurrentlyDark}
              onCheckedChange={handleThemeToggle}
              aria-label="Toggle Windows Dark/Light Theme"
            />
          </div>

          {/* Screen Brightness Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="brightness-slider" className="text-sm text-slate-600 dark:text-slate-300 flex items-center">
                <Zap className="text-cyan-500 dark:text-cyan-400 mr-2 h-4 w-4" />
                Screen Brightness
              </Label>
              <span className={`text-sm font-medium ${isBrightnessLoading ? 'text-slate-400 animate-pulse' : 'text-cyan-600 dark:text-cyan-400'}`}>
                {isBrightnessLoading ? '--' : brightness[0]}%
              </span>
            </div>
            <Slider
              id="brightness-slider"
              value={brightness}
              onValueChange={handleBrightnessChange}
              max={100}
              step={5}
              className="w-full [&>span:first-child>span]:bg-gradient-to-r [&>span:first-child>span]:from-cyan-500 [&>span:first-child>span]:to-blue-500"
              disabled={isBrightnessLoading}
              aria-label="Screen Brightness"
            />
          </div>

          {/* Other Operational Parameters */}
          <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-white/10">
            <Label htmlFor="energy-saver" className="flex items-center text-sm text-slate-500 dark:text-slate-400 cursor-pointer">
              <Radio className="text-slate-400 dark:text-slate-500 mr-2 h-4 w-4" />
              Energy Saver Mode
            </Label>
            <Switch
              id="energy-saver"
              checked={energySaver}
              onCheckedChange={setEnergySaver}
              aria-label="Toggle Energy Saver Mode"
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="high-alert" className="flex items-center text-sm text-slate-500 dark:text-slate-400 cursor-pointer">
              <Lock className="text-slate-400 dark:text-slate-500 mr-2 h-4 w-4" />
              High-Alert Protocol
            </Label>
            <Switch
              id="high-alert"
              checked={highAlert}
              onCheckedChange={setHighAlert}
              aria-label="Toggle High-Alert Protocol"
            />
          </div>
        </div>
      </CardContent>
    </FrostedCard>
  );
});