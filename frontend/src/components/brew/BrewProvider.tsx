import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useBrewPolling } from "./useBrewPolling";
import { BrewContextShape, BrewError } from "./types";
import { pauseBrew, resumeBrew } from "./constants";

const BrewContext = createContext<BrewContextShape>({
  brewInProgress: null,
  brewError: null,
  isFlipped: false,
  fetchBrewInProgress: async () => {},
  stopPolling: () => {},
  toggleFlip: () => {},
  handlePause: async () => {},
  handleResume: async () => {},
  dismissError: () => {},
});

export const useBrewContext = () => useContext(BrewContext);

export const BrewProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { brewInProgress, brewError, fetchBrewInProgress, startPolling, stopPolling } = useBrewPolling();
  const [isFlipped, setIsFlipped] = useState(false);

  useEffect(() => {
    startPolling();
    return () => stopPolling();
  }, [startPolling, stopPolling]);

  // When brewInProgress changes, update isFlipped to show correct side of card
  useEffect(() => {
    if (brewInProgress !== null && (brewInProgress.brew_state === "brewing" || brewInProgress.brew_state === "paused" || brewInProgress.brew_state === "error")) {
      setIsFlipped(true);
    }
  }, [brewInProgress]);

  const toggleFlip = () => setIsFlipped(v => !v);

  const handlePause = useCallback(async () => {
    await pauseBrew();
    await fetchBrewInProgress();
  }, [fetchBrewInProgress]);

  const handleResume = useCallback(async () => {
    await resumeBrew();
    await fetchBrewInProgress();
  }, [fetchBrewInProgress]);

  const dismissError = useCallback(() => {
    // Error is managed by useBrewPolling, so this is a no-op
    // The error will be cleared when the brew state changes
  }, []);

  return (
    <BrewContext.Provider value={{ 
      brewInProgress, 
      brewError,
      isFlipped, 
      fetchBrewInProgress, 
      stopPolling, 
      toggleFlip, 
      handlePause, 
      handleResume,
      dismissError 
    }}>
      {children}
    </BrewContext.Provider>
  );
};
