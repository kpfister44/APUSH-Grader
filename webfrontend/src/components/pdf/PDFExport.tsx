/**
 * PDF Export Component
 * Provides export button and handles PDF generation/download
 */
import React, { useState } from 'react';
import { pdf } from '@react-pdf/renderer';
import { GradingResponse, EssayType, SAQType } from '../../types/api';
import { PDFDocument } from './PDFDocument';

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
}

export const PDFExport: React.FC<PDFExportProps> = ({
  result,
  essayType,
  prompt,
  essayText,
  saqParts,
  saqType
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>('');

  // Generate filename with current date
  const generateFilename = (): string => {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
    return `APUSH_Grade_${essayType}_${date}.pdf`;
  };

  // Handle PDF export
  const handleExport = async () => {
    setIsGenerating(true);
    setError('');

    try {
      // Create PDF document
      const pdfDoc = (
        <PDFDocument
          result={result}
          essayType={essayType}
          prompt={prompt}
          essayText={essayText}
          saqParts={saqParts}
          saqType={saqType}
        />
      );

      // Generate PDF blob
      const blob = await pdf(pdfDoc).toBlob();
      
      // Create download link and trigger download
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = generateFilename();
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

    } catch (err: any) {
      console.error('PDF generation failed:', err);
      setError('Failed to generate PDF. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        onClick={handleExport}
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
        {isGenerating ? (
          <>
            {/* Spinner */}
            <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin"></div>
            <span>Generating PDF...</span>
          </>
        ) : (
          <>
            <span>Export to PDF</span>
          </>
        )}
      </button>

      {/* Error message */}
      {error && (
        <div className="text-red-600 text-sm flex items-center gap-2">
          <span className="text-red-500">⚠</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};