import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { incidentService } from '../services/incidents';

const IncidentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [newStatus, setNewStatus] = useState('');

  const { data: incident, isLoading, error } = useQuery(
    ['incident', id],
    () => incidentService.getIncident(id),
    {
      enabled: !!id,
    }
  );

  const updateStatusMutation = useMutation(
    (status) => incidentService.updateIncidentStatus(id, status),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['incident', id]);
        queryClient.invalidateQueries('incidents');
        toast.success('Status updated successfully');
        setNewStatus('');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to update status');
      }
    }
  );

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-white text-lg">Loading incident...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center">
        Error loading incident: {error.message}
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="text-center text-gray-400">
        Incident not found
      </div>
    );
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-red-500';
      case 'investigating': return 'bg-yellow-500';
      case 'resolved': return 'bg-green-500';
      case 'closed': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const handleStatusUpdate = () => {
    if (newStatus && newStatus !== incident.status) {
      updateStatusMutation.mutate(newStatus);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <button
          onClick={() => navigate('/incidents')}
          className="text-blue-400 hover:text-blue-300"
        >
          ← Back to Incidents
        </button>
        <div className="text-sm text-gray-400">
          Incident #{incident.id}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">{incident.title}</h1>
            <div className="flex space-x-4">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white ${getStatusColor(incident.status)}`}>
                {incident.status}
              </span>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white ${getSeverityColor(incident.severity)}`}>
                {incident.severity}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Description</h3>
              <p className="text-white">{incident.description || 'No description provided'}</p>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Incident Type</h3>
              <p className="text-white">{incident.incident_type || 'Not specified'}</p>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Source IP</h3>
              <p className="text-white font-mono">{incident.source_ip || 'Not specified'}</p>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Target System</h3>
              <p className="text-white">{incident.target_system || 'Not specified'}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Detected At</h3>
              <p className="text-white">{new Date(incident.detected_at).toLocaleString()}</p>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Created At</h3>
              <p className="text-white">{new Date(incident.created_at).toLocaleString()}</p>
            </div>
            
            {incident.updated_at && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Last Updated</h3>
                <p className="text-white">{new Date(incident.updated_at).toLocaleString()}</p>
              </div>
            )}
            
            {incident.resolved_at && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Resolved At</h3>
                <p className="text-white">{new Date(incident.resolved_at).toLocaleString()}</p>
              </div>
            )}
          </div>
        </div>

        {/* Status Update Section */}
        <div className="border-t border-gray-700 pt-6">
          <h3 className="text-lg font-medium text-white mb-4">Update Status</h3>
          <div className="flex space-x-4 items-center">
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className="bg-gray-700 text-white rounded px-3 py-2"
            >
              <option value="">Select new status...</option>
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
            <button
              onClick={handleStatusUpdate}
              disabled={!newStatus || newStatus === incident.status || updateStatusMutation.isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded font-medium"
            >
              {updateStatusMutation.isLoading ? 'Updating...' : 'Update Status'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentDetail;
