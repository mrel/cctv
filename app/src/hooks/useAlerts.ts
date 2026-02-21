/**
 * Hook for alert management
 */

import { useState, useCallback } from 'react';
import { alertApi } from '@/lib/api';
import type { AlertRule, AlertLog } from '@/types';

export function useAlerts() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [logs, setLogs] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRules = useCallback(async (params?: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await alertApi.getRules(params);
      setRules(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch alert rules');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLogs = useCallback(async (params?: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await alertApi.getLogs(params);
      setLogs(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch alert logs');
    } finally {
      setLoading(false);
    }
  }, []);

  const createRule = useCallback(async (data: any) => {
    try {
      const response = await alertApi.createRule(data);
      setRules((prev) => [...prev, response.data]);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create rule');
    }
  }, []);

  const updateRule = useCallback(async (id: string, data: any) => {
    try {
      const response = await alertApi.updateRule(id, data);
      setRules((prev) =>
        prev.map((r) => (r.rule_id === id ? response.data : r))
      );
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to update rule');
    }
  }, []);

  const deleteRule = useCallback(async (id: string) => {
    try {
      await alertApi.deleteRule(id);
      setRules((prev) => prev.filter((r) => r.rule_id !== id));
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to delete rule');
    }
  }, []);

  const acknowledgeAlert = useCallback(async (id: string, notes?: string) => {
    try {
      const response = await alertApi.acknowledge(id, notes);
      setLogs((prev) =>
        prev.map((l) => (l.alert_id === id ? response.data : l))
      );
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to acknowledge alert');
    }
  }, []);

  const resolveAlert = useCallback(async (id: string, notes?: string) => {
    try {
      const response = await alertApi.resolve(id, notes);
      setLogs((prev) =>
        prev.map((l) => (l.alert_id === id ? response.data : l))
      );
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to resolve alert');
    }
  }, []);

  const getStats = useCallback(async () => {
    try {
      const response = await alertApi.getStats();
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch stats');
    }
  }, []);

  return {
    rules,
    logs,
    loading,
    error,
    fetchRules,
    fetchLogs,
    createRule,
    updateRule,
    deleteRule,
    acknowledgeAlert,
    resolveAlert,
    getStats,
  };
}
