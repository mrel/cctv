/**
 * Subjects Page - Person identity management
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Filter, User, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useSubjects } from '@/hooks/useSubjects';

export function SubjectsPage() {
  const navigate = useNavigate();
  const { subjects, fetchSubjects, searchSubjects } = useSubjects();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchSubjects();
  }, []);

  const handleSearch = () => {
    searchSubjects({
      query: searchQuery,
      subject_types: filterType !== 'all' ? [filterType] : undefined,
      status: filterStatus !== 'all' ? filterStatus : undefined,
    });
  };

  const getSubjectTypeColor = (type: string) => {
    switch (type) {
      case 'employee': return 'bg-blue-500';
      case 'visitor': return 'bg-green-500';
      case 'banned': return 'bg-red-500';
      case 'vip': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Subjects</h2>
          <p className="text-muted-foreground">
            Manage person identities and face recognition data
          </p>
        </div>
        <Button onClick={() => {}}>
          <Plus className="h-4 w-4 mr-2" />
          Add Subject
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search subjects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="employee">Employee</SelectItem>
            <SelectItem value="visitor">Visitor</SelectItem>
            <SelectItem value="banned">Banned</SelectItem>
            <SelectItem value="vip">VIP</SelectItem>
            <SelectItem value="unknown">Unknown</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" onClick={handleSearch}>
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Subjects Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {subjects.map((subject) => (
          <Card 
            key={subject.subject_id} 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/subjects/${subject.subject_id}`)}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className={`h-16 w-16 rounded-full flex items-center justify-center text-white text-xl font-bold ${getSubjectTypeColor(subject.subject_type)}`}>
                  {subject.label?.[0]?.toUpperCase() || '?'}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">
                    {subject.label || `Unknown-${subject.subject_id.slice(-4)}`}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline">{subject.subject_type}</Badge>
                    <Badge variant={subject.status === 'active' ? 'default' : 'secondary'}>
                      {subject.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {subject.sighting_count} sightings
                    </span>
                    {subject.last_seen && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(subject.last_seen).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {subjects.length === 0 && (
        <div className="text-center py-12">
          <User className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium">No subjects found</h3>
          <p className="text-muted-foreground">
            Try adjusting your search or filter criteria
          </p>
        </div>
      )}
    </div>
  );
}
