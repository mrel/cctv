/**
 * Alerts Page - Alert management and monitoring
 */

import { useState, useEffect } from 'react';
import { Bell, Check, Filter, AlertTriangle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAlerts } from '@/hooks/useAlerts';
import { toast } from 'sonner';

export function AlertsPage() {
  const { logs, rules, fetchLogs, fetchRules, acknowledgeAlert, resolveAlert } = useAlerts();
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [activeTab, setActiveTab] = useState('active');

  useEffect(() => {
    fetchLogs();
    fetchRules();
  }, []);

  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledgeAlert(id);
      toast.success('Alert acknowledged');
    } catch (error: any) {
      toast.error(error.message || 'Failed to acknowledge alert');
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveAlert(id);
      toast.success('Alert resolved');
    } catch (error: any) {
      toast.error(error.message || 'Failed to resolve alert');
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'text-red-500';
    if (priority >= 5) return 'text-yellow-500';
    return 'text-blue-500';
  };

  const filteredLogs = logs.filter((log) => {
    if (activeTab === 'active') {
      return log.status === 'open' || log.status === 'acknowledged';
    }
    return filterStatus === 'all' || log.status === filterStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Alerts</h2>
          <p className="text-muted-foreground">
            Monitor and manage security alerts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-40">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Filter" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="acknowledged">Acknowledged</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="active">
            Active
            <Badge variant="secondary" className="ml-2">
              {logs.filter((l) => l.status === 'open' || l.status === 'acknowledged').length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="all">All Alerts</TabsTrigger>
          <TabsTrigger value="rules">Alert Rules</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {filteredLogs.map((alert) => (
            <Card key={alert.alert_id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className={`mt-1 ${getPriorityColor(alert.priority || 5)}`}>
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{alert.rule_name || 'Unknown Rule'}</h3>
                      <p className="text-sm text-muted-foreground">
                        {alert.camera_name} • {alert.subject_label || 'Unknown Subject'}
                      </p>
                      <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {new Date(alert.created_at).toLocaleString()}
                        {alert.age_minutes && (
                          <span>({Math.round(alert.age_minutes)} min ago)</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={alert.status === 'open' ? 'destructive' : 'secondary'}>
                      {alert.status}
                    </Badge>
                    {alert.status === 'open' && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAcknowledge(alert.alert_id)}
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Ack
                        </Button>
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => handleResolve(alert.alert_id)}
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Resolve
                        </Button>
                      </>
                    )}
                    {alert.status === 'acknowledged' && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => handleResolve(alert.alert_id)}
                      >
                        <Check className="h-4 w-4 mr-1" />
                        Resolve
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
          {filteredLogs.length === 0 && (
            <div className="text-center py-12">
              <Bell className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">No active alerts</h3>
              <p className="text-muted-foreground">All alerts have been resolved</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="all" className="space-y-4">
          {filteredLogs.map((alert) => (
            <Card key={alert.alert_id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">{alert.rule_name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {alert.camera_name} • {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Badge variant={alert.status === 'resolved' ? 'default' : 'secondary'}>
                    {alert.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="rules" className="space-y-4">
          {rules.map((rule) => (
            <Card key={rule.rule_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{rule.name}</CardTitle>
                  <Badge variant={rule.is_active ? 'default' : 'secondary'}>
                    {rule.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{rule.description}</p>
                <div className="flex items-center gap-4 mt-4">
                  <Badge variant="outline">{rule.rule_type}</Badge>
                  <span className="text-sm">Priority: {rule.priority}/10</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
