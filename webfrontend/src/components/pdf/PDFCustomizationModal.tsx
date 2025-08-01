/**
 * PDF Customization Modal Component
 * Allows users to customize PDF export settings before generation
 */
import React, { useState } from 'react';

export interface PDFCustomizationOptions {
  studentName: string;
  title: string;
  feedbackType: 'ai' | 'teacher';
}

interface PDFCustomizationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (options: PDFCustomizationOptions) => void;
  isGenerating: boolean;
}

export const PDFCustomizationModal: React.FC<PDFCustomizationModalProps> = ({
  isOpen,
  onClose,
  onExport,
  isGenerating
}) => {
  const [studentName, setStudentName] = useState('');
  const [title, setTitle] = useState('');
  const [feedbackType, setFeedbackType] = useState<'ai' | 'teacher'>('ai');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onExport({
      studentName: studentName.trim(),
      title: title.trim() || 'Essay Results',
      feedbackType
    });
  };

  const handleClose = () => {
    if (!isGenerating) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Customize PDF Export
          </h3>
          {!isGenerating && (
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <span className="sr-only">Close</span>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Student Name */}
          <div>
            <label htmlFor="studentName" className="block text-sm font-medium text-gray-700 mb-1">
              Student Name (optional)
            </label>
            <input
              type="text"
              id="studentName"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter student name"
              disabled={isGenerating}
            />
          </div>

          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              Assignment Title (optional)
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Essay Results"
              disabled={isGenerating}
            />
          </div>

          {/* Feedback Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Feedback Type
            </label>
            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  type="radio"
                  id="ai-feedback"
                  name="feedbackType"
                  value="ai"
                  checked={feedbackType === 'ai'}
                  onChange={(e) => setFeedbackType(e.target.value as 'ai' | 'teacher')}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  disabled={isGenerating}
                />
                <label htmlFor="ai-feedback" className="ml-3 block text-sm text-gray-700">
                  AI Feedback (complete results)
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="radio"
                  id="teacher-feedback"
                  name="feedbackType"
                  value="teacher"
                  checked={feedbackType === 'teacher'}
                  onChange={(e) => setFeedbackType(e.target.value as 'ai' | 'teacher')}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  disabled={isGenerating}
                />
                <label htmlFor="teacher-feedback" className="ml-3 block text-sm text-gray-700">
                  Teacher Template (blank for handwriting)
                </label>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={isGenerating}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isGenerating}
              className={`
                flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md
                transition-all duration-200 ease-out transform
                ${isGenerating
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-105 active:scale-95'
                }
              `}
            >
              {isGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <span>Export PDF</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};