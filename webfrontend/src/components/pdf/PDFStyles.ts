/**
 * PDF styling definitions for print-friendly formatting
 * Uses traditional black/white layout optimized for 8.5x11" paper
 */
import { StyleSheet } from '@react-pdf/renderer';

export const pdfStyles = StyleSheet.create({
  // Page styles
  page: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    padding: 30,
    fontFamily: 'Times-Roman',
    fontSize: 11,
    lineHeight: 1.4,
  },

  // Header styles
  pageHeader: {
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    paddingBottom: 10,
    borderBottom: '1 solid #000000',
  },

  sectionHeader: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 8,
    color: '#000000',
  },

  subHeader: {
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 10,
    marginBottom: 5,
    color: '#000000',
  },

  // Content styles
  paragraph: {
    marginBottom: 8,
    textAlign: 'justify',
  },

  essayContent: {
    fontSize: 10,
    lineHeight: 1.3,
    marginBottom: 6,
    textAlign: 'justify',
    padding: 5,
    border: '1 solid #CCCCCC',
    backgroundColor: '#FAFAFA',
  },

  // Score and grade styles
  scoreContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    padding: 10,
    border: '1 solid #000000',
    backgroundColor: '#F5F5F5',
  },

  scoreText: {
    fontSize: 14,
    fontWeight: 'bold',
  },

  gradeText: {
    fontSize: 12,
    fontWeight: 'bold',
  },

  // Table styles for rubric breakdown
  table: {
    display: 'table' as const,
    width: 'auto',
    marginBottom: 15,
  },

  tableRow: {
    margin: 'auto',
    flexDirection: 'row',
  },

  tableHeader: {
    backgroundColor: '#E5E5E5',
    fontWeight: 'bold',
    fontSize: 10,
  },

  tableCol: {
    width: '33%',
    borderStyle: 'solid',
    borderWidth: 1,
    borderColor: '#000000',
  },

  tableColWide: {
    width: '50%',
    borderStyle: 'solid',
    borderWidth: 1,
    borderColor: '#000000',
  },

  tableColNarrow: {
    width: '15%',
    borderStyle: 'solid',
    borderWidth: 1,
    borderColor: '#000000',
  },

  tableCell: {
    margin: 'auto',
    marginTop: 5,
    marginBottom: 5,
    fontSize: 9,
    padding: 4,
  },

  // List styles
  listContainer: {
    marginBottom: 10,
  },

  listItem: {
    flexDirection: 'row',
    marginBottom: 4,
  },

  listBullet: {
    width: 10,
    fontSize: 10,
  },

  listText: {
    flex: 1,
    fontSize: 10,
    lineHeight: 1.3,
  },

  // Essay part styles (for SAQ)
  essayPart: {
    marginBottom: 12,
  },

  partLabel: {
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 4,
  },

  partContent: {
    fontSize: 10,
    lineHeight: 1.3,
    marginLeft: 15,
    textAlign: 'justify',
  },

  // Feedback styles
  feedbackContainer: {
    marginBottom: 12,
    padding: 8,
    border: '1 solid #CCCCCC',
    backgroundColor: '#F9F9F9',
  },

  feedbackText: {
    fontSize: 10,
    lineHeight: 1.3,
    textAlign: 'justify',
  },

  // Warning styles
  warningContainer: {
    marginBottom: 10,
    padding: 6,
    border: '1 solid #999999',
    backgroundColor: '#F0F0F0',
  },

  warningText: {
    fontSize: 9,
    fontStyle: 'italic',
  },

  // Page break
  pageBreak: {
    pageBreakBefore: 'always' as const,
  },

  // Footer styles
  footer: {
    position: 'absolute' as const,
    bottom: 20,
    left: 30,
    right: 30,
    textAlign: 'center',
    fontSize: 8,
    color: '#666666',
  },
});

// Color utilities for score-based styling
export const getScoreColor = (score: number, maxScore: number): string => {
  const percentage = (score / maxScore) * 100;
  
  if (percentage >= 85) return '#000000'; // Perfect - black
  if (percentage >= 70) return '#333333'; // Good - dark gray  
  if (percentage >= 50) return '#666666'; // Average - medium gray
  return '#999999'; // Below average - light gray
};

// Typography utilities
export const formatSectionTitle = (title: string): string => {
  return title
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};