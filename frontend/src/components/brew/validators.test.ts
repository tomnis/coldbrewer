import { describe, it, expect } from 'vitest';
import {
  validateTargetFlowInput,
  validateValveIntervalInput,
  validateEpsilonInput,
  validateTargetWeightInput,
} from './validators';

describe('validateTargetFlowInput', () => {
  it('returns null for valid input in range', () => {
    expect(validateTargetFlowInput('0.05')).toBeNull();
    expect(validateTargetFlowInput('0.02')).toBeNull();
    expect(validateTargetFlowInput('0.08')).toBeNull();
  });

  it('returns null for empty input', () => {
    expect(validateTargetFlowInput('')).toBeNull();
    expect(validateTargetFlowInput('   ')).toBeNull();
  });

  it('returns error for non-numeric input', () => {
    expect(validateTargetFlowInput('abc')).toBe('target_flow_rate must be a number');
    expect(validateTargetFlowInput('abc123')).toBe('target_flow_rate must be a number');
  });

  it('returns error for out of range values', () => {
    expect(validateTargetFlowInput('0.01')).toBe('target_flow_rate must be between 0.02 and 0.08');
    expect(validateTargetFlowInput('0.09')).toBe('target_flow_rate must be between 0.02 and 0.08');
    expect(validateTargetFlowInput('-1')).toBe('target_flow_rate must be between 0.02 and 0.08');
  });

  it('trims whitespace from input', () => {
    expect(validateTargetFlowInput('  0.05  ')).toBeNull();
    expect(validateTargetFlowInput('  abc  ')).toBe('target_flow_rate must be a number');
  });
});

describe('validateValveIntervalInput', () => {
  it('returns null for valid input in range', () => {
    expect(validateValveIntervalInput('100')).toBeNull();
    expect(validateValveIntervalInput('4')).toBeNull();
    expect(validateValveIntervalInput('1024')).toBeNull();
  });

  it('returns null for empty input', () => {
    expect(validateValveIntervalInput('')).toBeNull();
    expect(validateValveIntervalInput('   ')).toBeNull();
  });

  it('returns error for non-numeric input', () => {
    expect(validateValveIntervalInput('xyz')).toBe('valve_interval must be a number');
  });

  it('returns error for out of range values', () => {
    expect(validateValveIntervalInput('3')).toBe('valve_interval must be between 4 and 1024');
    expect(validateValveIntervalInput('1025')).toBe('valve_interval must be between 4 and 1024');
    expect(validateValveIntervalInput('0')).toBe('valve_interval must be between 4 and 1024');
  });
});

describe('validateEpsilonInput', () => {
  it('returns null for valid input in range', () => {
    expect(validateEpsilonInput('1.0')).toBeNull();
    expect(validateEpsilonInput('0.001')).toBeNull();
    expect(validateEpsilonInput('3.99')).toBeNull();
  });

  it('returns null for empty input', () => {
    expect(validateEpsilonInput('')).toBeNull();
    expect(validateEpsilonInput('   ')).toBeNull();
  });

  it('returns error for non-numeric input', () => {
    expect(validateEpsilonInput('hello')).toBe('epsilon must be a number');
  });

  it('returns error for values at or below 0', () => {
    expect(validateEpsilonInput('0')).toBe('epsilon must be greater than 0.0');
    expect(validateEpsilonInput('-1')).toBe('epsilon must be greater than 0.0');
  });

  it('returns error for values at or above 4', () => {
    expect(validateEpsilonInput('4')).toBe('epsilon must be less than 4.0');
    expect(validateEpsilonInput('5')).toBe('epsilon must be less than 4.0');
  });
});

describe('validateTargetWeightInput', () => {
  it('returns null for valid input in range', () => {
    expect(validateTargetWeightInput('500')).toBeNull();
    expect(validateTargetWeightInput('1')).toBeNull();
    expect(validateTargetWeightInput('1339')).toBeNull();
  });

  it('returns null for empty input', () => {
    expect(validateTargetWeightInput('')).toBeNull();
    expect(validateTargetWeightInput('   ')).toBeNull();
  });

  it('returns error for non-numeric input', () => {
    expect(validateTargetWeightInput('abc')).toBe('target_weight must be a number');
  });

  it('returns error for values at or below 0', () => {
    expect(validateTargetWeightInput('0')).toBe('target_weight must be greater than 0');
    expect(validateTargetWeightInput('-10')).toBe('target_weight must be greater than 0');
  });

  it('returns error for values at or above 1340', () => {
    expect(validateTargetWeightInput('1340')).toBe('target_weight must be less than 1340');
    expect(validateTargetWeightInput('2000')).toBe('target_weight must be less than 1340');
  });
});
