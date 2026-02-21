/**
 * Hook for camera management
 */

import { useState, useCallback } from 'react';
import { cameraApi } from '@/lib/api';
import type { Camera } from '@/types';

export function useCameras() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCameras = useCallback(async (params?: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await cameraApi.getAll(params);
      setCameras(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch cameras');
    } finally {
      setLoading(false);
    }
  }, []);

  const getCamera = useCallback(async (id: string) => {
    try {
      const response = await cameraApi.getById(id);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch camera');
    }
  }, []);

  const createCamera = useCallback(async (data: any) => {
    try {
      const response = await cameraApi.create(data);
      setCameras((prev) => [...prev, response.data]);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create camera');
    }
  }, []);

  const updateCamera = useCallback(async (id: string, data: any) => {
    try {
      const response = await cameraApi.update(id, data);
      setCameras((prev) =>
        prev.map((c) => (c.camera_id === id ? response.data : c))
      );
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to update camera');
    }
  }, []);

  const deleteCamera = useCallback(async (id: string) => {
    try {
      await cameraApi.delete(id);
      setCameras((prev) => prev.filter((c) => c.camera_id !== id));
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to delete camera');
    }
  }, []);

  const testCamera = useCallback(async (id: string) => {
    try {
      const response = await cameraApi.test(id);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to test camera');
    }
  }, []);

  return {
    cameras,
    loading,
    error,
    fetchCameras,
    getCamera,
    createCamera,
    updateCamera,
    deleteCamera,
    testCamera,
  };
}
