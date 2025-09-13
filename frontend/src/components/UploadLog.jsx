// src/components/UploadLog.jsx
import { useState } from "react";

export default function UploadLog() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    if (!file) return;
    
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      
      // Get auth token from localStorage
      const token = localStorage.getItem('authToken');
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const res = await fetch("http://localhost:8000/upload-log", { 
        method: "POST", 
        body: fd,
        headers
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error('Upload failed:', error);
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="text-white">
      <h3 className="text-lg font-semibold mb-4">Upload log / stacktrace</h3>
      <form onSubmit={submit} className="space-y-4">
        <input 
          type="file" 
          accept=".txt,.log" 
          onChange={e=>setFile(e.target.files[0])} 
          className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        />
        <button 
          type="submit" 
          disabled={!file || loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-md font-medium"
        >
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      {result && (
        <div className="mt-6">
          <h4 className="text-md font-semibold mb-2">Analysis Result</h4>
          <pre className="bg-gray-900 p-4 rounded-md text-sm text-green-400 overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
