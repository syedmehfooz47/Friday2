// jarvis-ui/app/(dashboard)/_comps/Header.tsx

"use client"
import { memo, useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { useJarvisStore } from "@/app/store/jarvisStore"; // Using Zustand for status
import { BrainCircuit, Search, Bell, Sun, Moon, LogOut, User, CheckCircle } from "lucide-react"; // Added CheckCircle, LogOut, User
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"; // Added Dropdown components
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area"; // Added ScrollArea

// Interface for Notifications (align with backend structure)
interface Notification {
    id: string;
    type: string; // e.g., 'email', 'telegram', 'system', 'file'
    title: string;
    message: string;
    timestamp: string; // ISO string format preferred
    unread: boolean;
    // Optional: Add actions like opening a file
    action?: { type: 'open_file', path: string } | { type: 'view_email', id: string };
}

interface HeaderProps {
    onAvatarClick?: () => void; // Prop kept if needed elsewhere, but dropdown handles profile now
}

export const Header = memo(function Header({ onAvatarClick }: HeaderProps) {
    const [isMounted, setIsMounted] = useState(false);
    const { resolvedTheme, setTheme } = useTheme();
    const { status } = useJarvisStore(); // Get status from Zustand
    const [notifications, setNotifications] = useState<Notification[]>([]); // State for notifications
    const [showNotifications, setShowNotifications] = useState(false); // State for notification dropdown

    useEffect(() => {
        setIsMounted(true);

        // --- Mock Notification Setup (Replace with WebSocket listener) ---
        // In WebSocketProvider, you'd update this state when 'new_notifications' is received
        const mockNotifications: Notification[] = [
            { id: "1", type: "email", title: "New Email from Alice", message: "Meeting Confirmation", timestamp: new Date(Date.now() - 5 * 60000).toISOString(), unread: true },
            { id: "2", type: "telegram", title: "Telegram: Bob", message: "Check this link: ...", timestamp: new Date(Date.now() - 15 * 60000).toISOString(), unread: true },
            { id: "3", type: "system", title: "System Update", message: "Core module updated successfully.", timestamp: new Date(Date.now() - 60 * 60000).toISOString(), unread: false },
            { id: "4", type: "file", title: "PDF Generated", message: "Report_Q3.pdf created.", timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(), unread: true, action: { type: 'open_file', path: '/path/to/Report_Q3.pdf' } }, // Example action
        ];
        setNotifications(mockNotifications);
        // --- End Mock Notification Setup ---

    }, []);

    const toggleTheme = () => {
        setTheme(resolvedTheme === "dark" ? "light" : "dark");
    };

    const renderThemeToggle = () => {
        if (!isMounted) return <div className="h-5 w-5" />; // Placeholder for SSR
        return resolvedTheme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />;
    };

    const unreadCount = notifications.filter(n => n.unread).length;

    const handleNotificationClick = (notification: Notification) => {
        // Mark as read (update state, potentially notify backend)
        setNotifications(prev => prev.map(n => n.id === notification.id ? { ...n, unread: false } : n));
        // Handle actions if present
        if (notification.action) {
            if (notification.action.type === 'open_file') {
                // TODO: Implement file opening logic (likely needs backend API call)
                console.log("Attempting to open file:", notification.action.path);
                alert(`Open file: ${notification.action.path}\n(Implementation needed)`);
            } else if (notification.action.type === 'view_email') {
                 // TODO: Implement navigation or modal to view email
                 console.log("Viewing email:", notification.action.id);
                 alert(`View email ID: ${notification.action.id}\n(Implementation needed)`);
            }
        }
    };

    const markAllRead = () => {
         setNotifications(prev => prev.map(n => ({ ...n, unread: false })));
         // TODO: Optionally notify backend that all are read
    }

    const handleLogout = () => {
         // TODO: Implement actual logout logic
         console.log("Logout clicked");
         alert("Logout functionality not implemented yet.");
    }

    return (
        <header className="flex items-center justify-between py-4 border-b border-slate-900/10 dark:border-slate-50/10 mb-6">
            {/* Logo and Status */}
            <div className="flex items-center space-x-3">
                <BrainCircuit className="h-8 w-8 text-cyan-500 flex-shrink-0" />
                <div>
                    <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent block leading-tight">JARVIS AI</span>
                    <p className={`text-xs font-mono capitalize transition-colors duration-300 ${
                        status === 'Online' ? 'text-green-500' : status === 'Offline' ? 'text-red-500' : 'text-amber-500'
                    }`}>
                        {status}
                    </p>
                </div>
            </div>

             {/* Search and Controls */}
            <div className="flex items-center space-x-4 md:space-x-6">
                {/* Search Bar (Hidden on small screens) */}
                <div className="hidden md:flex items-center space-x-1 bg-white/40 dark:bg-slate-900/40 backdrop-blur-xl rounded-full px-3 py-1.5 border border-white/50 dark:border-white/10 shadow-sm">
                    <Search className="h-4 w-4 text-slate-500 dark:text-slate-400" />
                    <input type="text" placeholder="Ask Jarvis..." className="bg-transparent border-none focus:outline-none text-sm w-40 placeholder:text-slate-400 dark:placeholder:text-slate-500 text-slate-800 dark:text-slate-100" />
                </div>

                {/* Icons and Profile */}
                <div className="flex items-center space-x-2">
                    <TooltipProvider delayDuration={100}>
                        {/* Notification Dropdown */}
                        <DropdownMenu open={showNotifications} onOpenChange={setShowNotifications}>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" size="icon" className="relative text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 focus-visible:ring-cyan-500">
                                            <Bell className="h-5 w-5" />
                                            {unreadCount > 0 && (
                                                <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-cyan-500 text-white text-[10px] pointer-events-none">
                                                    {unreadCount > 9 ? '9+' : unreadCount}
                                                </Badge>
                                            )}
                                        </Button>
                                    </DropdownMenuTrigger>
                                </TooltipTrigger>
                                <TooltipContent><p>Notifications</p></TooltipContent>
                            </Tooltip>
                            <DropdownMenuContent align="end" className="w-80 md:w-96 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-white/50 dark:border-white/10 shadow-xl">
                                <DropdownMenuLabel className="flex justify-between items-center">
                                    Notifications
                                    {unreadCount > 0 && (
                                        <Button variant="link" size="sm" className="h-auto p-0 text-xs text-cyan-500 hover:text-cyan-600" onClick={markAllRead}>Mark all read</Button>
                                    )}
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <ScrollArea className="h-[300px] pr-1">
                                    {notifications.length === 0 ? (
                                        <div className="p-4 text-center text-slate-500 dark:text-slate-400 text-sm">
                                            No new notifications
                                        </div>
                                    ) : (
                                        notifications.map((notification) => (
                                            <DropdownMenuItem
                                                key={notification.id}
                                                className={`flex flex-col items-start p-3 cursor-pointer mb-1 rounded-md ${notification.unread ? 'bg-cyan-500/10' : ''}`}
                                                onClick={() => handleNotificationClick(notification)}
                                            >
                                                <div className="flex items-start justify-between w-full">
                                                    <div className="flex-1 overflow-hidden">
                                                        <p className={`font-semibold text-sm truncate ${notification.unread ? 'text-slate-800 dark:text-slate-100' : 'text-slate-600 dark:text-slate-300'}`}>{notification.title}</p>
                                                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 truncate">{notification.message}</p>
                                                        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                                                            {new Date(notification.timestamp).toLocaleString()} {/* Show full date/time */}
                                                        </p>
                                                    </div>
                                                    {notification.unread && (
                                                        <div className="h-2 w-2 rounded-full bg-cyan-500 flex-shrink-0 ml-2 mt-1" aria-label="Unread" />
                                                    )}
                                                </div>
                                            </DropdownMenuItem>
                                        ))
                                    )}
                                </ScrollArea>
                                {/* Add Footer if needed, e.g., View All button */}
                                {/* <DropdownMenuSeparator />
                                <DropdownMenuItem className="justify-center text-cyan-500 hover:!text-cyan-600 !bg-transparent">
                                    View All Notifications
                                </DropdownMenuItem> */}
                            </DropdownMenuContent>
                        </DropdownMenu>

                        {/* Theme Toggle */}
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button variant="ghost" size="icon" onClick={toggleTheme} className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 focus-visible:ring-cyan-500">
                                    {renderThemeToggle()}
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent><p>Toggle theme ({resolvedTheme === 'dark' ? 'Light' : 'Dark'})</p></TooltipContent>
                        </Tooltip>
                    </TooltipProvider>

                    {/* Profile Dropdown */}
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <button className="rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2 focus-visible:ring-offset-background dark:focus-visible:ring-offset-slate-950">
                                <Avatar className="h-9 w-9">
                                    <AvatarImage src="/placeholder-user.jpg" alt="User" />
                                    <AvatarFallback className="bg-slate-200 dark:bg-slate-700 text-cyan-500">M</AvatarFallback> {/* Use initial */}
                                </Avatar>
                            </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-56 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-white/50 dark:border-white/10 shadow-xl">
                            <DropdownMenuLabel>My Account</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="cursor-pointer">
                                <User className="mr-2 h-4 w-4" />
                                <span>Profile</span>
                            </DropdownMenuItem>
                             <DropdownMenuItem disabled className="opacity-100 cursor-default focus:!bg-transparent">
                                <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                                <span className="text-green-600 dark:text-green-400">Status: Online</span>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-red-600 dark:text-red-400 focus:!bg-red-500/10 focus:!text-red-700 dark:focus:!text-red-500 cursor-pointer" onClick={handleLogout}>
                                <LogOut className="mr-2 h-4 w-4" />
                                <span>Logout</span>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>
        </header>
    );
});