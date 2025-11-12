// jarvis-ui/app/files/page.tsx

"use client";

import { memo } from "react";
import GeneratedFilesDisplay from './_comps/GeneratedFilesDisplay'; // Import the component
import { Header } from "@/app/(dashboard)/_comps/Header"; // Adjust import path
import { Sidebar } from "@/app/(dashboard)/_comps/Sidebar"; // Adjust import path
import { useTheme } from "next-themes";
import { useEffect, useRef } from "react";

// Particle class remains the same for background animation
class Particle {
    x: number; y: number; size: number; speedX: number; speedY: number; color: string; canvasWidth: number; canvasHeight: number;
    constructor(canvasWidth: number, canvasHeight: number, theme: string) {
        this.canvasWidth = canvasWidth; this.canvasHeight = canvasHeight;
        this.x = Math.random() * this.canvasWidth; this.y = Math.random() * this.canvasHeight;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = (Math.random() - 0.5) * 0.2; this.speedY = (Math.random() - 0.5) * 0.2;
        this.color = theme === "light" ? `rgba(100, 100, 120, ${Math.random() * 0.3 + 0.1})` : `rgba(200, 220, 255, ${Math.random() * 0.4 + 0.1})`;
    }
    update() {
        this.x += this.speedX; this.y += this.speedY;
        if (this.x > this.canvasWidth + this.size) this.x = -this.size;
        else if (this.x < -this.size) this.x = this.canvasWidth + this.size;
        if (this.y > this.canvasHeight + this.size) this.y = -this.size;
        else if (this.y < -this.size) this.y = this.canvasHeight + this.size;
    }
    draw(ctx: CanvasRenderingContext2D) {
        ctx.fillStyle = this.color; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
    }
}


function FilesPageLayout() {
    const { resolvedTheme } = useTheme();
    const canvasRef = useRef<HTMLCanvasElement>(null);

    // Background particle effect (copied from chat page)
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;
        canvas.width = canvas.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        let particles: Particle[] = [];
        const initParticles = () => {
            particles = Array.from({ length: 40 }, () => new Particle(canvas.offsetWidth, canvas.offsetHeight, resolvedTheme || 'dark'));
        };
        initParticles();
        let animationFrameId: number;
        const animate = () => {
            if (!ctx || !canvas) return;
             const canvasWidth = canvas.offsetWidth;
             const canvasHeight = canvas.offsetHeight;
            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            for (const p of particles) { p.update(); p.draw(ctx); }
            animationFrameId = requestAnimationFrame(animate);
        };
        animate();
        let resizeTimeout: NodeJS.Timeout;
        const handleResize = () => {
             clearTimeout(resizeTimeout);
             resizeTimeout = setTimeout(() => {
                  if (!canvas || !ctx) return;
                  canvas.width = canvas.offsetWidth * window.devicePixelRatio;
                  canvas.height = canvas.offsetHeight * window.devicePixelRatio;
                  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
                  initParticles();
             }, 100);
        };
        window.addEventListener("resize", handleResize);
        return () => {
            window.removeEventListener("resize", handleResize);
            cancelAnimationFrame(animationFrameId);
             clearTimeout(resizeTimeout);
        };
    }, [resolvedTheme]);

    return (
        <div className="min-h-screen text-slate-900 dark:text-slate-100 relative overflow-hidden transition-colors duration-500">
            {/* Background Effects */}
            <div aria-hidden="true" className="fixed inset-0 -z-10 overflow-hidden">
                <div className="absolute inset-0 bg-white dark:bg-slate-950"></div>
                 <div className="absolute top-0 left-0 h-[40rem] w-[40rem] bg-cyan-200/30 dark:bg-cyan-500/10 rounded-full blur-[18rem] filter opacity-70 dark:opacity-50"></div>
                 <div className="absolute -bottom-20 -right-20 h-[40rem] w-[40rem] bg-purple-200/30 dark:bg-purple-500/10 rounded-full blur-[18rem] filter opacity-70 dark:opacity-50"></div>
            </div>
            <canvas ref={canvasRef} className="absolute inset-0 w-full h-full opacity-40 dark:opacity-20 pointer-events-none" />

            {/* Layout Structure */}
            <div className="relative z-10 flex flex-col h-screen">
                <div className="px-4 sm:px-6 lg:px-8 flex-shrink-0">
                    <Header />
                </div>
                <div className="flex-1 flex overflow-hidden">
                     {/* Sidebar - conditionally shown based on screen size */}
                    <div className="hidden lg:block flex-shrink-0 w-64 p-4"> {/* Adjust width as needed */}
                        <Sidebar />
                    </div>
                    {/* Main Content Area */}
                    <main className="flex-1 flex flex-col overflow-y-auto">
                        <GeneratedFilesDisplay /> {/* The main component for this page */}
                    </main>
                </div>
            </div>
        </div>
    );
}

export default memo(FilesPageLayout);