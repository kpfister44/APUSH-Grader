import React, { useState, useRef } from 'react';
import { DocumentUploadResponse, ApiError } from '../../types/api';

interface DocumentUploadProps {
  onUploadSuccess: (response: DocumentUploadResponse) => void;
  onUploadError: (error: string) => void;
  disabled?: boolean;
}

interface DocumentSlot {
  file: File | null;
  preview: string | null;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  disabled = false
}) => {
  const [documents, setDocuments] = useState<DocumentSlot[]>(
    Array(7).fill(null).map(() => ({ file: null, preview: null }))
  );
  const [isUploading, setIsUploading] = useState(false);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const fileInputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const REQUIRED_COUNT = 7;
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const ALLOWED_TYPES = ['image/png'];

  const validateFile = (file: File, docNum: number): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return `Document ${docNum} must be PNG format`;
    }
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / 1024 / 1024).toFixed(2);
      return `Document ${docNum} exceeds 5MB limit (${sizeMB}MB)`;
    }
    if (file.size === 0) {
      return `Document ${docNum} is empty`;
    }
    return null;
  };

  const handleFileSelect = (index: number, file: File | null) => {
    if (!file) {
      const newDocuments = [...documents];
      newDocuments[index] = { file: null, preview: null };
      setDocuments(newDocuments);
      return;
    }

    const error = validateFile(file, index + 1);
    if (error) {
      onUploadError(error);
      return;
    }

    const preview = URL.createObjectURL(file);
    const newDocuments = [...documents];
    newDocuments[index] = { file, preview };
    setDocuments(newDocuments);
  };

  const handleDrop = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverIndex(null);

    if (disabled) return;

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(index, file);
    }
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setDragOverIndex(index);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverIndex(null);
  };

  const handleInputChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    handleFileSelect(index, file);
  };

  const handleUpload = async () => {
    const filesToUpload = documents.map(d => d.file).filter(f => f !== null) as File[];

    if (filesToUpload.length !== REQUIRED_COUNT) {
      onUploadError(`Please select all ${REQUIRED_COUNT} documents before uploading`);
      return;
    }

    setIsUploading(true);

    try {
      const { authenticatedApiService } = await import('../../services/authApi');
      const response = await authenticatedApiService.uploadDocuments(filesToUpload);
      onUploadSuccess(response);
    } catch (error) {
      if (error instanceof ApiError) {
        onUploadError(error.message);
      } else if (error instanceof Error) {
        onUploadError(error.message);
      } else {
        onUploadError('Failed to upload documents');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleClear = () => {
    documents.forEach(doc => {
      if (doc.preview) {
        URL.revokeObjectURL(doc.preview);
      }
    });
    setDocuments(Array(7).fill(null).map(() => ({ file: null, preview: null })));
    fileInputRefs.current.forEach(ref => {
      if (ref) ref.value = '';
    });
  };

  const allDocsSelected = documents.every(d => d.file !== null);
  const selectedCount = documents.filter(d => d.file !== null).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          DBQ Documents ({selectedCount}/{REQUIRED_COUNT})
        </label>
        {selectedCount > 0 && (
          <button
            type="button"
            onClick={handleClear}
            disabled={disabled || isUploading}
            className="text-xs text-gray-500 hover:text-gray-700 disabled:opacity-50"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {documents.map((doc, index) => (
          <div key={index} className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">
              Document {index + 1}
            </label>
            <div
              onDrop={(e) => handleDrop(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragLeave={handleDragLeave}
              className={`
                relative border-2 border-dashed rounded-lg p-3 transition-all cursor-pointer
                ${dragOverIndex === index
                  ? 'border-blue-400 bg-blue-50'
                  : doc.file
                  ? 'border-green-300 bg-green-50'
                  : 'border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              onClick={() => {
                if (!disabled && fileInputRefs.current[index]) {
                  fileInputRefs.current[index]?.click();
                }
              }}
            >
              <input
                ref={el => fileInputRefs.current[index] = el}
                type="file"
                accept="image/png"
                onChange={(e) => handleInputChange(index, e)}
                disabled={disabled}
                className="hidden"
                aria-label={`Upload document ${index + 1}`}
              />

              {doc.file ? (
                <div className="space-y-2">
                  {doc.preview && (
                    <img
                      src={doc.preview}
                      alt={`Document ${index + 1} preview`}
                      className="w-full h-24 object-cover rounded"
                    />
                  )}
                  <div className="text-xs text-gray-600 truncate" title={doc.file.name}>
                    {doc.file.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {(doc.file.size / 1024).toFixed(1)} KB
                  </div>
                </div>
              ) : (
                <div className="text-center py-4">
                  <svg
                    className="mx-auto h-8 w-8 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                    aria-hidden="true"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p className="mt-1 text-xs text-gray-500">
                    Click or drag PNG
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={handleUpload}
          disabled={!allDocsSelected || disabled || isUploading}
          className={`
            flex-1 py-3 px-6 rounded-lg font-medium text-sm
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-2
            ${allDocsSelected && !isUploading
              ? 'bg-orange-500 hover:bg-orange-600 text-white focus:ring-orange-500'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isUploading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Uploading...
            </span>
          ) : (
            'Upload Documents'
          )}
        </button>
      </div>

      <p className="text-xs text-gray-500">
        Upload 7 PNG images (max 5MB each). Documents will be cached for 2 hours.
      </p>
    </div>
  );
};

export default DocumentUpload;
