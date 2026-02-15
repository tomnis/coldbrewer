export const validateTargetFlowInput = (value: string): string | null => {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const n = Number(trimmed);
  if (Number.isNaN(n)) return "target_flow_rate must be a number";
  if (n < 0.02 || n > 0.08) return "target_flow_rate must be between 0.02 and 0.08";
  return null;
};

export const validateValveIntervalInput = (value: string): string | null => {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const n = Number(trimmed);
  if (Number.isNaN(n)) return "valve_interval must be a number";
  if (n < 4 || n > 1024) return "valve_interval must be between 4 and 1024";
  return null;
};

export const validateEpsilonInput = (value: string): string | null => {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const n = Number(trimmed);
  if (Number.isNaN(n)) return "epsilon must be a number";
  if (n <= 0) return "epsilon must be greater than 0.0";
  if (n >= 4) return "epsilon must be less than 4.0";
  return null;
};

export const validateTargetWeightInput = (value: string): string | null => {
    const trimmed = value.trim();
    if (!trimmed) return null;
    const n = Number(trimmed);
    if (Number.isNaN(n)) return "target_weight must be a number";
    if (n <= 0) return "target_weight must be greater than 0";
    if (n >= 1340) return "target_weight must be less than 1340";
    return null;
};