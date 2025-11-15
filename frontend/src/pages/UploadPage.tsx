import React, { useRef, useState } from 'react';
import { Upload, X, File, Check } from 'lucide-react';
import { UploadedFile } from '../types';

interface UploadPageProps {
  onFilesUpload: (files: File[]) => void;
  uploadedFiles: UploadedFile[];
  onDeleteFile: (fileName: string) => void;
  isLoading?: boolean;
}

const UploadPage: React.FC<UploadPageProps> = ({ onFilesUpload, uploadedFiles, onDeleteFile, isLoading = false }) => {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    const fileArray = Array.from(files);
    onFilesUpload(fileArray);
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-12 transition-all text-center cursor-pointer ${
          dragActive
            ? 'border-white bg-white/5'
            : 'border-gray-700 bg-gray-950 hover:border-gray-600'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleChange}
          className="hidden"
          accept=".txt"
        />
        
        <Upload size={48} className="mx-auto mb-4 text-gray-600" />
        <h3 className="text-lg font-semibold text-white mb-2">
          {isLoading ? 'Uploading...' : 'Drop your chat file here'}
        </h3>
        <p className="text-gray-400 mb-4">
          Upload WhatsApp chat exports (.txt files) to analyze conversations
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="px-6 py-2 bg-white text-black rounded-lg font-medium hover:bg-gray-200 disabled:opacity-50 transition-all"
        >
          {isLoading ? 'Uploading...' : 'Select Files'}
        </button>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="bg-gray-950 border border-gray-800 rounded-lg overflow-hidden">
          <div className="bg-gray-900 px-6 py-4 border-b border-gray-800">
            <h4 className="font-semibold text-white">Uploaded Files ({uploadedFiles.length})</h4>
          </div>
          <div className="divide-y divide-gray-800">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-900 transition-colors group">
                <div className="flex items-center gap-3 flex-1">
                  <File size={20} className="text-white" />
                  <div className="flex-1">
                    <p className="font-medium text-white">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {file.size} messages
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-white" />
                  <span className="px-3 py-1 bg-white/10 text-white rounded text-xs font-medium">
                    Ready
                  </span>
                  <button
                    onClick={() => onDeleteFile(file.name)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors opacity-0 group-hover:opacity-100"
                    title="Delete file"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
