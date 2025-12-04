// jarvis-ui/app/chat/_comps/chat.tsx

"use client"

import { useEffect, useState, useRef, memo, FormEvent } from "react";
import { useTheme } from "next-themes"; // For particle theming
import { BrainCircuit, Send, Mic, MicOff, Square, RefreshCw, Wifi, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useJarvisStore, Message } from "@/app/store/jarvisStore"; // Import Message type from store
import { useWebSocket } from "@/app/providers/WebSocketProvider"; // WebSocket hook
import { toast } from "sonner"; // For notifications

// Extended message interface for chatlogs with date/time
interface ChatMessage extends Message {
  date?: string; // YYYY-MM-DD format
  time?: string; // HH:MM:SS format
}

// Particle class for background effect (optional, kept for consistency)
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

// Memoized Message Bubble Component
const MessageBubble = memo(function MessageBubble({ message }: { message: ChatMessage }) {
    const isUser = message.role === 'user';
    
    // Use the time field if available, otherwise format timestamp
    const timeDisplay = message.time 
        ? message.time.substring(0, 5) // HH:MM from HH:MM:SS
        : message.timestamp
        ? new Date(message.timestamp * 1000).toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit'
          })
        : "--:--";

    return (
        <div className={`flex items-start gap-3 w-full max-w-2xl ${isUser ? 'self-end flex-row-reverse' : 'self-start'}`}>
            <Avatar className="flex-shrink-0 mt-1">
                <AvatarImage src={isUser ? "/placeholder-user.jpg" : "/placeholder-logo.svg"} alt={message.role} />
                <AvatarFallback className="bg-slate-200 dark:bg-slate-700 text-cyan-500">
                    {isUser ? 'U' : <BrainCircuit className="w-4 h-4" />}
                </AvatarFallback>
            </Avatar>
            <div className={`rounded-2xl p-4 text-sm md:text-base leading-relaxed shadow-lg max-w-[80%] break-words ${
                    isUser
                        ? 'bg-blue-500/20 text-slate-800 dark:text-slate-100 rounded-br-none'
                        : 'bg-white/30 dark:bg-slate-900/40 backdrop-blur-xl border border-white/50 dark:border-white/10 text-slate-800 dark:text-slate-100 rounded-bl-none'
                }`}
            >
                {/* Use pre-wrap to preserve line breaks from the AI/user */}
                <p className="whitespace-pre-wrap">{message.content}</p>
                {/* Show timestamp */}
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 text-right">{timeDisplay}</p>
            </div>
        </div>
    );
});

// Date Header Component for separating messages by date
const DateHeader = memo(function DateHeader({ date }: { date: string }) {
    // Format date nicely (e.g., "October 31, 2025")
    const formattedDate = new Date(date + 'T00:00:00').toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    return (
        <div className="flex items-center justify-center my-6">
            <div className="bg-white/50 dark:bg-slate-800/50 backdrop-blur-xl border border-white/50 dark:border-white/10 rounded-full px-4 py-1.5 shadow-md">
                <p className="text-xs font-medium text-slate-600 dark:text-slate-300">{formattedDate}</p>
            </div>
        </div>
    );
});

// Main Chat Component
export default function ChatClient() {
    const { resolvedTheme } = useTheme();
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const messagesContainerRef = useRef<HTMLDivElement>(null);
    
    // Get messages and state from Zustand store
    const { messages, isMuted, setIsMuted, isAssistantSpeaking, setMessages } = useJarvisStore();
    
    // Get WebSocket send function and connection status
    const { send, isConnected, reconnect } = useWebSocket();
    
    const [input, setInput] = useState('');
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const [isReconnecting, setIsReconnecting] = useState(false);
    
    // Sticky date popup state
    const [currentDateHeader, setCurrentDateHeader] = useState<string | null>(null);
    const [showDatePopup, setShowDatePopup] = useState(false);
    
    // Store grouped messages by date
    const [groupedMessages, setGroupedMessages] = useState<{ [date: string]: ChatMessage[] }>({});

    // Load chat history from REST API (fast and stable)
    useEffect(() => {
        const loadChatHistory = async () => {
            setIsLoadingHistory(true);
            try {
                // Use Next.js API route for reliability (same-origin)
                const response = await fetch('/api/chatlogs?limit=1000');
                const data = await response.json();
                
                if (data.chatlogs && Array.isArray(data.chatlogs)) {
                    // Transform chatlogs to match Message interface
                    const transformedMessages: ChatMessage[] = data.chatlogs.map((log: any) => {
                        // Parse timestamp safely
                        let timestamp: number;
                        let date: string;
                        let time: string;
                        
                        try {
                            const logDate = new Date(log.timestamp);
                            if (isNaN(logDate.getTime())) {
                                // Invalid date, use current time as fallback
                                timestamp = Date.now() / 1000;
                                date = new Date().toISOString().split('T')[0];
                                time = new Date().toTimeString().split(' ')[0];
                            } else {
                                timestamp = logDate.getTime() / 1000;
                                date = log.date || logDate.toISOString().split('T')[0];
                                time = log.time || logDate.toTimeString().split(' ')[0];
                            }
                        } catch (error) {
                            // Fallback to current time if parsing fails
                            timestamp = Date.now() / 1000;
                            date = new Date().toISOString().split('T')[0];
                            time = new Date().toTimeString().split(' ')[0];
                        }
                        
                        return {
                            role: log.role.toLowerCase() as 'user' | 'assistant',
                            content: log.content,
                            timestamp,
                            date,
                            time
                        };
                    });
                    
                    // Group messages by date
                    const grouped: { [date: string]: ChatMessage[] } = {};
                    transformedMessages.forEach(msg => {
                        const msgDate = msg.date || new Date().toISOString().split('T')[0];
                        if (!grouped[msgDate]) {
                            grouped[msgDate] = [];
                        }
                        grouped[msgDate].push(msg);
                    });
                    
                    setGroupedMessages(grouped);
                    setMessages(transformedMessages);
                    console.log(`Loaded ${transformedMessages.length} messages from chatlogs`);
                } else {
                    console.warn('No chatlogs found or invalid format');
                }
            } catch (error) {
                console.error('Error loading chat history:', error);
                toast.error('Failed to load chat history');
            } finally {
                setIsLoadingHistory(false);
            }
        };
        
        loadChatHistory();
    }, []); // Load once on mount

    // Scroll detection for sticky date popup
    useEffect(() => {
        const container = messagesContainerRef.current;
        if (!container) return;
        
        const handleScroll = () => {
            const scrollTop = container.scrollTop;
            const isScrolled = scrollTop > 100;
            
            if (isScrolled) {
                // Find which date section is currently visible
                const dateHeaders = container.querySelectorAll('[data-date-header]');
                let currentDate = null;
                
                dateHeaders.forEach((header) => {
                    const rect = header.getBoundingClientRect();
                    const containerRect = container.getBoundingClientRect();
                    
                    if (rect.top <= containerRect.top + 100) {
                        currentDate = header.getAttribute('data-date-header');
                    }
                });
                
                if (currentDate && currentDate !== currentDateHeader) {
                    setCurrentDateHeader(currentDate);
                    setShowDatePopup(true);
                    
                    // Auto-hide after 2 seconds
                    setTimeout(() => setShowDatePopup(false), 2000);
                }
            } else {
                setShowDatePopup(false);
            }
        };
        
        container.addEventListener('scroll', handleScroll);
        return () => container.removeEventListener('scroll', handleScroll);
    }, [currentDateHeader]);

    // Scroll to bottom when messages update
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Sync grouped messages when messages array changes from WebSocket
    useEffect(() => {
        if (messages.length > 0 && Object.keys(groupedMessages).length > 0) {
            // Re-group messages to include new ones from WebSocket
            const grouped: { [date: string]: ChatMessage[] } = {};
            messages.forEach(msg => {
                const chatMsg = msg as ChatMessage;
                let msgDate: string;
                
                try {
                    // Try to use existing date or parse from timestamp
                    if (chatMsg.date) {
                        msgDate = chatMsg.date;
                    } else {
                        const dateObj = new Date(msg.timestamp * 1000);
                        if (isNaN(dateObj.getTime())) {
                            msgDate = new Date().toISOString().split('T')[0];
                        } else {
                            msgDate = dateObj.toISOString().split('T')[0];
                        }
                    }
                } catch (error) {
                    msgDate = new Date().toISOString().split('T')[0];
                }
                
                // Ensure msgDate is always a valid string
                const safeMsgDate = msgDate || new Date().toISOString().split('T')[0];
                
                if (!grouped[safeMsgDate]) {
                    grouped[safeMsgDate] = [];
                }
                grouped[safeMsgDate].push(chatMsg);
            });
            setGroupedMessages(grouped);
        }
    }, [messages]);

    // Background particle effect (optional)
    useEffect(() => {
        const canvas = canvasRef.current; if (!canvas) return; const ctx = canvas.getContext("2d"); if (!ctx) return;
        canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; let particles: Particle[] = [];
        const initParticles = () => { particles = []; for (let i = 0; i < 30; i++) { particles.push(new Particle(canvas.width, canvas.height, resolvedTheme || 'light')) } }; // Reduced particle count
        initParticles(); let animationFrameId: number;
        const animate = () => { if (!ctx || !canvas) return; ctx.clearRect(0, 0, canvas.width, canvas.height); for (const p of particles) { p.update(); p.draw(ctx); } animationFrameId = requestAnimationFrame(animate); };
        animate();
        const handleResize = () => { if (!canvas || !ctx) return; canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; initParticles(); };
        window.addEventListener("resize", handleResize);
        return () => { window.removeEventListener("resize", handleResize); cancelAnimationFrame(animationFrameId); };
    }, [resolvedTheme]);

    // Handle sending a text message from the input field
    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        const trimmedInput = input.trim();
        if (!trimmedInput || !isConnected) return;

        console.log("Sending chat message:", trimmedInput);
        
        // Optimistic update - add message immediately for instant feedback
        const timestamp = Date.now() / 1000;
        const date = new Date().toISOString().split('T')[0];
        const time = new Date().toTimeString().split(' ')[0];
        
        const optimisticMessage: ChatMessage = {
            role: 'user' as const,
            content: trimmedInput,
            timestamp,
            date,
            time
        };
        
        // Add to store immediately
        useJarvisStore.getState().addMessage(optimisticMessage);
        
        // Update grouped messages
        setGroupedMessages(prev => {
            const updated = { ...prev };
            if (!updated[date]) {
                updated[date] = [];
            }
            updated[date].push(optimisticMessage);
            return updated;
        });
        
        // Send message via WebSocket
        send({
            type: "send_message",
            payload: { message: trimmedInput }
        });

        setInput(''); // Clear input field immediately
    };

    // Handle Mic Toggle button click - Use REST API for speed and reliability
    // PERMANENT SOLUTION: Uses fast REST API as primary method with WebSocket fallback
    // - Optimistic UI update for instant feedback
    // - Backend verification ensures state is actually changed
    // - Automatic fallback to WebSocket if REST fails
    // - Toast notifications confirm success/failure
    const handleMicToggle = async () => {
        console.log('Mic toggle clicked. isConnected:', isConnected, 'isMuted:', isMuted);
        
        const newMutedState = !isMuted;
        console.log(`Toggling mic: ${isMuted ? 'MUTED' : 'UNMUTED'} -> ${newMutedState ? 'MUTED' : 'UNMUTED'}`);
        
        // Optimistically update UI immediately
        setIsMuted(newMutedState);
        
        try {
            // Use Next.js API route for reliability (same-origin)
            const response = await fetch('/api/mic-state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_muted: newMutedState })
            });
            
            const result = await response.json();
            
            if (result.success && result.verified) {
                // State verified on backend
                console.log('Mic state verified on backend:', result.is_muted);
                toast.success(newMutedState ? '🔇 Mic muted' : '🎤 Mic active');
            } else {
                // Verification failed - revert to actual state
                console.error('Mic state verification failed:', result);
                setIsMuted(result.is_muted);
                toast.error('Mic toggle failed', {
                    description: 'State verification failed, please try again'
                });
            }
        } catch (error) {
            console.error('Error toggling mic via REST:', error);
            
            // Fallback to WebSocket if REST fails
            if (isConnected) {
                console.log('Falling back to WebSocket for mic toggle');
                send({ type: "toggle_mic", payload: { is_muted: newMutedState } });
            } else {
                // Revert optimistic update
                setIsMuted(!newMutedState);
                toast.error("Cannot toggle mic", { 
                    description: "Backend not responding. Check connection." 
                });
            }
        }
    };

    // Handle Stop button click - ONLY works when unmuted AND assistant speaking
    // Uses fast REST API with validation
    const handleStop = async () => {
        // Check conditions locally first
        if (isMuted) {
            toast.error("Cannot stop", { description: "Mic is muted. Unmute to use stop." });
            return;
        }
        
        if (!isAssistantSpeaking) {
            toast.error("Cannot stop", { description: "Assistant is not speaking." });
            return;
        }
        
        try {
            // Use Next.js API route for fast stop
            const response = await fetch('/api/stop-speaking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                toast.success('🛑 Friday stopped');
            } else {
                // Backend validation failed
                if (result.reason === 'mic_muted') {
                    toast.error('Cannot stop while muted');
                } else if (result.reason === 'not_speaking') {
                    toast.error('Assistant not speaking');
                } else {
                    toast.error('Stop failed', { description: result.error });
                }
            }
        } catch (error) {
            console.error('Error stopping via REST:', error);
            
            // Fallback to WebSocket
            if (isConnected) {
                send({ type: "stop_jarvis", payload: {} });
                toast.info("Stop signal sent");
            } else {
                toast.error("Cannot stop", { description: "Backend not responding" });
            }
        }
    };

    // Handle manual reconnect button click
    const handleReconnect = () => {
        if (isReconnecting) return; // Prevent multiple clicks
        
        setIsReconnecting(true);
        reconnect();
        
        // Reset reconnecting state after 3 seconds
        setTimeout(() => {
            setIsReconnecting(false);
        }, 3000);
    };

    return (
        // Use flex-1 to fill available space within the layout
        <div className="flex-1 flex flex-col h-full relative overflow-hidden">
            {/* Background canvas */}
            <canvas ref={canvasRef} className="absolute inset-0 w-full h-full opacity-30 dark:opacity-15 pointer-events-none" />

            {/* Message display area */}
            <div 
                ref={messagesContainerRef}
                className="flex-1 flex flex-col gap-4 overflow-y-auto p-4 sm:p-6 lg:p-8 relative z-10 custom-scrollbar"
            >
                {/* Sticky date popup */}
                {showDatePopup && currentDateHeader && (
                    <div className="sticky top-4 z-50 flex justify-center pointer-events-none">
                        <div className="bg-cyan-500/90 backdrop-blur-xl border border-white/30 rounded-full px-4 py-1.5 shadow-lg animate-fade-in">
                            <p className="text-xs font-medium text-white">
                                {new Date(currentDateHeader + 'T00:00:00').toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                })}
                            </p>
                        </div>
                    </div>
                )}
                
                {isLoadingHistory ? (
                    <div className="flex items-center justify-center h-full">
                        <p className="text-slate-500 dark:text-slate-400 animate-pulse">Loading chat history...</p>
                    </div>
                ) : messages.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        <p className="text-slate-500 dark:text-slate-400">Start the conversation!</p>
                    </div>
                ) : (
                    // Render messages grouped by date
                    Object.keys(groupedMessages)
                        .sort() // Sort dates chronologically
                        .map((date) => (
                            <div key={date} data-date-header={date}>
                                <DateHeader date={date} />
                                {groupedMessages[date].map((msg, index) => (
                                    <MessageBubble key={`${date}-${index}`} message={msg} />
                                ))}
                            </div>
                        ))
                )}
                {/* Dummy div to ensure scrollIntoView works */}
                <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div className="p-4 sm:p-6 lg:p-8 relative z-10 border-t border-slate-200 dark:border-white/10">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                    {/* Input field and Send button */}
                    <div className="relative bg-white/40 dark:bg-slate-900/40 backdrop-blur-2xl border border-white/50 dark:border-white/10 rounded-2xl shadow-lg p-2 flex items-end gap-2">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isConnected ? "Ask Friday..." : "Connecting..."}
                            rows={1}
                            disabled={!isConnected} // Disable input if not connected
                            className="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 resize-none text-slate-800 dark:text-slate-100 placeholder:text-slate-500 dark:placeholder:text-slate-400 p-2 max-h-24 overflow-y-auto custom-scrollbar disabled:opacity-50"
                            onKeyDown={(e) => {
                                // Send on Enter, allow Shift+Enter for new line
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmit(e);
                                }
                            }}
                        />
                        <Button
                            type="submit"
                            size="icon"
                            disabled={!isConnected || !input.trim()} // Disable if not connected or input empty
                            className="w-10 h-10 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-white flex-shrink-0 disabled:opacity-50"
                        >
                            <Send className="w-5 h-5" />
                        </Button>
                    </div>
                     {/* Connection Status and Control buttons */}
                     <div className="flex flex-col items-center gap-3 mt-4">
                        {/* Connection Status Indicator */}
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full backdrop-blur-xl border text-xs font-medium transition-all duration-300 ${
                            isConnected
                                ? "bg-green-500/10 border-green-500/30 text-green-300"
                                : "bg-red-500/10 border-red-500/30 text-red-300"
                        }`}>
                            {isConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
                            <span>{isConnected ? "Connected" : "Disconnected"}</span>
                        </div>

                        {/* Control Buttons Row */}
                        <div className="flex items-center justify-center gap-4">
                            {/* Mic Toggle */}
                            <button
                                type="button"
                                onClick={handleMicToggle}
                                disabled={!isConnected}
                                className={`flex items-center justify-center w-12 h-12 rounded-full backdrop-blur-xl transition-all duration-300 shadow-lg border ${
                                    !isConnected
                                        ? "bg-slate-500/20 border-slate-500/30 text-slate-400 cursor-not-allowed"
                                        : isMuted
                                        ? "bg-red-500/20 border-red-500/30 text-red-300 hover:bg-red-500/40 hover:text-red-100"
                                        : "bg-slate-900/40 border-white/10 text-slate-300 hover:bg-slate-900/60 hover:text-white hover:border-white/20"
                                }`}
                                aria-label={isMuted ? "Unmute Mic" : "Mute Mic"}
                            >
                                 {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                            </button>

                            {/* Stop Button - ONLY enabled when unmuted AND assistant speaking */}
                            <button
                                type="button"
                                onClick={handleStop}
                                disabled={isMuted || !isAssistantSpeaking}
                                className={`flex items-center justify-center w-12 h-12 rounded-full backdrop-blur-xl border transition-all duration-300 shadow-lg ${
                                    isMuted || !isAssistantSpeaking
                                        ? "bg-slate-500/20 border-slate-500/30 text-slate-400 cursor-not-allowed opacity-50"
                                        : "bg-red-500/20 border-red-500/30 text-red-300 hover:bg-red-500/40 hover:text-red-100 hover:border-red-500/40"
                                }`}
                                aria-label="Stop Friday Speaking"
                                title={
                                    isMuted 
                                        ? "Unmute mic to use stop" 
                                        : !isAssistantSpeaking 
                                        ? "Friday is not speaking" 
                                        : "Stop Friday from speaking"
                                }
                            >
                                <Square className="w-5 h-5" />
                            </button>

                            {/* Manual Reconnect Button */}
                            <button
                                type="button"
                                onClick={handleReconnect}
                                disabled={isConnected || isReconnecting}
                                className={`flex items-center justify-center w-12 h-12 rounded-full backdrop-blur-xl border transition-all duration-300 shadow-lg ${
                                    isConnected
                                        ? "bg-slate-500/20 border-slate-500/30 text-slate-400 cursor-not-allowed"
                                        : isReconnecting
                                        ? "bg-cyan-500/20 border-cyan-500/30 text-cyan-300 animate-spin"
                                        : "bg-cyan-500/20 border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/40 hover:text-cyan-100"
                                }`}
                                aria-label="Reconnect to Backend"
                            >
                                <RefreshCw className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}