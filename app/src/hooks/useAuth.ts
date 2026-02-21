/**
 * Authentication hook for managing user session
 */

import { useState, useEffect, useCallback } from 'react';
import { authApi } from '@/lib/api';
import type { LoginCredentials, AuthState } from '@/types';

const AUTH_STORAGE_KEY = 'surveillance_auth';

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Load auth state from storage on mount
  useEffect(() => {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setState({
          user: parsed.user,
          token: parsed.token,
          refreshToken: parsed.refreshToken,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        setState((s) => ({ ...s, isLoading: false }));
      }
    } else {
      setState((s) => ({ ...s, isLoading: false }));
    }
  }, []);

  // Save auth state to storage
  const saveAuthState = useCallback((newState: Partial<AuthState>) => {
    setState((prev) => {
      const updated = { ...prev, ...newState };
      if (updated.isAuthenticated) {
        localStorage.setItem(
          AUTH_STORAGE_KEY,
          JSON.stringify({
            user: updated.user,
            token: updated.token,
            refreshToken: updated.refreshToken,
          })
        );
      } else {
        localStorage.removeItem(AUTH_STORAGE_KEY);
      }
      return updated;
    });
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials.username, credentials.password);
      const { access_token, refresh_token, user } = response.data;

      saveAuthState({
        user,
        token: access_token,
        refreshToken: refresh_token,
        isAuthenticated: true,
      });

      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  }, [saveAuthState]);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore logout errors
    }

    localStorage.removeItem(AUTH_STORAGE_KEY);
    setState({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  const refresh = useCallback(async () => {
    if (!state.refreshToken) return false;

    try {
      const response = await authApi.refresh(state.refreshToken);
      const { access_token, refresh_token, user } = response.data;

      saveAuthState({
        user,
        token: access_token,
        refreshToken: refresh_token,
      });

      return true;
    } catch {
      logout();
      return false;
    }
  }, [state.refreshToken, saveAuthState, logout]);

  const hasPermission = useCallback(
    (permission: string) => {
      if (!state.user) return false;

      const rolePermissions: Record<string, string[]> = {
        admin: ['*'],
        operator: [
          'cameras:read',
          'cameras:write',
          'subjects:read',
          'subjects:write',
          'sightings:read',
          'alerts:read',
          'alerts:write',
          'analytics:read',
        ],
        viewer: [
          'cameras:read',
          'subjects:read',
          'sightings:read',
          'alerts:read',
          'analytics:read',
        ],
        auditor: ['audit:read', 'reports:read'],
      };

      const permissions = rolePermissions[state.user.role] || [];
      return permissions.includes('*') || permissions.includes(permission);
    },
    [state.user]
  );

  return {
    ...state,
    login,
    logout,
    refresh,
    hasPermission,
  };
}
