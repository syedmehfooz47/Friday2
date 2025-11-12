// jarvis-ui/app/(dashboard)/_comps/CognitiveOverviewCard.tsx

"use client";

import { memo } from "react";
import { useJarvisStore } from "@/app/store/jarvisStore";
import { useWebSocket } from "@/app/providers/WebSocketProvider"; // Import WebSocket hook
import { Mic, MicOff, Square } from "lucide-react";
import { PulsingBorder } from "@paper-design/shaders-react";
import { FrostedCard } from "./ui/FrostedCard";
import { CardContent } from "@/components/ui/card";
import { toast } from "sonner";

// PulsingBorderShader component remains the same
function PulsingBorderShader(props: any) {
  return (
    <PulsingBorder
      colors={["#5800FF", "#BEECFF", "#E77EDC", "#FF4C3E"]}
      colorBack="#00000000"
      speed={1.5}
      roundness={1}
      thickness={0.05}
      softness={0.1}
      intensity={1}
      spotsPerColor={5}
      spotSize={0.1}
      pulse={0.2}
      smoke={0.5}
      smokeSize={2}
      scale={0.65}
      rotation={0}
      // frame={9161408.251009725} // Frame can be dynamic if needed
      {...props}
      style={{
        width: "100%",
        height: "100%",
        borderRadius: "0px", // Keep as 0 for the shader effect container
        backgroundImage: "radial-gradient(circle in oklab, oklab(0% 0 -.0001 / 0%) 25.22%, oklab(30.5% 0.029 -0.184) 43.89%, oklab(0% 0 -.0001 / 0%) 60.04%)",
      }}
    />
  );
}

export const CognitiveOverviewCard = memo(function CognitiveOverviewCard() {
  // Get state from Zustand store
  const { isMuted, setIsMuted, isAssistantSpeaking } = useJarvisStore();
  // Get WebSocket send function and connection status
  const { send, isConnected } = useWebSocket();

  const handleMicToggle = async () => {
    const newMutedState = !isMuted;
    
    // Optimistically update UI immediately
    setIsMuted(newMutedState);

    try {
      // Use REST API as primary method (faster and more reliable)
      const response = await fetch('http://localhost:8000/api/mic-state', {
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
      // Use REST API for fast stop
      const response = await fetch('http://localhost:8000/api/stop-speaking', {
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

  return (
    // Use the FrostedCard styling
    <FrostedCard>
      <CardContent className="p-4 sm:p-6 flex flex-col items-center justify-center">
        {/* Visualizer Section */}
        <div className="relative w-full max-w-[300px] sm:max-w-[350px] md:max-w-[400px] aspect-square flex items-center justify-center">
          {/* Background blur */}
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 blur-3xl scale-110 opacity-70 dark:opacity-50" />
          {/* Pulsing Border Shader */}
          <div className="relative w-full h-full"><PulsingBorderShader /></div>
          {/* Floating dots (optional decorative elements) */}
          <div className="absolute -top-2 -right-2 w-3 h-3 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0s" }}/>
          <div className="absolute top-1/3 -left-3 w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "1s" }}/>
          <div className="absolute bottom-1/4 -right-4 w-4 h-4 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: "2s" }}/>
        </div>

        {/* Control Buttons Section */}
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={handleMicToggle}
            disabled={!isConnected} // Disable button if not connected
            className={`flex items-center justify-center w-[3.6rem] h-[3.6rem] rounded-full backdrop-blur-xl transition-all duration-300 shadow-lg border ${
              !isConnected
                ? "bg-slate-500/20 border-slate-500/30 text-slate-400 cursor-not-allowed" // Disabled state
                : isMuted
                ? "bg-slate-900/40 border-white/10 text-slate-300 hover:bg-slate-900/60 hover:text-white hover:border-white/20" // Muted state
                : "bg-cyan-500/20 border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/40 hover:text-cyan-100" // Unmuted state
            }`}
            aria-label={isMuted ? "Unmute Mic" : "Mute Mic"}
          >
            {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
          <button
            onClick={handleStop}
            disabled={isMuted || !isAssistantSpeaking} // ONLY enabled when unmuted AND speaking
            className={`flex items-center justify-center w-[3.6rem] h-[3.6rem] rounded-full backdrop-blur-xl border transition-all duration-300 shadow-lg ${
              isMuted || !isAssistantSpeaking
                ? "bg-slate-500/20 border-slate-500/30 text-slate-400 cursor-not-allowed opacity-50" // Disabled state
                : "bg-red-500/20 border-red-500/30 text-red-300 hover:bg-red-500/40 hover:text-red-100 hover:border-red-500/40" // Active state
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
        </div>

        {/* Connection Status Indicator */}
        {!isConnected && (
          <p className="text-xs text-amber-500 mt-3 animate-pulse">Connecting...</p>
        )}
      </CardContent>
    </FrostedCard>
  );
});