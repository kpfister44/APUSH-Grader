import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { EssayType, SAQType, GradingResponse } from '../types/api';

// ============================================================================
// State Types
// ============================================================================

interface GradingFormState {
  essayType: EssayType | null;
  saqType: SAQType | null;
  essayText: string;
  prompt: string;
  saqParts: {
    part_a: string;
    part_b: string;
    part_c: string;
  };
}

interface GradingState {
  // Form state
  form: GradingFormState;
  
  // Submission state
  isSubmitting: boolean;
  lastResult: GradingResponse | null;
  
  // Validation state
  validationErrors: Record<string, string>;
  isFormValid: boolean;
}

// ============================================================================
// Action Types
// ============================================================================

type GradingAction =
  | { type: 'SET_ESSAY_TYPE'; payload: EssayType | null }
  | { type: 'SET_SAQ_TYPE'; payload: SAQType | null }
  | { type: 'SET_ESSAY_TEXT'; payload: string }
  | { type: 'SET_PROMPT'; payload: string }
  | { type: 'SET_SAQ_PART'; payload: { part: keyof GradingFormState['saqParts']; value: string } }
  | { type: 'CLEAR_FORM' }
  | { type: 'CLEAR_FIELDS_ON_TYPE_CHANGE' }
  | { type: 'SET_SUBMITTING'; payload: boolean }
  | { type: 'SET_RESULT'; payload: GradingResponse | null }
  | { type: 'SET_VALIDATION_ERRORS'; payload: Record<string, string> }
  | { type: 'VALIDATE_FORM' };

// ============================================================================
// Initial State
// ============================================================================

const initialFormState: GradingFormState = {
  essayType: null,
  saqType: null,
  essayText: '',
  prompt: '',
  saqParts: {
    part_a: '',
    part_b: '',
    part_c: ''
  }
};

const initialState: GradingState = {
  form: initialFormState,
  isSubmitting: false,
  lastResult: null,
  validationErrors: {},
  isFormValid: false
};

// ============================================================================
// Validation Logic
// ============================================================================

const validateForm = (form: GradingFormState): Record<string, string> => {
  const errors: Record<string, string> = {};

  // Essay type is required
  if (!form.essayType) {
    errors.essayType = 'Please select an essay type';
  }

  // Prompt is always required
  if (!form.prompt.trim()) {
    errors.prompt = 'Please enter the essay prompt or question';
  }

  // Content validation depends on essay type
  if (form.essayType === 'SAQ') {
    // For SAQ, at least one part must have content
    const hasContent = form.saqParts.part_a.trim() || 
                      form.saqParts.part_b.trim() || 
                      form.saqParts.part_c.trim();
    
    if (!hasContent) {
      errors.saqParts = 'Please provide content for at least one SAQ part';
    }

    // Individual part validation (optional but helpful for user experience)
    // Note: These are warnings, not blocking errors since SAQ parts are optional
    const parts = ['part_a', 'part_b', 'part_c'] as const;
    parts.forEach(part => {
      const content = form.saqParts[part].trim();
      if (content) {
        const wordCount = content.split(/\s+/).length;
        if (wordCount < 20) {
          errors[part] = `${part.replace('_', ' ').toUpperCase()} seems short. Consider expanding your response.`;
        }
      }
    });
  } else if (form.essayType === 'DBQ' || form.essayType === 'LEQ') {
    // For DBQ/LEQ, essay text is required
    if (!form.essayText.trim()) {
      errors.essayText = 'Please enter the essay text';
    }
  }

  return errors;
};

// ============================================================================
// Reducer
// ============================================================================

const gradingReducer = (state: GradingState, action: GradingAction): GradingState => {
  switch (action.type) {
    case 'SET_ESSAY_TYPE': {
      const newForm = {
        ...state.form,
        essayType: action.payload
      };
      
      // Clear fields when essay type changes (except prompt)
      if (action.payload !== state.form.essayType && state.form.essayType !== null) {
        newForm.essayText = '';
        newForm.saqType = null;
        newForm.saqParts = { ...initialFormState.saqParts };
      }
      
      const validationErrors = validateForm(newForm);
      
      return {
        ...state,
        form: newForm,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0,
        lastResult: null // Clear previous results when form changes
      };
    }

    case 'SET_SAQ_TYPE': {
      const newForm = {
        ...state.form,
        saqType: action.payload
      };
      
      const validationErrors = validateForm(newForm);
      
      return {
        ...state,
        form: newForm,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0
      };
    }

    case 'SET_ESSAY_TEXT': {
      const newForm = {
        ...state.form,
        essayText: action.payload
      };
      
      const validationErrors = validateForm(newForm);
      
      return {
        ...state,
        form: newForm,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0
      };
    }

    case 'SET_PROMPT': {
      const newForm = {
        ...state.form,
        prompt: action.payload
      };
      
      const validationErrors = validateForm(newForm);
      
      return {
        ...state,
        form: newForm,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0
      };
    }

    case 'SET_SAQ_PART': {
      const newForm = {
        ...state.form,
        saqParts: {
          ...state.form.saqParts,
          [action.payload.part]: action.payload.value
        }
      };
      
      const validationErrors = validateForm(newForm);
      
      return {
        ...state,
        form: newForm,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0
      };
    }

    case 'CLEAR_FORM':
      return {
        ...initialState
      };

    case 'CLEAR_FIELDS_ON_TYPE_CHANGE': {
      const newForm = {
        ...state.form,
        essayText: '',
        saqType: null,
        saqParts: { ...initialFormState.saqParts }
      };
      
      const validationErrors = validateForm(newForm);
      
      return {
        ...state,
        form: newForm,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0,
        lastResult: null
      };
    }

    case 'SET_SUBMITTING':
      return {
        ...state,
        isSubmitting: action.payload
      };

    case 'SET_RESULT':
      return {
        ...state,
        lastResult: action.payload,
        isSubmitting: false
      };

    case 'SET_VALIDATION_ERRORS':
      return {
        ...state,
        validationErrors: action.payload,
        isFormValid: Object.keys(action.payload).length === 0
      };

    case 'VALIDATE_FORM': {
      const validationErrors = validateForm(state.form);
      return {
        ...state,
        validationErrors,
        isFormValid: Object.keys(validationErrors).length === 0
      };
    }

    default:
      return state;
  }
};

// ============================================================================
// Context
// ============================================================================

interface GradingContextType {
  state: GradingState;
  actions: {
    setEssayType: (type: EssayType | null) => void;
    setSaqType: (type: SAQType | null) => void;
    setEssayText: (text: string) => void;
    setPrompt: (prompt: string) => void;
    setSaqPart: (part: keyof GradingFormState['saqParts'], value: string) => void;
    clearForm: () => void;
    clearFieldsOnTypeChange: () => void;
    setSubmitting: (submitting: boolean) => void;
    setResult: (result: GradingResponse | null) => void;
    setValidationErrors: (errors: Record<string, string>) => void;
    validateForm: () => void;
  };
}

const GradingContext = createContext<GradingContextType | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

interface GradingProviderProps {
  children: ReactNode;
}

export const GradingProvider: React.FC<GradingProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(gradingReducer, initialState);

  const actions = {
    setEssayType: (type: EssayType | null) => 
      dispatch({ type: 'SET_ESSAY_TYPE', payload: type }),
    
    setSaqType: (type: SAQType | null) => 
      dispatch({ type: 'SET_SAQ_TYPE', payload: type }),
    
    setEssayText: (text: string) => 
      dispatch({ type: 'SET_ESSAY_TEXT', payload: text }),
    
    setPrompt: (prompt: string) => 
      dispatch({ type: 'SET_PROMPT', payload: prompt }),
    
    setSaqPart: (part: keyof GradingFormState['saqParts'], value: string) => 
      dispatch({ type: 'SET_SAQ_PART', payload: { part, value } }),
    
    clearForm: () => 
      dispatch({ type: 'CLEAR_FORM' }),
    
    clearFieldsOnTypeChange: () => 
      dispatch({ type: 'CLEAR_FIELDS_ON_TYPE_CHANGE' }),
    
    setSubmitting: (submitting: boolean) => 
      dispatch({ type: 'SET_SUBMITTING', payload: submitting }),
    
    setResult: (result: GradingResponse | null) => 
      dispatch({ type: 'SET_RESULT', payload: result }),
    
    setValidationErrors: (errors: Record<string, string>) => 
      dispatch({ type: 'SET_VALIDATION_ERRORS', payload: errors }),
    
    validateForm: () => 
      dispatch({ type: 'VALIDATE_FORM' })
  };

  const contextValue: GradingContextType = {
    state,
    actions
  };

  return (
    <GradingContext.Provider value={contextValue}>
      {children}
    </GradingContext.Provider>
  );
};

// ============================================================================
// Hook
// ============================================================================

export const useGrading = (): GradingContextType => {
  const context = useContext(GradingContext);
  if (context === undefined) {
    throw new Error('useGrading must be used within a GradingProvider');
  }
  return context;
};

export default GradingContext;