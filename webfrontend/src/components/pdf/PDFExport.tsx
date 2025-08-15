/**
 * PDF Export Component
 * Provides export button and handles PDF generation/download
 */
import React, { useState } from 'react';
import { pdf } from '@react-pdf/renderer';
import { GradingResponse, EssayType, SAQType, RubricType } from '../../types/api';
import { PDFDocument } from './PDFDocument';
import { PDFCustomizationModal, PDFCustomizationOptions } from './PDFCustomizationModal';

interface PDFExportProps {
  result: GradingResponse;
  essayType: EssayType;
  prompt: string;
  essayText?: string;           // For DBQ/LEQ
  saqParts?: {                  // For SAQ
    part_a: string;
    part_b: string;
    part_c: string;
  };
  saqType?: SAQType;
  rubricType?: RubricType;      // For SAQ rubric type
}

export const PDFExport: React.FC<PDFExportProps> = ({
  result,
  essayType,
  prompt,
  essayText,
  saqParts,
  saqType,
  rubricType = 'college_board'
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Generate filename with customization options
  const generateFilename = (options: PDFCustomizationOptions): string => {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
    const studentPart = options.studentName ? `_${options.studentName.replace(/[^a-zA-Z0-9]/g, '_')}` : '';
    const feedbackPart = options.feedbackType === 'teacher' ? '_Template' : '';
    return `APUSH_Grade_${essayType}${studentPart}${feedbackPart}_${date}.pdf`;
  };

  // Handle PDF export with customization options
  const handleExport = async (options: PDFCustomizationOptions) => {
    setIsGenerating(true);
    setError('');

    try {
      // Create PDF document with customization options
      const pdfDoc = (
        <PDFDocument
          result={result}
          essayType={essayType}
          prompt={prompt}
          essayText={essayText}
          saqParts={saqParts}
          saqType={saqType}
          rubricType={rubricType}
          customization={options}
        />
      );

      // Generate PDF blob
      const blob = await pdf(pdfDoc).toBlob();
      
      // Create download link and trigger download
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = generateFilename(options);
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      // Close modal on success
      setIsModalOpen(false);

    } catch (err: any) {
      console.error('PDF generation failed:', err);
      setError('Failed to generate PDF. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle opening the customization modal
  const handleOpenModal = () => {
    setError('');
    setIsModalOpen(true);
  };

  return (
    <>
      <div className="flex flex-col items-start gap-2">
        <button
          onClick={handleOpenModal}
          disabled={isGenerating}
          className={`
            flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium text-sm w-full
            transition-all duration-200 ease-out transform
            ${isGenerating
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-105 active:scale-95'
            }
          `}
        >
          <span>Export to PDF</span>
        </button>

        {/* Error message */}
        {error && (
          <div className="text-red-600 text-sm flex items-center gap-2">
            <span className="text-red-500">⚠</span>
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* PDF Customization Modal */}
      <PDFCustomizationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onExport={handleExport}
        isGenerating={isGenerating}
      />
    </>
  );
};