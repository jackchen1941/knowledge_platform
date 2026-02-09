import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface KnowledgeState {
  items: any[];
  selectedItem: any | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: KnowledgeState = {
  items: [],
  selectedItem: null,
  isLoading: false,
  error: null,
};

const knowledgeSlice = createSlice({
  name: 'knowledge',
  initialState,
  reducers: {
    setItems: (state, action: PayloadAction<any[]>) => {
      state.items = action.payload;
    },
    setSelectedItem: (state, action: PayloadAction<any | null>) => {
      state.selectedItem = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setItems, setSelectedItem, setLoading, setError } = knowledgeSlice.actions;
export default knowledgeSlice.reducer;