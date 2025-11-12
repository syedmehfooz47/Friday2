// jarvis-ui/app/providers/WebSocketProvider.tsx
"use client";

import { createContext, useContext, useEffect, useRef, ReactNode, useCallback, useState } from 'react';
import { useJarvisStore } from '@/app/store/jarvisStore';
import { toast } from 'sonner';

interface WebSocketContextType {
    send: (message: any) => void;
    isConnected: boolean;
    reconnect: () => void;
}

const defaultContextValue: WebSocketContextType = {
    send: () => { console.warn("WebSocket not connected yet.") },
    isConnected: false,
    reconnect: () => { console.warn("WebSocket reconnect not available yet.") }
};

const WebSocketContext = createContext<WebSocketContextType>(defaultContextValue);

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }: { children: ReactNode }) => {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
    const reconnectAttemptsRef = useRef<number>(0);
    const [isConnected, setIsConnected] = useState(false);
    const messageQueueRef = useRef<any[]>([]);

    const {
        setStatus,
        setSystemMetrics,
        addMessage,
        updateLastMessage,
        setIsMuted,
        setIsAssistantSpeaking,
        setMessages,
    } = useJarvisStore();

    // Optimized send function with queue support
    const send = useCallback((message: any) => {
        console.log('WebSocket send called:', message);
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            try {
                wsRef.current.send(JSON.stringify(message));
                console.log('WebSocket message sent successfully:', message);
            } catch (error) {
                console.error("Failed to send WebSocket message:", error);
                // Queue message for retry
                messageQueueRef.current.push(message);
                toast.error("Failed to send command. Will retry.");
            }
        } else {
            console.warn('WebSocket is not connected. Queueing message:', message.type);
            // Queue message to send when reconnected
            messageQueueRef.current.push(message);
        }
    }, []);

    // Flush queued messages when connection is established
    const flushMessageQueue = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && messageQueueRef.current.length > 0) {
            console.log(`Flushing ${messageQueueRef.current.length} queued messages`);
            const queue = [...messageQueueRef.current];
            messageQueueRef.current = [];
            
            queue.forEach(msg => {
                try {
                    wsRef.current?.send(JSON.stringify(msg));
                } catch (error) {
                    console.error("Error flushing queued message:", error);
                }
            });
        }
    }, []);

    // Exponential backoff for reconnection
    const getReconnectDelay = useCallback(() => {
        const baseDelay = 1000; // 1 second
        const maxDelay = 30000; // 30 seconds
        const delay = Math.min(baseDelay * Math.pow(1.5, reconnectAttemptsRef.current), maxDelay);
        return delay;
    }, []);

    const connect = useCallback(() => {
        if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
            console.log("WebSocket already connecting or connected.");
            return;
        }

        console.log(`Attempting WebSocket connection (attempt ${reconnectAttemptsRef.current + 1})...`);
        try {
            const ws = new WebSocket('ws://localhost:8000/ws');
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('🔗 WebSocket Connected');
                setStatus("Online");
                setIsConnected(true);
                reconnectAttemptsRef.current = 0; // Reset reconnect attempts
                
                if (reconnectTimeoutRef.current) {
                    clearTimeout(reconnectTimeoutRef.current);
                    reconnectTimeoutRef.current = undefined;
                }

                // Flush any queued messages
                flushMessageQueue();

                // Setup ping interval for keep-alive
                const pingInterval = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'ping', payload: {} }));
                    } else {
                        clearInterval(pingInterval);
                    }
                }, 20000); // Ping every 20 seconds

                // Setup periodic state sync to ensure UI matches backend
                const stateSyncInterval = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'get_state', payload: {} }));
                    } else {
                        clearInterval(stateSyncInterval);
                    }
                }, 5000); // Sync state every 5 seconds

                ws.addEventListener('close', () => {
                    clearInterval(pingInterval);
                    clearInterval(stateSyncInterval);
                });

                // Request initial data immediately
                if (ws.readyState === WebSocket.OPEN) {
                    try {
                        ws.send(JSON.stringify({ type: "get_chatlogs", payload: {} }));
                        // Also request current mic state explicitly to hard-sync
                        ws.send(JSON.stringify({ type: "get_state", payload: {} }));
                    } catch (error) {
                        console.error("Failed to request chatlogs:", error);
                    }
                }
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case 'connection_established':
                            console.log('✅ Connection established', data.payload);
                            setIsMuted(data.payload.mic_state?.is_muted ?? true);
                            break;

                        case 'system_metrics':
                            setSystemMetrics(data.payload);
                            break;

                        case 'new_message':
                            addMessage(data.payload);
                            break;
                        
                        case 'new_chatlog':
                            // Handle live transcription updates
                            console.log('New chatlog received:', data.payload);
                            addMessage(data.payload);
                            break;
                        
                        case 'assistant_stream':
                            updateLastMessage(data.payload.content, false);
                            break;

                        case 'assistant_end':
                            updateLastMessage(data.payload.content, true);
                            break;

                        case 'mic_state_changed':
                            console.log('Mic state changed from server:', data.payload);
                            setIsMuted(data.payload.is_muted);
                            // Toast handled by component now
                            break;

                        case 'mic_toggled':
                            console.log('Mic toggled from server:', data.payload);
                            setIsMuted(data.payload.is_muted);
                            // Toast handled by component now
                            break;

                        case 'state_response':
                            console.log('Mic state sync from server:', data.payload);
                            setIsMuted(!!data.payload.is_muted);
                            break;

                        case 'assistant_speaking_changed':
                            console.log('Assistant speaking state changed:', data.payload);
                            setIsAssistantSpeaking(data.payload.is_speaking);
                            break;

                        case 'mic_toggle_failed':
                            console.warn('Mic toggle failed from server:', data.payload);
                            toast.error('Mic toggle failed', {
                                description: data.payload?.error || 'Please try again.'
                            });
                            // Re-sync state after failure
                            try {
                                wsRef.current?.send(JSON.stringify({ type: 'get_state', payload: {} }));
                            } catch {}
                            break;

                        case 'jarvis_stopped_ack':
                            console.log("Jarvis stop acknowledged by server");
                            break;

                        case 'jarvis_stopped':
                            console.log("Jarvis stopped by server");
                            toast.success("Jarvis stopped");
                            break;

                        case 'new_notifications':
                            console.log("Received notifications:", data.payload.notifications);
                            window.dispatchEvent(new CustomEvent('websocket-message', { detail: data }));
                            data.payload.notifications.forEach((notification: any) => {
                                toast.info(notification.title, {
                                    description: notification.message,
                                });
                            });
                            break;

                        case 'weather_update':
                            console.log('Weather updated via WebSocket:', data.payload);
                            window.dispatchEvent(new CustomEvent('websocket-message', { detail: data }));
                            break;

                        case 'chatlogs_response':
                            console.log(`Received ${data.payload.chatlogs?.length ?? 0} chat logs`);
                            const messages = (data.payload.chatlogs || []).map((log: any) => ({
                                role: log.role?.toLowerCase() === 'user' ? 'user' : 'assistant',
                                content: log.content,
                                timestamp: new Date(log.timestamp).getTime() / 1000
                            }));
                            setMessages(messages);
                            break;

                        case 'notification':
                            toast(data.payload.title || "Notification", {
                                description: data.payload.message
                            });
                            break;

                        case 'pong':
                            // Keep-alive response, no action needed
                            break;

                        case 'setting_updated':
                            console.log("Setting updated:", data.payload);
                            toast.info(`Setting '${data.payload.key}' updated.`);
                            break;

                        case 'brightness_changed':
                            console.log("Brightness changed:", data.payload);
                            toast.success('Brightness adjusted');
                            break;

                        case 'theme_changed':
                            console.log("Theme changed:", data.payload);
                            toast.info(`Windows theme changed to ${data.payload.theme}`);
                            break;

                        case 'image_generated':
                        case 'pdf_generated':
                        case 'word_generated':
                        case 'ppt_generated':
                        case 'excel_generated':
                        case 'file_converted':
                        case 'email_sent':
                        case 'telegram_sent':
                        case 'search_results':
                        case 'app_opened':
                        case 'app_closed':
                        case 'device_controlled':
                        case 'call_initiated':
                        case 'sms_sent':
                        case 'contact_added':
                        case 'contact_found':
                        case 'screenshot_taken':
                        case 'memory_recalled':
                            // Dispatch these as custom events for specific components to handle
                            window.dispatchEvent(new CustomEvent('websocket-message', { detail: data }));
                            // Also show toast for user feedback
                            toast.success(data.type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()));
                            break;

                        case 'error':
                            console.error('Server error:', data.payload);
                            toast.error(`Error: ${data.payload.message}`);
                            break;

                        default:
                            console.warn("Received unknown WebSocket message type:", data.type);
                            window.dispatchEvent(new CustomEvent('websocket-message', { detail: data }));
                    }
                } catch (err) {
                    console.error('Error parsing WebSocket message:', err, "Raw data:", event.data);
                }
            };

            ws.onclose = (event) => {
                console.log(`❌ WebSocket Disconnected. Code: ${event.code}, Reason: ${event.reason}`);
                setStatus("Offline");
                setIsConnected(false);
                wsRef.current = null;

                // Auto-reconnect with exponential backoff
                if (event.code !== 1000) {
                    reconnectAttemptsRef.current += 1;
                    const delay = getReconnectDelay();
                    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})...`);
                    
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, delay);
                }
            };

            ws.onerror = (error) => {
                console.warn('⚠️ WebSocket connection error (backend may not be running)');
                setStatus("Error - Backend not responding");
                // Connection will be closed, which triggers onclose and reconnect
            };

        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
            setStatus("Error");
            setIsConnected(false);
            
            // Retry connection
            reconnectAttemptsRef.current += 1;
            const delay = getReconnectDelay();
            
            if (!reconnectTimeoutRef.current) {
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log(`🔄 Retrying connection in ${delay}ms...`);
                    connect();
                }, delay);
            }
        }
    }, [setStatus, setSystemMetrics, addMessage, updateLastMessage, setIsMuted, setMessages, flushMessageQueue, getReconnectDelay]);

    // Manual reconnect function for user-triggered reconnection
    const manualReconnect = useCallback(() => {
        console.log("Manual reconnect triggered by user");
        
        // Close existing connection if any
        if (wsRef.current) {
            wsRef.current.close(1000, "Manual reconnect");
            wsRef.current = null;
        }
        
        // Clear any pending reconnect timeout
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = undefined;
        }
        
        // Reset reconnect attempts for fresh start
        reconnectAttemptsRef.current = 0;
        
        // Show toast notification
        toast.info("Reconnecting to backend...");
        
        // Attempt reconnection
        connect();
    }, [connect]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                console.log("Closing WebSocket connection on component unmount.");
                wsRef.current.close(1000, "Component unmounted");
                wsRef.current = null;
            }
        };
    }, [connect]);

    const contextValue = { send, isConnected, reconnect: manualReconnect };
    
    console.log('WebSocketProvider context value:', contextValue);

    return (
        <WebSocketContext.Provider value={contextValue}>
            {children}
        </WebSocketContext.Provider>
    );
};