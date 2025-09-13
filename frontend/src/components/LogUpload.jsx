import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { CloudArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { incidentService } from '../services/incidents';

const LogUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }

    setUploading(true);
    try {
      const result = await incidentService.uploadLogFile(file);
      toast.success(`Log file analyzed: ${result.filename}`);
      
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      
      // Reset form
      setFile(null);
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload log file');
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-medium text-white mb-4">Upload Log File for Analysis</h3>
      
      {/* Drag & Drop Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-400/10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        
        {file ? (
          <div className="space-y-2">
            <div className="flex items-center justify-center space-x-2">
              <DocumentTextIcon className="h-5 w-5 text-blue-400" />
              <span className="text-white font-medium">{file.name}</span>
            </div>
            <p className="text-sm text-gray-400">{formatFileSize(file.size)}</p>
            <button
              onClick={() => setFile(null)}
              className="text-red-400 hover:text-red-300 text-sm"
            >
              Remove file
            </button>
          </div>
        ) : (
          <div>
            <p className="text-white mb-2">
              <strong>Drop your log file here</strong> or click to browse
            </p>
            <p className="text-sm text-gray-400 mb-4">
              Supports .txt, .log files up to 10MB
            </p>
            <input
              type="file"
              onChange={handleFileChange}
              accept=".txt,.log"
              className="hidden"
              id="log-file-input"
            />
            <label
              htmlFor="log-file-input"
              className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-600 rounded-md shadow-sm text-sm font-medium text-white bg-gray-700 hover:bg-gray-600 transition-colors"
            >
              Choose File
            </label>
          </div>
        )}
      </div>

      {/* Upload Button */}
      {file && (
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <div className="animate-spin -ml-1 mr-3 h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                Analyzing...
              </>
            ) : (
              <>
                <CloudArrowUpIcon className="-ml-1 mr-2 h-4 w-4" />
                Upload & Analyze
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default LogUpload;
