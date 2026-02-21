/**
 * WebSocket client for real-time updates
 */

import { io, Socket } from 'socket.io-client';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';

class WebSocketManager {
  private sockets: Map<string, Socket> = new Map();
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  connect(channel: string, token: string): Socket {
    if (this.sockets.has(channel)) {
      return this.sockets.get(channel)!;
    }

    const socket = io(`${WS_BASE_URL}/${channel}`, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    socket.on('connect', () => {
      console.log(`Connected to ${channel} WebSocket`);
    });

    socket.on('disconnect', () => {
      console.log(`Disconnected from ${channel} WebSocket`);
    });

    socket.on('error', (error) => {
      console.error(`WebSocket error on ${channel}:`, error);
    });

    // Handle incoming messages
    socket.on('message', (data) => {
      this.notifyListeners(channel, data);
    });

    this.sockets.set(channel, socket);
    return socket;
  }

  disconnect(channel: string): void {
    const socket = this.sockets.get(channel);
    if (socket) {
      socket.disconnect();
      this.sockets.delete(channel);
    }
  }

  disconnectAll(): void {
    this.sockets.forEach((socket) => socket.disconnect());
    this.sockets.clear();
  }

  subscribe(channel: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(channel)) {
      this.listeners.set(channel, new Set());
    }
    this.listeners.get(channel)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(channel)?.delete(callback);
    };
  }

  private notifyListeners(channel: string, data: any): void {
    const listeners = this.listeners.get(channel);
    if (listeners) {
      listeners.forEach((callback) => callback(data));
    }
  }

  // Specific channel helpers
  connectAlerts(token: string): Socket {
    return this.connect('alerts', token);
  }

  connectDetections(token: string, cameraId?: string): Socket {
    const channel = cameraId ? `detections?camera_id=${cameraId}` : 'detections';
    return this.connect(channel, token);
  }

  connectCameraStream(cameraId: string, token: string): Socket {
    return this.connect(`cameras/${cameraId}/stream`, token);
  }

  connectSystem(token: string): Socket {
    return this.connect('system', token);
  }
}

export const wsManager = new WebSocketManager();
export default wsManager;
