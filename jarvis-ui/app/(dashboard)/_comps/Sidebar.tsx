// File: jarvis-ui/app/(dashboard)/_comps/Sidebar.tsx

"use client";
import { memo } from "react";
import Link from "next/link";
import { CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { type LucideIcon, Terminal, MessageSquare, Inbox, Settings, User, FolderOpen } from "lucide-react"; // Added FolderOpen
import { FrostedCard } from "./ui/FrostedCard";
import { usePathname } from 'next/navigation';

const NavItem = memo(function NavItem({ icon: Icon, label, href }: { icon: LucideIcon; label: string; href: string }) {
    const pathname = usePathname();
    const isActive = pathname === href; // Check for exact match first
    // Optional: Check if the current path starts with the href for parent routes
    // const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));

    return (
        <Link href={href} passHref legacyBehavior>
            <Button
                variant="ghost"
                className={`w-full justify-start rounded-lg text-sm px-3 py-2 ${isActive
                    ? "bg-white/70 dark:bg-black/20 text-cyan-600 dark:text-cyan-400 font-medium shadow-inner"
                    : "text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-black/10 hover:text-slate-900 dark:hover:text-slate-100"
                }`}
                aria-current={isActive ? "page" : undefined}
            >
                <Icon className={`mr-2.5 h-4 w-4 ${isActive ? 'text-cyan-500' : 'text-slate-400 dark:text-slate-500'}`} />
                {label}
            </Button>
        </Link>
    )
});

export const Sidebar = memo(function Sidebar() {
    return (
        <FrostedCard>
            <CardContent className="p-3">
                <nav className="space-y-1">
                    <NavItem icon={Terminal} label="Dashboard" href="/" />
                    <NavItem icon={MessageSquare} label="Chat" href="/chat" />
                    <NavItem icon={FolderOpen} label="Generated Files" href="/files" /> {/* <<< ADDED LINK */}
                    <NavItem icon={Inbox} label="Inbox" href="#" /> {/* Placeholder */}
                    <NavItem icon={Settings} label="Settings" href="/settings" />
                    <NavItem icon={User} label="Profile" href="#" /> {/* Placeholder */}
                </nav>
            </CardContent>
        </FrostedCard>
    );
});