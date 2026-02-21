/**
 * Live View Page - Real-time camera monitoring
 */

import { useState, useEffect } from 'react';
import { Grid3X3, Grid2X2, Maximize2, VideoIcon, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useCameras } from '@/hooks/useCameras';

type LayoutType = '1x1' | '2x2' | '3x3';

export function LiveViewPage() {
  const { cameras, fetchCameras } = useCameras();
  const [layout, setLayout] = useState<LayoutType>('2x2');
  const [selectedCameras, setSelectedCameras] = useState<string[]>([]);

  useEffect(() => {
    fetchCameras();
  }, []);

  useEffect(() => {
    // Auto-select first cameras if none selected
    if (selectedCameras.length === 0 && cameras.length > 0) {
      const activeCameras = cameras
        .filter(c => c.is_active)
        .slice(0, layout === '1x1' ? 1 : layout === '2x2' ? 4 : 9)
        .map(c => c.camera_id);
      setSelectedCameras(activeCameras);
    }
  }, [cameras, layout]);

  const getGridClass = () => {
    switch (layout) {
      case '1x1': return 'grid-cols-1';
      case '2x2': return 'grid-cols-2';
      case '3x3': return 'grid-cols-3';
      default: return 'grid-cols-2';
    }
  };

  const handleCameraSelect = (slotIndex: number, cameraId: string) => {
    const newSelection = [...selectedCameras];
    newSelection[slotIndex] = cameraId;
    setSelectedCameras(newSelection);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Live View</h2>
          <p className="text-muted-foreground">
            Real-time monitoring of surveillance cameras
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={layout === '1x1' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setLayout('1x1')}
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Button
            variant={layout === '2x2' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setLayout('2x2')}
          >
            <Grid2X2 className="h-4 w-4" />
          </Button>
          <Button
            variant={layout === '3x3' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setLayout('3x3')}
          >
            <Grid3X3 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Camera Grid */}
      <div className={`grid ${getGridClass()} gap-4`}>
        {Array.from({ length: layout === '1x1' ? 1 : layout === '2x2' ? 4 : 9 }).map((_, index) => {
          const cameraId = selectedCameras[index];
          const camera = cameras.find(c => c.camera_id === cameraId);

          return (
            <Card key={index} className="aspect-video relative overflow-hidden bg-black">
              {/* Camera Selection */}
              <div className="absolute top-2 left-2 z-10">
                <Select
                  value={cameraId || ''}
                  onValueChange={(value) => handleCameraSelect(index, value)}
                >
                  <SelectTrigger className="w-48 bg-black/50 text-white border-white/20">
                    <SelectValue placeholder="Select camera" />
                  </SelectTrigger>
                  <SelectContent>
                    {cameras.filter(c => c.is_active).map((c) => (
                      <SelectItem key={c.camera_id} value={c.camera_id}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Camera Info */}
              {camera && (
                <div className="absolute top-2 right-2 z-10 flex items-center gap-2">
                  <Badge 
                    variant={camera.health_status === 'healthy' ? 'default' : 'destructive'}
                    className="bg-black/50"
                  >
                    {camera.health_status}
                  </Badge>
                </div>
              )}

              {/* Video Placeholder */}
              <div className="w-full h-full flex items-center justify-center">
                {camera ? (
                  <div className="text-center text-white/60">
                    <VideoIcon className="h-16 w-16 mx-auto mb-2" />
                    <p>{camera.name}</p>
                    <p className="text-sm">Stream placeholder - HLS/WebRTC integration required</p>
                  </div>
                ) : (
                  <div className="text-center text-white/40">
                    <AlertCircle className="h-12 w-12 mx-auto mb-2" />
                    <p>Select a camera</p>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
