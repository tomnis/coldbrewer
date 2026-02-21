import { Button, HStack } from "@chakra-ui/react";
import { useBrewContext } from "./BrewProvider";

export default function NudgeButtons() {
  const { brewInProgress, handleNudgeOpen, handleNudgeClose } = useBrewContext();

  // Only show during active brewing (not paused, completed, etc.)
  if (!brewInProgress || brewInProgress.brew_state !== "brewing") {
    return null;
  }

  return (
    <HStack gap={2} mt={2}>
      <Button
        className="brew-button"
        h="1.5rem"
        onClick={handleNudgeOpen}
        colorScheme="blue"
        size="sm"
      >
        Nudge Open
      </Button>
      <Button
        className="brew-button"
        h="1.5rem"
        onClick={handleNudgeClose}
        colorScheme="orange"
        size="sm"
      >
        Nudge Close
      </Button>
    </HStack>
  );
}
