// typescript
import React, { useEffect, useState, useRef, useId, createContext } from "react";
import {
  Box,
  Button,
  Container,
  Flex,
  Input,
  Stack,
  Text,
} from "@chakra-ui/react";
const apiUrl = import.meta.env.COLDBREW_FRONTEND_API_URL;

interface BrewInProgress {
  brew_id: string;
  current_flow_rate: string;
  current_weight: string;
}

type BrewContextShape = {
  brewInProgress: BrewInProgress | null;
  fetchBrewInProgress: () => Promise<void>;
  stopPolling: () => void;
};

const BrewContext = createContext<BrewContextShape>({
  brewInProgress: null,
  fetchBrewInProgress: async () => {},
  stopPolling: () => {},
});

export default function Brew() {
  const [brewInProgress, setBrewInProgress] = useState<BrewInProgress | null>(null);

  // ref to hold polling state, timeout id and abort controller
  const pollRef = useRef<{
    active: boolean;
    timeoutId: number | null;
    controller: AbortController | null;
  }>({ active: false, timeoutId: null, controller: null });

  const fetchBrewInProgress = async () => {
    // abort previous fetch if still running
    if (pollRef.current.controller) {
      try {
        pollRef.current.controller.abort();
      } catch {}
    }
    const controller = new AbortController();
    pollRef.current.controller = controller;

    try {
      const response = await fetch(`${apiUrl}/brew/status`, { signal: controller.signal });
      if (!response.ok) return;
      const data = await response.json();
      setBrewInProgress(data);
    } catch (e) {
      if ((e as any).name === "AbortError") {
        // fetch was aborted; ignore
      } else {
        console.error("fetch error", e);
      }
    } finally {
      pollRef.current.controller = null;
    }
  };

  const backgroundRefreshBrewInProgress = async () => {
    await fetchBrewInProgress();
    if (!pollRef.current.active) return;
    const id = window.setTimeout(() => backgroundRefreshBrewInProgress(), 4000);
    pollRef.current.timeoutId = id;
  };

  const startPolling = () => {
    if (pollRef.current.active) return;
    pollRef.current.active = true;
    backgroundRefreshBrewInProgress();
  };

  const stopPolling = () => {
    pollRef.current.active = false;
    if (pollRef.current.timeoutId != null) {
      clearTimeout(pollRef.current.timeoutId);
      pollRef.current.timeoutId = null;
    }
    if (pollRef.current.controller) {
      try {
        pollRef.current.controller.abort();
      } catch {}
      pollRef.current.controller = null;
    }
  };

  useEffect(() => {
    startPolling();
    return () => {
      stopPolling();
    };
    // run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <BrewContext.Provider value={{ brewInProgress, fetchBrewInProgress, stopPolling }}>
      <Container maxW="container.xl" pt="100px">
        <Stack gap={5}>
          Brew in Progress:
          <b key={brewInProgress?.brew_id}>
            [id={brewInProgress?.brew_id}] [flow_rate={brewInProgress?.current_flow_rate}] [weight={brewInProgress?.current_weight}]
          </b>
        </Stack>
        <CancelBrew />
        <StartBrew />
      </Container>
    </BrewContext.Provider>
  );
}

const CancelBrew: React.FC = () => {
  const { fetchBrewInProgress, stopPolling } = React.useContext(BrewContext);

  const cancelBrew = async () => {
    try {
      await fetch(`${apiUrl}/brew/kill`, {
        method: "POST",
      });
    } catch (e) {
      console.error("cancel failed", e);
    } finally {
      // stop polling immediately and refresh state once
      stopPolling();
      await fetchBrewInProgress();
    }
  };

  return <Button h="1.5rem" onClick={cancelBrew}>cancel_brew</Button>;
};

// typescript
function StartBrew() {
  const DEFAULT_FLOW = "0.05";
  const DEFAULT_VALVE_INTERVAL = "60";
  const DEFAULT_EPSILON = "0.08";

  const [targetFlowRate, setTargetFlowRate] = React.useState("");
  const [valveInterval, setValveInterval] = React.useState("");
  const [epsilon, setEpsilon] = React.useState("");
  const { fetchBrewInProgress } = React.useContext(BrewContext);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    // use user input when present, otherwise fall back to the placeholder defaults
    const newBrewRequest = {
      target_flow_rate: targetFlowRate.trim() || DEFAULT_FLOW,
      valve_interval: valveInterval.trim() || DEFAULT_VALVE_INTERVAL,
      epsilon: epsilon.trim() || DEFAULT_EPSILON,
    };

    try {
      await fetch(`${apiUrl}/brew/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newBrewRequest),
      });
      await fetchBrewInProgress();
    } catch (e) {
      console.error("start failed", e);
    }
  };

  const targetFlowRateInputId = useId();
  const valveIntervalInputId = useId();
  const epsilonInputId = useId();

  return (
    <Container maxW="container.xl" pt="100px">
      <form onSubmit={handleSubmit}>
        <label htmlFor={targetFlowRateInputId}>target_flow_rate:</label>
        <Input
          value={targetFlowRate}
          onChange={(e) => setTargetFlowRate(e.target.value)}
          type="text"
          id={targetFlowRateInputId}
          placeholder={DEFAULT_FLOW}
          aria-label="target_flow_rate"
        />

        <label htmlFor={valveIntervalInputId}>valve_interval:</label>
        <Input
          value={valveInterval}
          onChange={(e) => setValveInterval(e.target.value)}
          type="text"
          id={valveIntervalInputId}
          placeholder={DEFAULT_VALVE_INTERVAL}
          aria-label="valve_interval"
        />

        <label htmlFor={epsilonInputId}>epsilon:</label>
        <Input
          value={epsilon}
          onChange={(e) => setEpsilon(e.target.value)}
          type="text"
          id={epsilonInputId}
          placeholder={DEFAULT_EPSILON}
          aria-label="epsilon"
        />
        <Button type="submit">start_brew</Button>
      </form>
    </Container>
  );
}