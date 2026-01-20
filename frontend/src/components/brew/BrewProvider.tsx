import React, { createContext, useContext, useEffect, useState } from "react";
import { useBrewPolling } from "./useBrewPolling";
import { BrewContextShape } from "./types";

const BrewContext = createContext<BrewContextShape>({
  brewInProgress: null,
  isFlipped: false,
  fetchBrewInProgress: async () => {},
  stopPolling: () => {},
  toggleFlip: () => {},
});

export const useBrewContext = () => useContext(BrewContext);

export const BrewProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { brewInProgress, fetchBrewInProgress, startPolling, stopPolling } = useBrewPolling();
  const [isFlipped, setIsFlipped] = useState(false);

  useEffect(() => {
    startPolling();
    return () => stopPolling();
  }, [startPolling, stopPolling]);

  const toggleFlip = () => setIsFlipped(v => !v);

  return (
    <BrewContext.Provider value={{ brewInProgress, isFlipped, fetchBrewInProgress, stopPolling, toggleFlip }}>
      {children}
    </BrewContext.Provider>
  );
};
