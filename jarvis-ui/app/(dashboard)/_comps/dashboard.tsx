// jarvis-ui/app/(dashboard)/_comps/dashboard.tsx

"use client"

import { useEffect, useState, useRef, memo } from "react";
import { useTheme } from "next-themes";
// Import Dashboard Components
import { Header } from "./Header";
import { CognitiveOverviewCard } from "./CognitiveOverviewCard";
import { CommunicationHubCard } from "./CommunicationHubCard";
import { SystemOverviewCard } from "./SystemOverviewCard";
import { OperationalParametersCard } from "./OperationalParametersCard";
import { WeatherCard } from "./WeatherCard";
import { Sidebar } from "./Sidebar";
import { SystemTimeCard } from "./SystemTimeCard";
import { SecurityMatrixCard } from "./SecurityMatrixCard";
import { PriorityAlertsCard } from "./PriorityAlertsCard";

// Particle Class for background effect (optional)
class Particle {
  x: number; y: number; size: number; speedX: number; speedY: number; color: string; canvasWidth: number; canvasHeight: number;
  constructor(canvasWidth: number, canvasHeight: number, theme: string) {
    this.canvasWidth = canvasWidth; this.canvasHeight = canvasHeight;
    this.x = Math.random() * this.canvasWidth; this.y = Math.random() * this.canvasHeight;
    this.size = Math.random() * 1.5 + 0.5; // Slightly smaller max size
    this.speedX = (Math.random() - 0.5) * 0.15; // Slightly slower speed
    this.speedY = (Math.random() - 0.5) * 0.15; // Slightly slower speed
    // Adjusted opacity based on theme
    this.color = theme === "light" ? `rgba(100, 100, 120, ${Math.random() * 0.25 + 0.05})` : `rgba(200, 220, 255, ${Math.random() * 0.3 + 0.05})`;
  }
  update() {
    this.x += this.speedX; this.y += this.speedY;
    // Wrap around edges instead of bouncing
    if (this.x > this.canvasWidth + this.size) this.x = -this.size;
    else if (this.x < -this.size) this.x = this.canvasWidth + this.size;
    if (this.y > this.canvasHeight + this.size) this.y = -this.size;
    else if (this.y < -this.size) this.y = this.canvasHeight + this.size;
  }
  draw(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = this.color; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
  }
}

const DashboardComponent = () => {
  const { resolvedTheme } = useTheme();
  // State for security level (can be fetched or updated via WebSocket later)
  const [securityLevel, setSecurityLevel] = useState(75);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true); // Initial loading state
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Simulate initial loading time
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1500); // Shorter load time
    return () => clearTimeout(timer);
  }, []);

  // Update current time every second
  useEffect(() => {
    const interval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  // Initialize and manage particle animation canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || typeof window === 'undefined') return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let particles: Particle[] = [];
    let animationFrameId: number;

    const setupCanvas = () => {
        if (!canvas || !ctx) return;
        // Match canvas dimensions to its container size
        canvas.width = canvas.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio); // Scale context for High DPI displays
        // Initialize particles based on new dimensions
        particles = Array.from({ length: 40 }, () => new Particle(canvas.offsetWidth, canvas.offsetHeight, resolvedTheme || 'dark')); // Reduced particle count
    };

    const animate = () => {
      if (!ctx || !canvas) return;
      // Use offsetWidth/Height as particle boundaries are in CSS pixels
      const canvasWidth = canvas.offsetWidth;
      const canvasHeight = canvas.offsetHeight;
      ctx.clearRect(0, 0, canvasWidth, canvasHeight); // Clear based on CSS pixel dimensions
      for (const particle of particles) {
        particle.update();
        particle.draw(ctx);
      }
      animationFrameId = requestAnimationFrame(animate);
    };

    // Debounced resize handler
    let resizeTimeout: NodeJS.Timeout;
    const handleResize = () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(setupCanvas, 100); // Debounce resize event
    };

    setupCanvas(); // Initial setup
    animate(); // Start animation
    window.addEventListener("resize", handleResize); // Listen for resize

    // Cleanup function
    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
      clearTimeout(resizeTimeout);
    };
  }, [resolvedTheme]); // Re-initialize if theme changes

  return (
    // Main container with background styles and canvas
    <div className="min-h-screen text-slate-900 dark:text-slate-100 relative overflow-hidden transition-colors duration-500">
      {/* Background Gradient Layers */}
      <div aria-hidden="true" className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute inset-0 bg-white dark:bg-slate-950"></div>
          {/* Subtle gradient blurs */}
          <div className="absolute top-0 left-0 h-[40rem] w-[40rem] bg-cyan-200/30 dark:bg-cyan-500/10 rounded-full blur-[18rem] filter opacity-60 dark:opacity-40 will-change-transform"></div>
          <div className="absolute -bottom-20 -right-20 h-[40rem] w-[40rem] bg-purple-200/30 dark:bg-purple-500/10 rounded-full blur-[18rem] filter opacity-60 dark:opacity-40 will-change-transform"></div>
          <div className="absolute top-1/3 left-1/2 h-[30rem] w-[30rem] -translate-x-1/2 -translate-y-1/2 bg-blue-200/30 dark:bg-blue-500/10 rounded-full blur-[16rem] filter opacity-50 dark:opacity-30 will-change-transform"></div>
      </div>
      {/* Particle Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full opacity-60 dark:opacity-25 pointer-events-none" />

       {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/70 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-500">
          <div className="flex flex-col items-center">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
              <div className="absolute inset-0 border-t-4 border-cyan-500 rounded-full animate-spin"></div>
            </div>
            <div className="mt-4 text-cyan-600 dark:text-cyan-400 font-mono text-sm tracking-wider animate-pulse">INITIALIZING INTERFACE...</div>
          </div>
        </div>
      )}

      {/* Main Content Area (conditionally rendered or animated in) */}
      <div className={`relative z-10 p-4 sm:p-6 lg:p-8 transition-opacity duration-500 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
        <Header />
        {/* Dashboard Grid Layout */}
        <div className="grid grid-cols-12 gap-6 mt-6">
          {/* Left Column (Sidebar, Weather, Security, Alerts) */}
          <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
            <Sidebar /> {/* Navigation */}
            <WeatherCard /> {/* Real-time Weather */}
            <SecurityMatrixCard securityLevel={securityLevel} /> {/* Security Status */}
            <PriorityAlertsCard /> {/* Important Backend Events */}
          </div>

          {/* Center Column (Core Interaction and Communication) */}
          <div className="col-span-12 lg:col-span-6 flex flex-col gap-6">
            <CognitiveOverviewCard /> {/* Mic/Stop Controls & Visualizer */}
            <CommunicationHubCard /> {/* Real-time Inbox/Notifications */}
          </div>

          {/* Right Column (Time, System Stats, Parameters) */}
          <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
            <SystemTimeCard currentTime={currentTime} /> {/* Current Time & Uptime */}
            <SystemOverviewCard /> {/* Real-time CPU, Mem, Network */}
            <OperationalParametersCard /> {/* Theme, Brightness, Other Toggles */}
          </div>
        </div>
      </div>
    </div>
  )
}

export default memo(DashboardComponent); // Memoize for performance