/**
 * Hook for analytics data
 */

import { useState, useCallback } from 'react';
import { analyticsApi } from '@/lib/api';
import type { Statistics, HeatmapDataPoint } from '@/types';

export function useAnalytics() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await analyticsApi.getStatistics();
      setStatistics(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHeatmap = useCallback(async (params: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await analyticsApi.getHeatmap(params);
      setHeatmapData(response.data.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch heatmap');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCameraStats = useCallback(async (cameraId: string, hours?: number) => {
    try {
      const response = await analyticsApi.getCameraStats(cameraId, hours);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch camera stats');
    }
  }, []);

  const fetchMovementFlow = useCallback(async (timeFrom: string, timeTo: string) => {
    try {
      const response = await analyticsApi.getMovementFlow(timeFrom, timeTo);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch movement flow');
    }
  }, []);

  const fetchDemographics = useCallback(async (timeFrom: string, timeTo: string) => {
    try {
      const response = await analyticsApi.getDemographics(timeFrom, timeTo);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch demographics');
    }
  }, []);

  return {
    statistics,
    heatmapData,
    loading,
    error,
    fetchStatistics,
    fetchHeatmap,
    fetchCameraStats,
    fetchMovementFlow,
    fetchDemographics,
  };
}
