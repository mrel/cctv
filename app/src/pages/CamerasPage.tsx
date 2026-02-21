/**
 * Cameras Page - Camera management
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Video, MoreVertical, Trash2, Edit } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useCameras } from '@/hooks/useCameras';
import { toast } from 'sonner';

export function CamerasPage() {
  const navigate = useNavigate();
  const { cameras, loading, fetchCameras, createCamera, deleteCamera } = useCameras();
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newCamera, setNewCamera] = useState({
    name: '',
    rtsp_url: '',
    location: '',
  });

  useEffect(() => {
    fetchCameras();
  }, []);

  const handleAddCamera = async () => {
    try {
      await createCamera(newCamera);
      setIsAddDialogOpen(false);
      setNewCamera({ name: '', rtsp_url: '', location: '' });
      toast.success('Camera added successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add camera');
    }
  };

  const handleDeleteCamera = async (id: string) => {
    if (!confirm('Are you sure you want to delete this camera?')) return;
    
    try {
      await deleteCamera(id);
      toast.success('Camera deleted successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete camera');
    }
  };

  const filteredCameras = cameras.filter(
    (c) =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.location?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'disconnected':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Cameras</h2>
          <p className="text-muted-foreground">
            Manage surveillance cameras and stream configuration
          </p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Camera
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Camera</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label htmlFor="name">Camera Name</Label>
                <Input
                  id="name"
                  value={newCamera.name}
                  onChange={(e) => setNewCamera({ ...newCamera, name: e.target.value })}
                  placeholder="e.g., Main Entrance"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rtsp_url">RTSP URL</Label>
                <Input
                  id="rtsp_url"
                  value={newCamera.rtsp_url}
                  onChange={(e) => setNewCamera({ ...newCamera, rtsp_url: e.target.value })}
                  placeholder="rtsp://username:password@ip:554/stream"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={newCamera.location}
                  onChange={(e) => setNewCamera({ ...newCamera, location: e.target.value })}
                  placeholder="e.g., Building A - Floor 1"
                />
              </div>
              <Button onClick={handleAddCamera} className="w-full">
                Add Camera
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search cameras..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Cameras Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredCameras.map((camera) => (
          <Card key={camera.camera_id}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`h-10 w-10 rounded-full flex items-center justify-center ${getHealthColor(camera.health_status)}`}>
                    <Video className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{camera.name}</CardTitle>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      {camera.location || 'No location'}
                    </div>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => navigate(`/cameras/${camera.camera_id}`)}>
                      <Edit className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleDeleteCamera(camera.camera_id)}>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant={camera.is_active ? 'default' : 'secondary'}>
                    {camera.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                  <Badge variant="outline">{camera.health_status}</Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  {camera.stream_config?.resolution} @ {camera.stream_config?.fps}fps
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCameras.length === 0 && !loading && (
        <div className="text-center py-12">
          <Video className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium">No cameras found</h3>
          <p className="text-muted-foreground">
            Add your first camera to start monitoring
          </p>
        </div>
      )}
    </div>
  );
}
