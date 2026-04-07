import { createSlice } from '@reduxjs/toolkit';

const avatarStates = {
  IDLE: 'idle',
  LISTENING: 'listening', 
  THINKING: 'thinking',
  ANALYZING: 'analyzing',
  PRESENTING: 'presenting',
  ENCOURAGING: 'encouraging',
  CELEBRATING: 'celebrating',
  ERROR: 'error'
};

const initialState = {
  currentState: avatarStates.IDLE,
  isVisible: true,
  states: avatarStates
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
    setPresenting: (state) => {
      state.currentState = avatarStates.PRESENTING;
    },
    setEncouraging: (state) => {
      state.currentState = avatarStates.ENCOURAGING;
    },
    setCelebrating: (state) => {
      state.currentState = avatarStates.CELEBRATING;
    },
    setError: (state) => {
      state.currentState = avatarStates.ERROR;
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
  toggleVisibility,
  setVisibility
} = avatarSlice.actions;

export default avatarSlice.reducer;