/**
 * Main PDF Document Component
 * Combines the results page and essay page into a complete 2-page PDF
 */
import React from 'react';
import { Document } from '@react-pdf/renderer';
import { GradingResponse, EssayType, SAQType, RubricType } from '../../types/api';
import { PDFResultsPage } from './PDFResultsPage';
import { PDFEssayPage } from './PDFEssayPage';
import { PDFCustomizationOptions } from './PDFCustomizationModal';

interface PDFDocumentProps {
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
  customization?: PDFCustomizationOptions;
}

export const PDFDocument: React.FC<PDFDocumentProps> = ({
  result,
  essayType,
  prompt,
  essayText,
  saqParts,
  saqType,
  rubricType = 'college_board',
  customization
}) => {
  return (
    <Document
      title={`APUSH Grade ${essayType} ${new Date().toISOString().split('T')[0]}`}
      author="APUSH Grader"
      subject="Essay Grading Results"
      creator="APUSH Grader"
    >
      {/* Page 1: Grading Results */}
      <PDFResultsPage 
        result={result}
        essayType={essayType}
        rubricType={rubricType}
        customization={customization}
      />

      {/* Page 2: Essay Content */}
      <PDFEssayPage
        essayType={essayType}
        prompt={prompt}
        essayText={essayText}
        saqParts={saqParts}
        saqType={saqType}
        rubricType={rubricType}
      />
    </Document>
  );
};