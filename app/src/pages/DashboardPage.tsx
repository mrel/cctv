/**
 * Dashboard Page - Overview of system status
 */

import { useEffect } from 'react';
import { Camera, Users, Bell, Activity, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCameras } from '@/hooks/useCameras';
import { useSubjects } from '@/hooks/useSubjects';
import { useAlerts } from '@/hooks/useAlerts';
import { useAnalytics } from '@/hooks/useAnalytics';

export function DashboardPage() {
  const { cameras, fetchCameras } = useCameras();
  const { subjects, fetchSubjects } = useSubjects();
  const { logs, fetchLogs } = useAlerts();
  const { statistics, fetchStatistics } = useAnalytics();

  useEffect(() => {
    fetchCameras();
    fetchSubjects();
    fetchLogs({ limit: 5 });
    fetchStatistics();
  }, []);

  const activeCameras = cameras.filter(c => c.is_active).length;
  const healthyCameras = cameras.filter(c => c.health_status === 'healthy').length;
  const openAlerts = logs.filter(l => l.status === 'open').length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Overview of your surveillance system status and activity
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cameras</CardTitle>
            <Camera className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{cameras.length}</div>
            <p className="text-xs text-muted-foreground">
              {activeCameras} active, {healthyCameras} healthy
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Subjects</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{subjects.length}</div>
            <p className="text-xs text-muted-foreground">
              {statistics?.known_subjects || 0} known, {statistics?.unknown_subjects || 0} unknown
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Alerts</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{openAlerts}</div>
            <p className="text-xs text-muted-foreground">
              {statistics?.total_alerts_24h || 0} in last 24h
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Detections (24h)</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.total_sightings_24h || 0}</div>
            <p className="text-xs text-muted-foreground">
              {statistics?.avg_detections_per_hour || 0}/hour average
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts & Camera Status */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
            <CardDescription>Latest security alerts requiring attention</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {logs.slice(0, 5).map((alert) => (
                <div key={alert.alert_id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className={`h-5 w-5 ${
                      (alert.priority || 0) >= 8 ? 'text-red-500' : 
                      (alert.priority || 0) >= 5 ? 'text-yellow-500' : 'text-blue-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium">{alert.rule_name || 'Unknown Rule'}</p>
                      <p className="text-xs text-muted-foreground">
                        {alert.camera_name} • {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Badge variant={alert.status === 'open' ? 'destructive' : 'secondary'}>
                    {alert.status}
                  </Badge>
                </div>
              ))}
              {logs.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No recent alerts
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Camera Health</CardTitle>
            <CardDescription>Status of connected cameras</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {cameras.slice(0, 5).map((camera) => (
                <div key={camera.camera_id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`h-3 w-3 rounded-full ${
                      camera.health_status === 'healthy' ? 'bg-green-500' :
                      camera.health_status === 'degraded' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium">{camera.name}</p>
                      <p className="text-xs text-muted-foreground">{camera.location}</p>
                    </div>
                  </div>
                  <Badge variant={camera.is_active ? 'default' : 'secondary'}>
                    {camera.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              ))}
              {cameras.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No cameras configured
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
