/**
 * Subject Detail Page
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Camera, User, Trash2, Edit } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useSubjects } from '@/hooks/useSubjects';
import { toast } from 'sonner';

export function SubjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getSubject, getTimeline, deleteSubject } = useSubjects();
  const [subject, setSubject] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadSubject();
    }
  }, [id]);

  const loadSubject = async () => {
    try {
      const subjectData = await getSubject(id!);
      setSubject(subjectData);

      const timelineData = await getTimeline(id!, 50);
      setTimeline(timelineData.events || []);
    } catch (error: any) {
      toast.error(error.message || 'Failed to load subject');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this subject?')) return;

    try {
      await deleteSubject(id!);
      toast.success('Subject deleted');
      navigate('/subjects');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete subject');
    }
  };

  const getSubjectTypeColor = (type: string) => {
    switch (type) {
      case 'employee':
        return 'bg-blue-500';
      case 'visitor':
        return 'bg-green-500';
      case 'banned':
        return 'bg-red-500';
      case 'vip':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!subject) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium">Subject not found</h3>
        <Button onClick={() => navigate('/subjects')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Subjects
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/subjects')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">
              {subject.label || `Unknown-${subject.subject_id.slice(-4)}`}
            </h2>
            <p className="text-muted-foreground">Subject Details</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Type</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Badge className={getSubjectTypeColor(subject.subject_type)}>{subject.subject_type}</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sightings</CardTitle>
            <Camera className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{subject.sighting_count}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Seen</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-medium">
              {subject.last_seen ? new Date(subject.last_seen).toLocaleDateString() : 'Never'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="timeline">
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="images">Images</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="space-y-4">
          {timeline.map((event, index) => (
            <Card key={index}>
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <Camera className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{event.camera_name}</p>
                    <p className="text-sm text-muted-foreground">{event.location}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm">{new Date(event.detected_at).toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">
                      Confidence: {(event.detection_confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
          {timeline.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No timeline events</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="images">
          <div className="text-center py-12">
            <p className="text-muted-foreground">Images will be displayed here</p>
          </div>
        </TabsContent>

        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle>Subject Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-muted-foreground">Subject ID</Label>
                <p className="font-medium">{subject.subject_id}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Enrollment Date</Label>
                <p className="font-medium">{new Date(subject.enrollment_date).toLocaleString()}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <Badge variant={subject.status === 'active' ? 'default' : 'secondary'}>{subject.status}</Badge>
              </div>
              <div>
                <Label className="text-muted-foreground">Consent Status</Label>
                <p className="font-medium">{subject.consent_status}</p>
              </div>
              {subject.metadata && (
                <div>
                  <Label className="text-muted-foreground">Metadata</Label>
                  <pre className="mt-2 p-4 bg-muted rounded-lg text-sm">{JSON.stringify(subject.metadata, null, 2)}</pre>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

import { Label } from '@/components/ui/label';
