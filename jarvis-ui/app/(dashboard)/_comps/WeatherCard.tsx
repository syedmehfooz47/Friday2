// jarvis-ui/app/(dashboard)/_comps/WeatherCard.tsx

"use client";

import { memo, useEffect, useState } from "react";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FrostedCard } from "./ui/FrostedCard";
import { Sun, Wind, Droplets, Cloud, CloudFog, Zap, Snowflake, CloudRain, AlertTriangle } from "lucide-react";
import { fetchWeather } from "@/app/services/api";

const WeatherIcon = memo(function WeatherIcon({ icon, className }: { icon: string; className: string; }) {
    // ... (same as before)
    switch (icon) {
        case "01d": case "01n": return <Sun className={className} />;
        case "02d": case "02n": return <Cloud className={className} />;
        case "03d": case "03n": case "04d": case "04n": return <Cloud className={className} />;
        case "09d": case "09n": return <CloudRain className={className} />;
        case "10d": case "10n": return <CloudRain className={className} />;
        case "11d": case "11n": return <Zap className={className} />;
        case "13d": case "13n": return <Snowflake className={className} />;
        case "50d": case "50n": return <CloudFog className={className} />;
        default: return <Sun className={className} />;
    }
});

export const WeatherCard = memo(function WeatherCard() {
    const [weather, setWeather] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadWeather = async () => {
            const data = await fetchWeather();
            if (data && data.status === 'success') {
                setWeather(data);
                setError(null);
            } else {
                setError(data?.message || "Failed to fetch weather data.");
            }
        };
        
        loadWeather();
        const interval = setInterval(loadWeather, 600000); // Fetch every 10 minutes
        
        // Listen for real-time weather updates via WebSocket
        const handleWeatherUpdate = (event: any) => {
            const data = event.detail;
            if (data.type === 'weather_update' && data.payload && data.payload.status === 'success') {
                setWeather(data.payload);
                setError(null);
            }
        };
        
        window.addEventListener('websocket-message', handleWeatherUpdate);
        
        return () => {
            clearInterval(interval);
            window.removeEventListener('websocket-message', handleWeatherUpdate);
        };
    }, []);

    if (error) {
        return (
            <FrostedCard>
                <CardHeader className="pb-2"><CardTitle className="text-slate-800 dark:text-slate-100 text-base">Current Weather</CardTitle></CardHeader>
                <CardContent>
                    <div className="flex flex-col justify-center items-center h-full text-center text-amber-500">
                        <AlertTriangle className="h-8 w-8 mb-2" />
                        <p className="text-xs font-semibold">Weather Unavailable</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 px-2">{error}</p>
                    </div>
                </CardContent>
            </FrostedCard>
        );
    }
    
    if (!weather) {
        return (
            <FrostedCard>
                <CardHeader className="pb-2"><CardTitle className="text-slate-800 dark:text-slate-100 text-base">Current Weather</CardTitle></CardHeader>
                <CardContent><div className="flex justify-center items-center h-24 text-slate-500 dark:text-slate-400">Loading weather...</div></CardContent>
            </FrostedCard>
        );
    }

    return (
        <FrostedCard>
            <CardHeader className="pb-2"><CardTitle className="text-slate-800 dark:text-slate-100 text-base">Weather in {weather.city}</CardTitle></CardHeader>
            <CardContent>
                <div className="flex flex-col items-center space-y-4">
                    <div className="flex items-center space-x-4">
                        <WeatherIcon icon={weather.icon || '01d'} className="h-12 w-12 text-amber-400" />
                        <div>
                            <div className="text-4xl font-bold text-slate-800 dark:text-slate-100">{weather.temperature_f || weather.temp}°F</div>
                            <div className="text-sm text-slate-500 dark:text-slate-400">{weather.condition || weather.description}</div>
                        </div>
                    </div>
                    <div className="w-full text-xs text-slate-500 dark:text-slate-400 space-y-2 pt-4 border-t border-slate-900/10 dark:border-slate-50/10">
                        <div className="flex justify-between"><span className="flex items-center"><Wind className="h-3 w-3 mr-1.5" />Wind</span><span>{weather.wind_speed_mph || weather.wind_speed} mph</span></div>
                        <div className="flex justify-between"><span className="flex items-center"><Droplets className="h-3 w-3 mr-1.5" />Humidity</span><span>{weather.humidity}%</span></div>
                        <div className="flex justify-between"><span className="flex items-center"><Cloud className="h-3 w-3 mr-1.5" />Feels Like</span><span>{weather.feels_like_f || weather.feels_like}°F</span></div>
                    </div>
                </div>
            </CardContent>
        </FrostedCard>
    );
});