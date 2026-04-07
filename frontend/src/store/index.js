import { configureStore } from '@reduxjs/toolkit';
import avatarReducer from './avatarSlice';

export const store = configureStore({
  reducer: {
    avatar: avatarReducer,
  },
});