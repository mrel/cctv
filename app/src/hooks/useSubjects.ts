/**
 * Hook for subject management
 */

import { useState, useCallback } from 'react';
import { subjectApi } from '@/lib/api';
import type { Subject } from '@/types';

export function useSubjects() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubjects = useCallback(async (params?: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await subjectApi.getAll(params);
      setSubjects(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  }, []);

  const searchSubjects = useCallback(async (params: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await subjectApi.search(params);
      setSubjects(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search subjects');
    } finally {
      setLoading(false);
    }
  }, []);

  const getSubject = useCallback(async (id: string) => {
    try {
      const response = await subjectApi.getById(id);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch subject');
    }
  }, []);

  const createSubject = useCallback(async (data: any) => {
    try {
      const response = await subjectApi.create(data);
      setSubjects((prev) => [...prev, response.data]);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create subject');
    }
  }, []);

  const updateSubject = useCallback(async (id: string, data: any) => {
    try {
      const response = await subjectApi.update(id, data);
      setSubjects((prev) =>
        prev.map((s) => (s.subject_id === id ? response.data : s))
      );
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to update subject');
    }
  }, []);

  const deleteSubject = useCallback(async (id: string) => {
    try {
      await subjectApi.delete(id);
      setSubjects((prev) => prev.filter((s) => s.subject_id !== id));
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to delete subject');
    }
  }, []);

  const getTimeline = useCallback(async (id: string, limit?: number) => {
    try {
      const response = await subjectApi.getTimeline(id, limit);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch timeline');
    }
  }, []);

  const searchByImage = useCallback(async (image: File, threshold?: number) => {
    try {
      const response = await subjectApi.searchByImage(image, threshold);
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to search by image');
    }
  }, []);

  return {
    subjects,
    loading,
    error,
    fetchSubjects,
    searchSubjects,
    getSubject,
    createSubject,
    updateSubject,
    deleteSubject,
    getTimeline,
    searchByImage,
  };
}
