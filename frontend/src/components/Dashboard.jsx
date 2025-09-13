import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  ExclamationTriangleIcon, 
  ShieldCheckIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { incidentService } from '../services/incidents';
import UploadLog from './UploadLog';

const Dashboard = () => {
  const [showLogUpload, setShowLogUpload] = useState(false);
  
  const { data: incidents, isLoading, error, refetch } = useQuery(
    'incidents',
    () => incidentService.getIncidents(),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const handleLogUploadSuccess = (result) => {
    console.log('Log analysis result:', result);
    // Optionally refetch incidents or show analysis results
    refetch();
    setShowLogUpload(false);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-white text-lg">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center">
        Error loading dashboard: {error.message}
      </div>
    );
  }

  const openIncidents = incidents?.filter(i => i.status === 'open') || [];
  const investigatingIncidents = incidents?.filter(i => i.status === 'investigating') || [];
  const resolvedIncidents = incidents?.filter(i => i.status === 'resolved') || [];
  const criticalIncidents = incidents?.filter(i => i.severity === 'critical') || [];

  const stats = [
    {
      name: 'Open Incidents',
      value: openIncidents.length,
      icon: ExclamationTriangleIcon,
      color: 'text-red-400',
      bgColor: 'bg-red-400/10'
    },
    {
      name: 'Investigating',
      value: investigatingIncidents.length,
      icon: ClockIcon,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-400/10'
    },
    {
      name: 'Resolved Today',
      value: resolvedIncidents.length,
      icon: CheckCircleIcon,
      color: 'text-green-400',
      bgColor: 'bg-green-400/10'
    },
    {
      name: 'Critical',
      value: criticalIncidents.length,
      icon: ShieldCheckIcon,
      color: 'text-purple-400',
      bgColor: 'bg-purple-400/10'
    }
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-400';
      case 'high': return 'text-orange-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Security Dashboard</h1>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowLogUpload(!showLogUpload)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {showLogUpload ? 'Hide Log Upload' : 'Upload Log'}
          </button>
          <div className="text-sm text-gray-400">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-400">{stat.name}</p>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Log Upload Section */}
      {showLogUpload && (
        <div className="bg-gray-800 rounded-lg p-6">
          <UploadLog />
        </div>
      )}

      {/* Recent Incidents */}
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">Recent Incidents</h2>
          <Link 
            to="/incidents" 
            className="text-blue-400 hover:text-blue-300 text-sm font-medium"
          >
            View all →
          </Link>
        </div>
        
        {incidents && incidents.length > 0 ? (
          <div className="space-y-4">
            {incidents.slice(0, 5).map((incident) => (
              <div key={incident.id} className="border border-gray-700 rounded-lg p-4 hover:bg-gray-750 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-block w-2 h-2 rounded-full ${getStatusColor(incident.status)}`}></span>
                      <h3 className="text-white font-medium">{incident.title}</h3>
                      <span className={`text-xs px-2 py-1 rounded ${getSeverityColor(incident.severity)} bg-opacity-20`}>
                        {incident.severity}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mt-1">{incident.description}</p>
                    <div className="flex space-x-4 mt-2 text-xs text-gray-500">
                      <span>Created: {new Date(incident.created_at).toLocaleDateString()}</span>
                      {incident.source_ip && <span>IP: {incident.source_ip}</span>}
                    </div>
                  </div>
                  <Link 
                    to={`/incidents/${incident.id}`}
                    className="text-blue-400 hover:text-blue-300 text-sm"
                  >
                    View →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            No incidents found
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
