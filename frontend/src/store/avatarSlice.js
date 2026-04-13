import { createSlice } from '@reduxjs/toolkit';

const avatarStates = {
  IDLE: 'idle',
  LISTENING: 'listening', 
  THINKING: 'thinking',
  ANALYZING: 'analyzing',
  PRESENTING: 'presenting',
  ENCOURAGING: 'encouraging',
  CELEBRATING: 'celebrating',
  ERROR: 'error',
  WARNING: 'warning'
};

const initialState = {
  currentState: avatarStates.IDLE,
  isVisible: true,
  states: avatarStates,
  warningData: null,
  encouragingMessage: null,
  presentingMessage: null
};

export const avatarSlice = createSlice({
  name: 'avatar',
  initialState,
  reducers: {
    setState: (state, action) => {
      state.currentState = action.payload;
    },
    setIdle: (state) => {
      state.currentState = avatarStates.IDLE;
      state.encouragingMessage = null;
      state.presentingMessage = null;
    },
    setListening: (state) => {
      state.currentState = avatarStates.LISTENING;
    },
    setThinking: (state) => {
      state.currentState = avatarStates.THINKING;
    },
    setAnalyzing: (state) => {
      state.currentState = avatarStates.ANALYZING;
    },
    setPresenting: (state, action) => {
      state.currentState = avatarStates.PRESENTING;
      state.presentingMessage = action.payload || 'Preparing insights...';
    },
    setEncouraging: (state, action) => {
      state.currentState = avatarStates.ENCOURAGING;
      state.encouragingMessage = action.payload || 'Great work!';
    },
    setCelebrating: (state) => {
      state.currentState = avatarStates.CELEBRATING;
    },
    setError: (state) => {
      state.currentState = avatarStates.ERROR;
    },
    setWarning: (state, action) => {
      state.currentState = avatarStates.WARNING;
      state.warningData = action.payload;
    },
    clearWarning: (state) => {
      state.currentState = avatarStates.IDLE;
      state.warningData = null;
    },
    toggleVisibility: (state) => {
      state.isVisible = !state.isVisible;
    },
    setVisibility: (state, action) => {
      state.isVisible = action.payload;
    }
  }
});

export const {
  setState,
  setIdle,
  setListening,
  setThinking,
  setAnalyzing,
  setPresenting,
  setEncouraging,
  setCelebrating,
  setError,
  setWarning,
  clearWarning,
  toggleVisibility,
  setVisibility
} = avatarSlice.actions;

export default avatarSlice.reducer;