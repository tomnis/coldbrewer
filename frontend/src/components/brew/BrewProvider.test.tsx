import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { BrewProvider, useBrewContext } from './BrewProvider';
import * as constants from './constants';

// Mock the constants module
vi.mock('./constants', () => ({
  wsUrl: vi.fn(() => 'ws://localhost:8000'),
  pauseBrew: vi.fn(),
  resumeBrew: vi.fn(),
}));

// Mock useBrewPolling
vi.mock('./useBrewPolling', () => ({
  useBrewPolling: vi.fn(() => ({
    brewInProgress: null,
    fetchBrewInProgress: vi.fn(),
    startPolling: vi.fn(),
    stopPolling: vi.fn(),
  })),
}));

import { useBrewPolling } from './useBrewPolling';

describe('BrewProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockUseBrewPolling = useBrewPolling as ReturnType<typeof vi.fn>;

  const createMockHookReturn = (overrides = {}) => ({
    brewInProgress: null,
    fetchBrewInProgress: vi.fn(),
    startPolling: vi.fn(),
    stopPolling: vi.fn(),
    ...overrides,
  });

  it('should provide default context values', async () => {
    mockUseBrewPolling.mockReturnValue(createMockHookReturn());

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.brewInProgress).toBeNull();
    });

    expect(result.current.isFlipped).toBe(false);
    expect(typeof result.current.fetchBrewInProgress).toBe('function');
    expect(typeof result.current.stopPolling).toBe('function');
    expect(typeof result.current.toggleFlip).toBe('function');
    expect(typeof result.current.handlePause).toBe('function');
    expect(typeof result.current.handleResume).toBe('function');
  });

  it('should start polling on mount', () => {
    const startPolling = vi.fn();
    mockUseBrewPolling.mockReturnValue(createMockHookReturn({ startPolling }));

    renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    expect(startPolling).toHaveBeenCalled();
  });

  it('should stop polling on unmount', () => {
    const stopPolling = vi.fn();
    mockUseBrewPolling.mockReturnValue(createMockHookReturn({ stopPolling }));

    const { unmount } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    unmount();

    expect(stopPolling).toHaveBeenCalled();
  });

  it('should set isFlipped to true when brew_state is brewing', async () => {
    const mockBrewInProgress = {
      brew_id: 'test-123',
      current_flow_rate: '0.05',
      current_weight: '100',
      target_weight: '1337',
      brew_state: 'brewing' as const,
      brew_strategy: 'default',
      time_started: new Date().toISOString(),
      time_completed: null,
      estimated_time_remaining: '120',
      error_message: null,
      valve_position: 50,
    };

    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ brewInProgress: mockBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.isFlipped).toBe(true);
    });
  });

  it('should set isFlipped to true when brew_state is paused', async () => {
    const mockBrewInProgress = {
      brew_id: 'test-123',
      current_flow_rate: '0.05',
      current_weight: '100',
      target_weight: '1337',
      brew_state: 'paused' as const,
      brew_strategy: 'default',
      time_started: new Date().toISOString(),
      time_completed: null,
      estimated_time_remaining: '120',
      error_message: null,
      valve_position: 50,
    };

    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ brewInProgress: mockBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.isFlipped).toBe(true);
    });
  });

  it('should set isFlipped to true when brew_state is error', async () => {
    const mockBrewInProgress = {
      brew_id: 'test-123',
      current_flow_rate: '0.05',
      current_weight: '100',
      target_weight: '1337',
      brew_state: 'error' as const,
      brew_strategy: 'default',
      time_started: new Date().toISOString(),
      time_completed: null,
      estimated_time_remaining: null,
      error_message: 'Test error',
      valve_position: 50,
    };

    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ brewInProgress: mockBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.isFlipped).toBe(true);
    });
  });

  it('should not set isFlipped when brew_state is idle', async () => {
    const mockBrewInProgress = {
      brew_id: 'test-123',
      current_flow_rate: null,
      current_weight: null,
      target_weight: '1337',
      brew_state: 'idle' as const,
      brew_strategy: 'default',
      time_started: new Date().toISOString(),
      time_completed: null,
      estimated_time_remaining: null,
      error_message: null,
      valve_position: null,
    };

    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ brewInProgress: mockBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.isFlipped).toBe(false);
    });
  });

  it('should not set isFlipped when brew_state is completed', async () => {
    const mockBrewInProgress = {
      brew_id: 'test-123',
      current_flow_rate: '0.05',
      current_weight: '1337',
      target_weight: '1337',
      brew_state: 'completed' as const,
      brew_strategy: 'default',
      time_started: new Date().toISOString(),
      time_completed: new Date().toISOString(),
      estimated_time_remaining: null,
      error_message: null,
      valve_position: 100,
    };

    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ brewInProgress: mockBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.isFlipped).toBe(false);
    });
  });

  it('should toggle isFlipped when toggleFlip is called', async () => {
    mockUseBrewPolling.mockReturnValue(createMockHookReturn());

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.isFlipped).toBe(false);
    });

    // Toggle on
    act(() => {
      result.current.toggleFlip();
    });

    expect(result.current.isFlipped).toBe(true);

    // Toggle off
    act(() => {
      result.current.toggleFlip();
    });

    expect(result.current.isFlipped).toBe(false);
  });

  it('should call pauseBrew and fetchBrewInProgress when handlePause is called', async () => {
    const fetchBrewInProgress = vi.fn();
    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ fetchBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await act(async () => {
      await result.current.handlePause();
    });

    expect(constants.pauseBrew).toHaveBeenCalled();
    expect(fetchBrewInProgress).toHaveBeenCalled();
  });

  it('should call resumeBrew and fetchBrewInProgress when handleResume is called', async () => {
    const fetchBrewInProgress = vi.fn();
    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ fetchBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await act(async () => {
      await result.current.handleResume();
    });

    expect(constants.resumeBrew).toHaveBeenCalled();
    expect(fetchBrewInProgress).toHaveBeenCalled();
  });

  it('should pass brewInProgress from useBrewPolling to context', async () => {
    const mockBrewInProgress = {
      brew_id: 'test-123',
      current_flow_rate: '0.05',
      current_weight: '100',
      target_weight: '1337',
      brew_state: 'brewing' as const,
      brew_strategy: 'default',
      time_started: new Date().toISOString(),
      time_completed: null,
      estimated_time_remaining: '120',
      error_message: null,
      valve_position: 50,
    };

    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ brewInProgress: mockBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await waitFor(() => {
      expect(result.current.brewInProgress).toEqual(mockBrewInProgress);
    });
  });

  it('should pass through stopPolling from useBrewPolling', () => {
    const stopPolling = vi.fn();
    mockUseBrewPolling.mockReturnValue(createMockHookReturn({ stopPolling }));

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    result.current.stopPolling();

    expect(stopPolling).toHaveBeenCalled();
  });

  it('should pass through fetchBrewInProgress from useBrewPolling', async () => {
    const fetchBrewInProgress = vi.fn();
    mockUseBrewPolling.mockReturnValue(
      createMockHookReturn({ fetchBrewInProgress })
    );

    const { result } = renderHook(() => useBrewContext(), {
      wrapper: BrewProvider,
    });

    await act(async () => {
      await result.current.fetchBrewInProgress();
    });

    expect(fetchBrewInProgress).toHaveBeenCalled();
  });
});
