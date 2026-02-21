import { useRef, useState, useCallback, useEffect } from "react";
import { wsUrl } from "./constants";
import { BrewInProgress, BrewError } from "./types";

// Reconnection delay settings
const RECONNECT_DELAY_MS = 1000;
const MAX_RECONNECT_DELAY_MS = 30000;

export function useBrewPolling() {
  const [brewInProgress, setBrewInProgress] = useState<BrewInProgress | null>(null);
  const [brewError, setBrewError] = useState<BrewError | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const ws = new WebSocket(`${wsUrl()}/ws/brew/status`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setBrewInProgress(data);
        
        // Check if the brew is in error state
        if (data.brew_state === "error") {
          // The error info can come from either error_message directly or from 
          // the enhanced error response format
          if (data.error) {
            // Enhanced error response from backend
            setBrewError({
              error: data.error || data.error_message || "An error occurred",
              error_detailed: data.error_detailed,
              category: data.category || "brew",
              severity: data.severity || "error",
              timestamp: data.timestamp || new Date().toISOString(),
              retryable: data.retryable ?? true,
              brew_id: data.brew_id,
              recovery_suggestion: data.recovery_suggestion,
              exception_type: data.exception_type,
            });
          } else {
            // Legacy error message format
            setBrewError({
              error: data.error_message || "An error occurred",
              category: "brew",
              severity: "error",
              timestamp: new Date().toISOString(),
              retryable: true,
              brew_id: data.brew_id,
              recovery_suggestion: "Try restarting the brew or check the system status.",
            });
          }
        } else {
          // Clear error when not in error state
          setBrewError(null);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      wsRef.current = null;
      
      // Attempt to reconnect with exponential backoff
      const delay = Math.min(
        RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts.current),
        MAX_RECONNECT_DELAY_MS
      );
      reconnectAttempts.current += 1;
      
      console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`);
      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect();
      }, delay);
    };
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    reconnectAttempts.current = 0;
  }, []);

  const startPolling = useCallback(() => {
    connect();
  }, [connect]);

  const stopPolling = useCallback(() => {
    disconnect();
    setBrewInProgress(null);
    setBrewError(null);
  }, [disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // fetchBrewInProgress is no longer needed with WebSocket - the connection handles it
  const fetchBrewInProgress = useCallback(async () => {
    // With WebSocket, we just ensure we're connected
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      connect();
    }
  }, [connect]);

  return { brewInProgress, brewError, fetchBrewInProgress, startPolling, stopPolling };
}
