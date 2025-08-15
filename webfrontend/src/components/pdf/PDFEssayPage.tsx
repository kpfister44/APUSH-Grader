/**
 * PDF Essay Page Component - Page 2 of the PDF export
 * Contains the original essay prompt and student's essay content
 */
import React from 'react';
import { Page, Text, View } from '@react-pdf/renderer';
import { EssayType, SAQType, RubricType } from '../../types/api';
import { pdfStyles } from './PDFStyles';

interface PDFEssayPageProps {
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

export const PDFEssayPage: React.FC<PDFEssayPageProps> = ({
  essayType,
  prompt,
  essayText,
  saqParts,
  saqType,
  rubricType = 'college_board'
}) => {
  // Helper function to format SAQ type label
  const getSAQTypeLabel = (type?: SAQType): string => {
    if (!type) return '';
    
    const labels = {
      stimulus: 'Source Analysis',
      non_stimulus: 'Content Question',
      secondary_comparison: 'Historical Comparison'
    };
    
    return labels[type] || '';
  };

  // Helper function to check if SAQ part has content
  const hasContent = (part: string): boolean => {
    return part && part.trim().length > 0;
  };

  return (
    <Page size="A4" style={pdfStyles.page}>
      {/* Page Header */}
      <Text style={pdfStyles.pageHeader}>
        Student Essay & Prompt
      </Text>

      {/* Essay Type and Prompt Section */}
      <View>
        <Text style={pdfStyles.sectionHeader}>
          Essay Prompt ({essayType}
          {essayType === 'SAQ' && saqType && ` - ${getSAQTypeLabel(saqType)}`})
        </Text>
        <View style={pdfStyles.feedbackContainer}>
          <Text style={pdfStyles.feedbackText}>
            {prompt}
          </Text>
        </View>
      </View>

      {/* Student Response Section */}
      <Text style={pdfStyles.sectionHeader}>Student Response</Text>

      {/* SAQ Multi-Part Display */}
      {essayType === 'SAQ' && saqParts && (
        <View>
          {/* Part A */}
          {hasContent(saqParts.part_a) && (
            <View style={pdfStyles.essayPart}>
              <Text style={pdfStyles.partLabel}>Part A:</Text>
              <Text style={pdfStyles.partContent}>
                {saqParts.part_a}
              </Text>
            </View>
          )}

          {/* Part B */}
          {hasContent(saqParts.part_b) && (
            <View style={pdfStyles.essayPart}>
              <Text style={pdfStyles.partLabel}>Part B:</Text>
              <Text style={pdfStyles.partContent}>
                {saqParts.part_b}
              </Text>
            </View>
          )}

          {/* Part C */}
          {hasContent(saqParts.part_c) && (
            <View style={pdfStyles.essayPart}>
              <Text style={pdfStyles.partLabel}>Part C:</Text>
              <Text style={pdfStyles.partContent}>
                {saqParts.part_c}
              </Text>
            </View>
          )}

          {/* Show message if no parts have content */}
          {!hasContent(saqParts.part_a) && 
           !hasContent(saqParts.part_b) && 
           !hasContent(saqParts.part_c) && (
            <View style={pdfStyles.warningContainer}>
              <Text style={pdfStyles.warningText}>
                No SAQ responses provided
              </Text>
            </View>
          )}
        </View>
      )}

      {/* DBQ/LEQ Full Essay Display */}
      {(essayType === 'DBQ' || essayType === 'LEQ') && (
        <View>
          {essayText && essayText.trim() ? (
            <Text style={pdfStyles.essayContent}>
              {essayText}
            </Text>
          ) : (
            <View style={pdfStyles.warningContainer}>
              <Text style={pdfStyles.warningText}>
                No essay text provided
              </Text>
            </View>
          )}
        </View>
      )}

      {/* Footer */}
      <Text style={pdfStyles.footer}>
        Page 2 of 2
      </Text>
    </Page>
  );
};