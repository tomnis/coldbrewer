export interface BrewInProgress {
  brew_id: string;
  current_flow_rate: string;
  current_weight: string;
}

export type BrewContextShape = {
  brewInProgress: BrewInProgress | null;
  isFlipped: boolean;
  fetchBrewInProgress: () => Promise<void>;
  stopPolling: () => void;
  toggleFlip: () => void;
};
