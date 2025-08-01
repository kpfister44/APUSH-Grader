/**
 * PDF Results Page Component - Page 1 of the PDF export
 * Contains grading results, scores, feedback, and suggestions
 */
import React from 'react';
import { Page, Text, View } from '@react-pdf/renderer';
import { GradingResponse, EssayType } from '../../types/api';
import { pdfStyles, getScoreColor, formatSectionTitle } from './PDFStyles';
import { PDFCustomizationOptions } from './PDFCustomizationModal';

interface PDFResultsPageProps {
  result: GradingResponse;
  essayType: EssayType;
  customization?: PDFCustomizationOptions;
}

export const PDFResultsPage: React.FC<PDFResultsPageProps> = ({
  result,
  essayType,
  customization
}) => {
  const isTeacherTemplate = customization?.feedbackType === 'teacher';
  return (
    <Page size="A4" style={pdfStyles.page}>
      {/* Page Header with Student Info */}
      {customization?.studentName && (
        <Text style={pdfStyles.pageHeader}>
          Student: {customization.studentName}
        </Text>
      )}
      <Text style={pdfStyles.pageHeader}>
        {customization?.title || 'Essay Results'}
      </Text>

      {/* Score Summary Section */}
      <View style={pdfStyles.scoreContainer}>
        <View>
          <Text style={pdfStyles.scoreText}>
            {essayType} Essay: {isTeacherTemplate ? `____/${result.max_score}` : `${result.score}/${result.max_score}`}
          </Text>
          {!isTeacherTemplate && (
            <Text style={pdfStyles.gradeText}>
              {result.performance_level}
            </Text>
          )}
          {isTeacherTemplate && (
            <Text style={pdfStyles.gradeText}>
              Grade: _______
            </Text>
          )}
        </View>
        {!isTeacherTemplate && (
          <View>
            <Text style={[pdfStyles.scoreText, { 
              color: getScoreColor(result.score, result.max_score) 
            }]}>
              {result.percentage.toFixed(1)}%
            </Text>
          </View>
        )}
      </View>

      {/* Overall Feedback */}
      <View>
        <Text style={pdfStyles.sectionHeader}>Overall Feedback</Text>
        <View style={pdfStyles.feedbackContainer}>
          {isTeacherTemplate ? (
            <View>
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
            </View>
          ) : (
            result.overall_feedback && (
              <Text style={pdfStyles.feedbackText}>
                {result.overall_feedback}
              </Text>
            )
          )}
        </View>
      </View>

      {/* Detailed Score Breakdown */}
      <Text style={pdfStyles.sectionHeader}>Detailed Score Breakdown</Text>
      
      <View style={pdfStyles.table}>
        {/* Table Header */}
        <View style={[pdfStyles.tableRow, pdfStyles.tableHeader]}>
          <View style={pdfStyles.tableColSection}>
            <Text style={pdfStyles.tableCell}>Section</Text>
          </View>
          <View style={pdfStyles.tableColScore}>
            <Text style={pdfStyles.tableCell}>Score</Text>
          </View>
          <View style={pdfStyles.tableColFeedback}>
            <Text style={pdfStyles.tableCell}>Feedback</Text>
          </View>
        </View>

        {/* Table Rows */}
        {Object.entries(result.breakdown).map(([section, details]) => (
          <View style={pdfStyles.tableRow} key={section}>
            <View style={pdfStyles.tableColSection}>
              <Text style={pdfStyles.tableCell}>
                {formatSectionTitle(section)}
              </Text>
            </View>
            <View style={pdfStyles.tableColScore}>
              <Text style={[pdfStyles.tableCell, {
                color: isTeacherTemplate ? 'black' : getScoreColor(details.score, details.max_score),
                textAlign: 'center'
              }]}>
                {isTeacherTemplate ? `____/${details.max_score}` : `${details.score}/${details.max_score}`}
              </Text>
            </View>
            <View style={pdfStyles.tableColFeedback}>
              {isTeacherTemplate ? (
                <View style={{ padding: 4, minHeight: 30, justifyContent: 'space-around' }}>
                  <View style={{ height: 10, borderBottom: '1 solid black', marginBottom: 2 }} />
                  <View style={{ height: 10, borderBottom: '1 solid black', marginBottom: 2 }} />
                </View>
              ) : (
                <View style={{ padding: 4, minHeight: 30, justifyContent: 'flex-start' }}>
                  <Text style={[pdfStyles.tableCell, { margin: 0, padding: 0, textAlign: 'left' }]}>
                    {details.feedback}
                  </Text>
                </View>
              )}
            </View>
          </View>
        ))}
      </View>

      {/* Improvement Suggestions */}
      <View>
        <Text style={pdfStyles.sectionHeader}>
          {isTeacherTemplate ? 'Comments & Suggestions' : 'Improvement Suggestions'}
        </Text>
        <View style={pdfStyles.listContainer}>
          {isTeacherTemplate ? (
            <View>
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
              <View style={{ height: 15, borderBottom: '1 solid black', marginBottom: 4 }} />
            </View>
          ) : (
            result.suggestions && result.suggestions.length > 0 && result.suggestions.map((suggestion, index) => (
              <View style={pdfStyles.listItem} key={index}>
                <Text style={pdfStyles.listBullet}>•</Text>
                <Text style={pdfStyles.listText}>{suggestion}</Text>
              </View>
            ))
          )}
        </View>
      </View>

      {/* Processing Warnings - AI Feedback Only */}
      {!isTeacherTemplate && result.warnings && result.warnings.length > 0 && (
        <View>
          <Text style={pdfStyles.sectionHeader}>Processing Notes</Text>
          <View style={pdfStyles.warningContainer}>
            {result.warnings.map((warning, index) => (
              <Text key={index} style={pdfStyles.warningText}>
                • {warning}
              </Text>
            ))}
          </View>
        </View>
      )}

      {/* Essay Statistics */}
      <View style={{ marginTop: 'auto' }}>
        <Text style={pdfStyles.sectionHeader}>Essay Statistics</Text>
        <View style={pdfStyles.feedbackContainer}>
          <Text style={pdfStyles.feedbackText}>
            Word Count: {result.word_count}
          </Text>
        </View>
      </View>

      {/* Footer */}
      <Text style={pdfStyles.footer}>
        Page 1 of 2
      </Text>
    </Page>
  );
};