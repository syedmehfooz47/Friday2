// jarvis-ui/app/chat/page.tsx

"use client";

import { memo } from "react";
import ChatClient from './_comps/chat';
import { Header } from "@/app/(dashboard)/_comps/Header";
import { Sidebar } from "@/app/(dashboard)/_comps/Sidebar";
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
        if (this.x > this.canvasWidth || this.x < 0) this.speedX *= -1;
        if (this.y > this.canvasHeight || this.y < 0) this.speedY *= -1;
    }
    draw(ctx: CanvasRenderingContext2D) {
        ctx.fillStyle = this.color; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
    }
}

function ChatPageLayout() {
    const { resolvedTheme } = useTheme();
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        let particles: Particle[] = [];
        const initParticles = () => {
            particles = [];
            for (let i = 0; i < 50; i++) {
                particles.push(new Particle(canvas.width, canvas.height, resolvedTheme || 'dark'));
            }
        };
        initParticles();
        let animationFrameId: number;
        const animate = () => {
            if (!ctx || !canvas) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (const p of particles) {
                p.update();
                p.draw(ctx);
            }
            animationFrameId = requestAnimationFrame(animate);
        };
        animate();
        const handleResize = () => {
            if (!canvas || !ctx) return;
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            initParticles();
        };
        window.addEventListener("resize", handleResize);
        return () => {
            window.removeEventListener("resize", handleResize);
            cancelAnimationFrame(animationFrameId);
        };
    }, [resolvedTheme]);

    return (
        <div className="min-h-screen text-slate-900 dark:text-slate-100 relative overflow-hidden transition-colors duration-500">
            <div aria-hidden="true" className="fixed inset-0 -z-10 overflow-hidden">
                <div className="absolute inset-0 bg-white dark:bg-slate-950"></div>
                <div className="absolute top-0 left-0 h-[40rem] w-[40rem] bg-cyan-200/50 dark:bg-cyan-500/20 rounded-full blur-[16rem] filter"></div>
                <div className="absolute -bottom-20 -right-20 h-[40rem] w-[40rem] bg-purple-200/50 dark:bg-purple-500/20 rounded-full blur-[16rem] filter"></div>
            </div>
            <canvas ref={canvasRef} className="absolute inset-0 w-full h-full opacity-50 dark:opacity-20" />
            <div className="relative z-10 flex flex-col h-screen">
                <div className="px-4 sm:px-6 lg:px-8">
                    <Header />
                </div>
                <div className="flex-1 flex overflow-hidden">
                    <div className="hidden lg:block">
                        <Sidebar />
                    </div>
                    <main className="flex-1 flex flex-col">
                        <ChatClient />
                    </main>
                </div>
            </div>
        </div>
    );
}

export default memo(ChatPageLayout);