// jarvis-ui/app/store/jarvisStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware'; // Import persist middleware

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  networkStatus: number; // Represents general network activity/load
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number; // Unix timestamp (seconds)
}

// Define the shape of the store's state and actions
interface JarvisState {
  status: string; // e.g., 'Initializing...', 'Online', 'Offline', 'Error'
  isMuted: boolean; // Microphone mute state
  isAssistantSpeaking: boolean; // Whether Friday is currently speaking
  systemMetrics: SystemMetrics;
  messages: Message[]; // Chat messages
  // Define actions to update the state
  setStatus: (status: string) => void;
  setIsMuted: (muted: boolean) => void; // Action to directly set mute state
  toggleMute: () => void; // Action to toggle mute state
  setIsAssistantSpeaking: (speaking: boolean) => void; // Action to set assistant speaking state
  setSystemMetrics: (metrics: SystemMetrics) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (chunk: string, isFinal?: boolean) => void; // For streaming responses
  setMessages: (messages: Message[]) => void; // To replace all messages (e.g., on load)
}

// Create the store using zustand and persist middleware
export const useJarvisStore = create<JarvisState>()(
  persist(
    (set, get) => ({
      // Initial state
      status: 'Initializing...',
      isMuted: true, // Default to muted
      isAssistantSpeaking: false, // Default to not speaking
      systemMetrics: { cpuUsage: 0, memoryUsage: 0, networkStatus: 0 },
      messages: [],

      // --- Actions ---
      setStatus: (status) => set({ status }),

      setIsMuted: (muted) => set({ isMuted: muted }),

      // Toggle mute state - uses the current state via get()
      toggleMute: () => set((state) => ({ isMuted: !state.isMuted })),

      setIsAssistantSpeaking: (speaking) => set({ isAssistantSpeaking: speaking }),

      setSystemMetrics: (metrics) => set({ systemMetrics: metrics }),

      // Add a new message to the end of the messages array
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
      })),

      // Append a chunk to the last message if it's from the assistant,
      // otherwise create a new assistant message
      updateLastMessage: (chunk, isFinal = false) => set((state) => {
        const lastMessageIndex = state.messages.length - 1;
        if (lastMessageIndex >= 0 && state.messages[lastMessageIndex].role === 'assistant') {
          const updatedMessages = [...state.messages];
          const currentContent = updatedMessages[lastMessageIndex].content;
          
          // If it's the final message from an 'assistant_end' event, replace the content.
          // Otherwise, append the chunk for 'assistant_stream'.
          updatedMessages[lastMessageIndex] = {
            ...updatedMessages[lastMessageIndex],
            content: isFinal ? chunk : currentContent + chunk,
          };
          return { messages: updatedMessages };
        } else {
          // If there's no message or the last one isn't from the assistant,
          // create a new one. This handles the initial placeholder message.
          const newMessage: Message = {
            role: 'assistant',
            content: chunk,
            timestamp: Date.now() / 1000
          };
          return { messages: [...state.messages, newMessage] };
        }
      }),

       // Replace the entire messages array
      setMessages: (messages) => set({ messages }),
    }),
    {
      name: 'jarvis-ui-storage', // Name for the local storage item
      partialize: (state) => ({ isMuted: state.isMuted }), // Only persist the 'isMuted' state
      // Optional: use sessionStorage instead of localStorage
      // getStorage: () => sessionStorage,
    }
  )
);

// ==================== NOTIFICATIONS STORE ====================

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  timestamp: number;
  read: boolean;
  autoClose?: boolean;
  duration?: number; // in milliseconds
}

interface NotificationState {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  
  addNotification: (notification) => set((state) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      read: false,
      autoClose: notification.autoClose !== false, // Default true
      duration: notification.duration || 5000, // Default 5 seconds
    };
    
    return {
      notifications: [newNotification, ...state.notifications].slice(0, 50), // Keep max 50
    };
  }),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter((n) => n.id !== id),
  })),
  
  markAsRead: (id) => set((state) => ({
    notifications: state.notifications.map((n) =>
      n.id === id ? { ...n, read: true } : n
    ),
  })),
  
  markAllAsRead: () => set((state) => ({
    notifications: state.notifications.map((n) => ({ ...n, read: true })),
  })),
  
  clearAll: () => set({ notifications: [] }),
}));