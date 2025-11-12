// jarvis-ui/app/(dashboard)/_comps/CommunicationHubCard.tsx

"use client"; // Needs client-side state

import { memo, useState, useEffect } from "react"; // Added useState, useEffect
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Inbox, Mail, MessageSquare, AlertTriangle, FileText, Bot } from "lucide-react"; // Added more icons
import { FrostedCard } from "./ui/FrostedCard";
import { ScrollArea } from "@/components/ui/scroll-area"; // Import ScrollArea
import { useWebSocket } from "@/app/providers/WebSocketProvider"; // Import WebSocket hook

// Define Notification type (should match backend/header)
interface NotificationItem {
    id: string;
    type: string; // 'email', 'telegram', 'system', 'file', 'missed_call', 'jarvis' etc.
    sender: string; // Extracted sender name
    time: string; // Formatted time string
    message: string; // Snippet or description
    avatar?: string; // Optional avatar URL
    unread: boolean;
    rawTimestamp: string; // ISO timestamp for sorting
}

// Map notification types to icons
const notificationIcons: { [key: string]: React.ElementType } = {
    email: Mail,
    telegram: MessageSquare,
    missed_call: AlertTriangle,
    file: FileText,
    jarvis: Bot,
    system: Bot,
    default: Inbox // Fallback icon
};

const CommunicationItem = memo(function CommunicationItem({ item }: { item: NotificationItem }) {
    const Icon = notificationIcons[item.type] || notificationIcons.default;
    const fallbackInitial = item.sender ? item.sender.charAt(0).toUpperCase() : '?';

    return (
        <div className={`flex space-x-3 p-3 rounded-xl transition-colors duration-200 ${item.unread ? "bg-white/40 dark:bg-black/20 shadow-sm" : "hover:bg-white/20 dark:hover:bg-black/10"}`}>
            <Avatar className="h-9 w-9">
                {item.avatar ? (
                    <AvatarImage src={item.avatar} alt={item.sender} />
                ) : (
                     <div className={`flex items-center justify-center h-full w-full rounded-full ${item.unread ? 'bg-cyan-500/20' : 'bg-slate-200 dark:bg-slate-700'}`}>
                        <Icon className={`h-4 w-4 ${item.unread ? 'text-cyan-500' : 'text-slate-500 dark:text-slate-400'}`} />
                    </div>
                )}
                 {/* Fallback can be simple or based on sender */}
                 <AvatarFallback className={`bg-slate-200 dark:bg-slate-700 ${item.unread ? 'text-cyan-500 font-semibold' : 'text-slate-500'}`}>
                    {fallbackInitial}
                 </AvatarFallback>
            </Avatar>
            <div className="flex-1 overflow-hidden">
                <div className="flex items-center justify-between">
                    <div className={`text-sm font-medium truncate pr-2 ${item.unread ? 'text-slate-800 dark:text-slate-100' : 'text-slate-600 dark:text-slate-300'}`}>
                        {item.sender}
                    </div>
                    <div className="text-xs text-slate-400 dark:text-slate-500 flex-shrink-0">{item.time}</div>
                </div>
                <div className={`text-xs mt-1 truncate ${item.unread ? 'text-slate-600 dark:text-slate-300' : 'text-slate-500 dark:text-slate-400'}`}>
                    {item.message}
                </div>
            </div>
            {item.unread && (
                <div className="flex-shrink-0 self-center pl-1">
                    <div className="h-2 w-2 rounded-full bg-cyan-500 animate-pulse"></div>
                </div>
            )}
        </div>
    )
});

export const CommunicationHubCard = memo(function CommunicationHubCard() {
    const [notifications, setNotifications] = useState<NotificationItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const { isConnected } = useWebSocket();

    // Listen for WebSocket messages to update notifications
    useEffect(() => {
        if (!isConnected) {
            setIsLoading(true);
            return;
        }

        // Set up WebSocket message listener
        const handleWebSocketMessage = (event: CustomEvent) => {
            const data = event.detail;
            if (data.type === 'new_notifications') {
                const newNotifications = data.payload.notifications.map((n: any) => ({
                    ...n,
                    time: new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    rawTimestamp: n.timestamp,
                }));

                setNotifications(prev => {
                    // Combine and deduplicate notifications
                    const combined = [...newNotifications, ...prev];
                    const unique = combined.filter((item, index, self) =>
                        index === self.findIndex(t => t.id === item.id)
                    );
                    // Sort by timestamp, newest first
                    return unique.sort((a, b) => new Date(b.rawTimestamp).getTime() - new Date(a.rawTimestamp).getTime());
                });
            }
        };

        // Add event listener for WebSocket messages
        window.addEventListener('websocket-message', handleWebSocketMessage as EventListener);

        // Mark as loaded once connected
        setIsLoading(false);

        return () => {
            window.removeEventListener('websocket-message', handleWebSocketMessage as EventListener);
        };
    }, [isConnected]);

    const unreadCount = notifications.filter(n => n.unread).length;

    return (
        <FrostedCard className="flex flex-col h-full"> {/* Added flex flex-col h-full */}
            <CardHeader className="pb-3 flex flex-row items-center justify-between flex-shrink-0">
                <CardTitle className="text-slate-800 dark:text-slate-100 flex items-center text-base font-semibold">
                    <Inbox className="mr-2 h-5 w-5 text-blue-500" />
                    Inbox & Notifications
                </CardTitle>
                {unreadCount > 0 && (
                    <Badge variant="outline" className="bg-blue-500/10 text-blue-500 dark:text-blue-400 border-blue-500/30 dark:border-blue-500/50">
                        {unreadCount} New
                    </Badge>
                )}
            </CardHeader>
            <CardContent className="flex-grow overflow-hidden p-2"> {/* Allow content to grow and hide overflow */}
                {isLoading ? (
                     <div className="flex justify-center items-center h-full text-slate-500 dark:text-slate-400">Loading...</div>
                ) : !isConnected ? (
                     <div className="flex justify-center items-center h-full text-amber-500 dark:text-amber-400 text-center p-4">
                        <div>
                            <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                            <p className="text-sm">Disconnected</p>
                        </div>
                    </div>
                ) : notifications.length === 0 ? (
                     <div className="flex justify-center items-center h-full text-slate-500 dark:text-slate-400 text-center p-4">
                        <Inbox className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No notifications</p>
                    </div>
                ) : (
                     <ScrollArea className="h-full pr-2"> {/* Ensure ScrollArea takes full height */}
                        <div className="space-y-2">
                             {notifications.map((item) => (
                                <CommunicationItem key={item.id} item={item} />
                            ))}
                        </div>
                    </ScrollArea>
                )}
            </CardContent>
        </FrostedCard>
    );
});