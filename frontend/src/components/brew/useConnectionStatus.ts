import { useRef, useState, useCallback, useEffect } from "react";
import { healthWsUrl } from "./constants";

// Reconnection delay settings
const RECONNECT_DELAY_MS = 1000;
const MAX_RECONNECT_DELAY_MS = 30000;

// Types for component health status
export interface ComponentHealth {
  connected: boolean;
  battery_pct?: number | null;
  weight?: number | null;
  units?: string | null;
}

export interface ValveHealth {
  available: boolean;
  position?: number | null;
}

export interface InfluxDBHealth {
  connected: boolean;
  error?: string | null;
}

export interface ConnectionStatus {
  scale: ComponentHealth;
  valve: ValveHealth;
  influxdb: InfluxDBHealth;
  timestamp?: string;
}

export type ConnectionState = "connected" | "reconnecting" | "disconnected";

export interface UseConnectionStatusResult {
  connectionStatus: ConnectionStatus | null;
  connectionState: ConnectionState;
  startPolling: () => void;
  stopPolling: () => void;
}

export function useConnectionStatus(): UseConnectionStatusResult {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const ws = new WebSocket(healthWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Health WebSocket connected");
      setConnectionState("connected");
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setConnectionStatus(data);
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onerror = (error) => {
      console.error("Health WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("Health WebSocket disconnected");
      wsRef.current = null;
      setConnectionState("reconnecting");
      
      // Attempt to reconnect with exponential backoff
      const delay = Math.min(
        RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts.current),
        MAX_RECONNECT_DELAY_MS
      );
      reconnectAttempts.current += 1;
      
      console.log(`Reconnecting health in ${delay}ms (attempt ${reconnectAttempts.current})`);
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
    setConnectionState("disconnected");
  }, []);

  const startPolling = useCallback(() => {
    connect();
  }, [connect]);

  const stopPolling = useCallback(() => {
    disconnect();
    setConnectionStatus(null);
  }, [disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { connectionStatus, connectionState, startPolling, stopPolling };
}
