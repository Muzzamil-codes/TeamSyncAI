import React, { useRef, useState } from 'react';
import { Upload, X, File } from 'lucide-react';
import { UploadedFile } from '../types';

interface UploadPageProps {
  onFilesUpload: (files: UploadedFile[]) => void;
  uploadedFiles: UploadedFile[];
}

const UploadPage: React.FC<UploadPageProps> = ({ onFilesUpload, uploadedFiles }) => {
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files: FileList) => {
    setIsUploading(true);
    const newFiles: UploadedFile[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileType = file.name.toLowerCase().includes('whatsapp') ? 'whatsapp' : 
                       file.name.toLowerCase().includes('transcript') ? 'transcript' : 'other';
      
      newFiles.push({
        id: String(Date.now() + i),
        name: file.name,
        type: fileType,
        uploadedAt: new Date().toISOString(),
        size: file.size
      });
    }

    onFilesUpload(newFiles);
    setIsUploading(false);
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
            ? 'border-blue-500 bg-blue-500/5'
            : 'border-gray-600 bg-black-custom-800 hover:border-gray-500'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleChange}
          className="hidden"
          accept=".txt,.pdf,.doc,.docx"
        />
        
        <Upload size={48} className="mx-auto mb-4 text-gray-500" />
        <h3 className="text-lg font-semibold text-white mb-2">
          {isUploading ? 'Uploading...' : 'Drop your files here'}
        </h3>
        <p className="text-gray-400 mb-4">
          or click to browse WhatsApp chats, Google Meet transcriptions, and other documents
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 transition-all"
        >
          {isUploading ? 'Uploading...' : 'Select Files'}
        </button>
      </div>

      {/* File Instructions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold text-white mb-2">WhatsApp Chats</h4>
          <p className="text-sm text-gray-400">Export chat conversations to extract tasks and deadlines</p>
        </div>
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold text-white mb-2">Transcriptions</h4>
          <p className="text-sm text-gray-400">Upload Google Meet or Zoom transcripts for AI analysis</p>
        </div>
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold text-white mb-2">Documents</h4>
          <p className="text-sm text-gray-400">PDFs, Word docs, or any text format with relevant info</p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg overflow-hidden">
          <div className="bg-black-custom-900 px-6 py-4 border-b border-gray-700">
            <h4 className="font-semibold text-white">Uploaded Files ({uploadedFiles.length})</h4>
          </div>
          <div className="divide-y divide-gray-700">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="px-6 py-4 flex items-center justify-between hover:bg-black-custom-700 transition-colors">
                <div className="flex items-center gap-3">
                  <File size={20} className="text-blue-400" />
                  <div>
                    <p className="font-medium text-white">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(file.size / 1024).toFixed(2)} KB • {file.type}
                    </p>
                  </div>
                </div>
                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs font-medium">
                  Uploaded
                </span>
              </div>
            ))}
          </div>
          
          {uploadedFiles.length > 0 && (
            <div className="px-6 py-4 bg-black-custom-900 border-t border-gray-700">
              <button className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-all">
                Process with AI
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadPage;
