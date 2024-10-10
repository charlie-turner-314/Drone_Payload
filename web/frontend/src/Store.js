import { configureStore, createSlice } from "@reduxjs/toolkit";

const mute = createSlice({
    name: 'mute',
    initialState: true,
    reducers: {
        toggleMute: state => !state
    }
})

const Store = configureStore({
    reducer: {
        mute: mute.reducer
    }
})

export const { toggleMute } = mute.actions
export default Store