import React, { useState } from 'react';
import { ChatLayout, Header, MainContent } from '../components/layout';
import { EssayTypeSelector, SAQTypeSelector, SAQMultiPartInput, ChatTextArea, PromptInput } from '../components/input';
import { SubmitButton, ResultsDisplay } from '../components/ui';
import { GradingProvider, useGrading } from '../contexts/GradingContext';
import { apiService } from '../services/api';
import { GradingRequest } from '../types/api';

/**
 * Inner component that uses the grading context
 */
const GradingPageContent: React.FC = () => {
  const { state, actions } = useGrading();
  const [testResults, setTestResults] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string>('');
  
  // Helper function to build GradingRequest from form state
  const buildGradingRequest = (): GradingRequest => {
    const request: GradingRequest = {
      essay_type: state.form.essayType!,
      prompt: state.form.prompt
    };
    
    if (state.form.essayType === 'SAQ') {
      request.saq_parts = state.form.saqParts;
      if (state.form.saqType) {
        request.saq_type = state.form.saqType;
      }
    } else {
      // For DBQ/LEQ, use essay_text
      request.essay_text = state.form.essayText;
    }
    
    return request;
  };
  
  // Real grading submission handler
  const handleGradingSubmit = async () => {
    setSubmitError('');
    actions.setSubmitting(true);
    
    try {
      const request = buildGradingRequest();
      const result = await apiService.gradeEssay(request);
      actions.setResult(result);
    } catch (error: any) {
      // Handle different error types with teacher-friendly messages
      let errorMessage = 'An error occurred while grading the essay.';
      
      switch (error.type) {
        case 'RATE_LIMIT_ERROR':
          errorMessage = 'Rate limit exceeded. Please wait a few minutes before submitting another essay.';
          break;
        case 'NETWORK_ERROR':
          errorMessage = 'Connection problem. Please check your internet connection and try again.';
          break;
        case 'VALIDATION_ERROR':
          errorMessage = `Validation error: ${error.message}`;
          break;
        case 'TIMEOUT_ERROR':
          errorMessage = 'Request timed out. The AI service may be busy. Please try again.';
          break;
        case 'SERVER_ERROR':
          errorMessage = 'Server error occurred. Please try again in a few moments.';
          break;
        default:
          errorMessage = `Error: ${error.message}`;
      }
      
      setSubmitError(errorMessage);
      actions.setSubmitting(false);
    }
  };

  const testHealthCheck = async () => {
    setLoading(true);
    setTestResults('Testing health check...');
    try {
      const result = await apiService.checkHealth();
      setTestResults(`✅ Health Check Success:\n${JSON.stringify(result, null, 2)}`);
    } catch (error: any) {
      setTestResults(`❌ Health Check Failed:\n${error.message}\nType: ${error.type}\nStatus: ${error.status}`);
    }
    setLoading(false);
  };

  const testUsageSummary = async () => {
    setLoading(true);
    setTestResults('Testing usage summary...');
    try {
      const result = await apiService.getUsageSummary();
      setTestResults(`✅ Usage Summary Success:\n${JSON.stringify(result, null, 2)}`);
    } catch (error: any) {
      setTestResults(`❌ Usage Summary Failed:\n${error.message}\nType: ${error.type}\nStatus: ${error.status}`);
    }
    setLoading(false);
  };

  const testGrading = async () => {
    setLoading(true);
    setTestResults('Testing SAQ grading (may take 10-15 seconds with real AI)...');
    try {
      const sampleRequest = {
        essay_type: 'SAQ' as const,
        prompt: 'Explain the main causes of the American Revolution.',
        saq_parts: {
          part_a: 'The main causes of the American Revolution included taxation without representation by the British Parliament. The colonists were particularly frustrated with acts like the Stamp Act and Sugar Act, which imposed taxes on everyday items without giving them any voice in the British government that was taxing them.',
          part_b: 'Key events like the Boston Tea Party in 1773 demonstrated growing colonial resistance to British policies. This act of defiance, where colonists dumped British tea into Boston Harbor, was a direct response to the Tea Act and showed how willing the colonists were to take action against what they saw as unfair treatment.',
          part_c: 'These mounting grievances and escalating conflicts ultimately led to the Declaration of Independence in 1776, which formally broke ties with Britain. The document outlined the colonists\' complaints and established the philosophical foundation for their right to self-governance, marking the beginning of the United States as an independent nation.'
        },
        saq_type: 'non_stimulus' as const
      };

      const result = await apiService.gradeEssay(sampleRequest);
      setTestResults(`✅ Grading Success:\nScore: ${result.score}/${result.max_score} (${result.percentage}%)\nGrade: ${result.letter_grade}\nPerformance: ${result.performance_level}\n\nFull Response:\n${JSON.stringify(result, null, 2)}`);
    } catch (error: any) {
      setTestResults(`❌ Grading Failed:\n${error.message}\nType: ${error.type}\nStatus: ${error.status}`);
    }
    setLoading(false);
  };

  return (
    <ChatLayout>
      <Header />
      <MainContent>
        <div className="space-y-6">
          {/* Main Grading Interface */}
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-gray-900">
                APUSH Essay Grader
              </h2>
              <p className="text-gray-600 leading-relaxed mt-2">
                Grade AP US History essays with AI assistance
              </p>
            </div>

            {/* Essay Grading Form */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <EssayTypeSelector
                selectedType={state.form.essayType}
                onTypeChange={actions.setEssayType}
                disabled={state.isSubmitting}
              />

              {/* Essay type validation feedback */}
              {state.validationErrors.essayType && (
                <div className="text-red-600 text-sm flex items-center gap-2 mt-2">
                  <span className="text-red-500">⚠</span>
                  <span>{state.validationErrors.essayType}</span>
                </div>
              )}

              {/* Prompt input - appears for all essay types */}
              {state.form.essayType && (
                <div className="space-y-3">
                  <label htmlFor="prompt-input" className="block text-sm font-medium text-gray-700">
                    Essay Prompt / Question
                  </label>
                  <PromptInput
                    id="prompt-input"
                    value={state.form.prompt}
                    onChange={actions.setPrompt}
                    essayType={state.form.essayType}
                    saqType={state.form.saqType}
                    disabled={state.isSubmitting}
                    error={state.validationErrors.prompt}
                    ariaDescribedBy="prompt-help"
                  />
                  <div id="prompt-help" className="text-xs text-gray-500">
                    Enter the essay question or prompt that students are responding to
                  </div>
                </div>
              )}

              {/* SAQ-specific components */}
              {state.form.essayType === 'SAQ' && (
                <div className="border-t pt-6 space-y-6">
                  <SAQTypeSelector
                    selectedType={state.form.saqType}
                    onTypeChange={actions.setSaqType}
                    disabled={state.isSubmitting}
                  />
                  
                  <SAQMultiPartInput
                    saqParts={state.form.saqParts}
                    onPartChange={actions.setSaqPart}
                    disabled={state.isSubmitting}
                    validationErrors={state.validationErrors}
                  />
                  {/* Overall SAQ validation - only shows if no individual parts have content */}
                  {state.validationErrors.saqParts && (
                    <div className="text-red-600 text-sm flex items-center gap-2 mt-2">
                      <span className="text-red-500">⚠</span>
                      <span>{state.validationErrors.saqParts}</span>
                    </div>
                  )}
                </div>
              )}

              {/* DBQ/LEQ essay text input */}
              {(state.form.essayType === 'DBQ' || state.form.essayType === 'LEQ') && (
                <div className="border-t pt-6 space-y-3">
                  <label htmlFor="essay-text-input" className="block text-sm font-medium text-gray-700">
                    Student Essay Text
                  </label>
                  <ChatTextArea
                    id="essay-text-input"
                    value={state.form.essayText}
                    onChange={actions.setEssayText}
                    placeholder={`Enter the student's ${state.form.essayType} essay text here...`}
                    disabled={state.isSubmitting}
                    error={state.validationErrors.essayText}
                    minRows={6}
                    maxRows={20}
                    ariaDescribedBy="essay-text-help"
                  />
                  <div id="essay-text-help" className="text-xs text-gray-500">
                    Paste the complete student essay response for grading
                  </div>
                </div>
              )}

              {/* Submit Button - Hidden when results are displayed */}
              {state.form.essayType && !state.lastResult && (
                <div className="border-t pt-6">
                  <SubmitButton
                    isValid={state.isFormValid}
                    isSubmitting={state.isSubmitting}
                    onClick={handleGradingSubmit}
                  />
                  
                  {/* Inline error display */}
                  {submitError && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center gap-2 text-red-700">
                        <span className="text-red-500">⚠</span>
                        <span className="text-sm font-medium">Error</span>
                      </div>
                      <p className="text-sm text-red-600 mt-1">{submitError}</p>
                      <button
                        onClick={() => setSubmitError('')}
                        className="mt-2 text-xs text-red-600 hover:text-red-700 underline"
                      >
                        Dismiss
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Enhanced Results Display - Issue #32 Score Visualization */}
            {state.lastResult && (
              <div className="mt-6">
                <ResultsDisplay 
                  result={state.lastResult}
                  onNewEssay={() => actions.setResult(null)}
                />
              </div>
            )}
          </div>

          {/* Development Progress Sections */}
          <div className="max-w-4xl mx-auto space-y-6">
          <div className="bg-gray-50 rounded-lg p-6 text-left">
            <h3 className="font-semibold text-gray-900 mb-3">
              Issue #24 Components Complete:
            </h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                ChatLayout with centered 768px max-width
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                Header component with app title
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                MainContent conversation area
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                React Router basic structure
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                ChatGPT-style typography & spacing
              </li>
            </ul>
          </div>


          {/* API Testing Section - Issue #25 */}
          <div className="bg-blue-50 rounded-lg p-6 text-left">
            <h3 className="font-semibold text-blue-900 mb-4">
              🧪 Issue #25: API Service Layer Testing
            </h3>
            <p className="text-blue-700 mb-4">
              Test the TypeScript API service integration with the Python backend:
            </p>
            
            <div className="space-x-3 mb-4">
              <button
                onClick={testHealthCheck}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                Test Health Check
              </button>
              <button
                onClick={testUsageSummary}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                Test Usage Summary
              </button>
              <button
                onClick={testGrading}
                disabled={loading}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
              >
                Test SAQ Grading
              </button>
            </div>

            {testResults && (
              <div className="bg-white border rounded p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Test Results:</h4>
                <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto">
                  {testResults}
                </pre>
              </div>
            )}
          </div>
          </div>
        </div>
      </MainContent>
    </ChatLayout>
  );
};

/**
 * Main grading page component wrapped with context provider
 */
const GradingPage: React.FC = () => {
  return (
    <GradingProvider>
      <GradingPageContent />
    </GradingProvider>
  );
};

export default GradingPage;