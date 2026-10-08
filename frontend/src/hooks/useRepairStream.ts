import { useState, useEffect, useCallback, useRef } from 'react';
import { RepairDetail, RepairEvent } from '../types';
import { getRepair } from '../api/client';

export function useRepairStream(repairId?: string) {
  const [repair, setRepair] = useState<RepairDetail | null>(null);
  const [events, setEvents] = useState<RepairEvent[]>([]);
  const [activeNode, setActiveNode] = useState<string>('initialize');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  const refreshData = useCallback(async () => {
    if (!repairId) return;
    try {
      const data = await getRepair(repairId);
      setRepair(data);
      setIsLoading(false);
    } catch (e: any) {
      setError(e.message);
      setIsLoading(false);
    }
  }, [repairId]);

  useEffect(() => {
    if (!repairId) return;

    refreshData();

    // Map events to active nodes
    const mapEventToNode = (eventType: string) => {
      if (eventType.includes('workspace')) return 'inspect_workspace';
      if (eventType.includes('analysis')) return 'analyze_failure';
      if (eventType.includes('coder')) return 'coder';
      if (eventType.includes('tool')) return 'execute_tools';
      if (eventType.includes('target_test')) return 'target_test';
      if (eventType.includes('regression')) return 'regression_test';
      if (eventType.includes('critic')) return 'critic';
      if (eventType.includes('retry')) return 'rollback';
      if (eventType.includes('human_review')) return 'human_escalation';
      if (eventType.includes('success')) return 'finalize_success';
      return 'route_decision';
    };

    // Establish WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/repairs/${repairId}/ws`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (msgEvent) => {
      try {
        const evt: RepairEvent = JSON.parse(msgEvent.data);
        setEvents((prev) => [...prev, evt]);
        setActiveNode(mapEventToNode(evt.event_type));

        // Refetch repair state on terminal or phase change events
        if (
          evt.event_type.includes('completed') ||
          evt.event_type.includes('success') ||
          evt.event_type.includes('failed') ||
          evt.event_type.includes('human_review') ||
          evt.event_type.includes('retry')
        ) {
          refreshData();
        }
      } catch (err) {
        console.error('Error parsing WS message:', err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (e) => {
      console.warn('WebSocket error, falling back to polling:', e);
      setIsConnected(false);
    };

    // Backup polling timer (every 2.5 seconds if active)
    const interval = setInterval(() => {
      if (repair?.status !== 'SUCCESS' && repair?.status !== 'FAILED' && repair?.status !== 'HUMAN_REVIEW') {
        refreshData();
      }
    }, 2500);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [repairId, refreshData, repair?.status]);

  return {
    repair,
    events,
    activeNode,
    isConnected,
    isLoading,
    error,
    refreshData,
  };
}
