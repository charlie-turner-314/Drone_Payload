import { configureStore, createSlice } from "@reduxjs/toolkit";

const mute = createSlice({
    name: 'mute',
    initialState: true,
    reducers: {
        toggleMute: state => !state
    }
})
const rate = createSlice({
    name: 'rate',
    initialState: 1000,
    reducers: {
        setRate: (_, action) => action.payload
    }
})

const Store = configureStore({
    reducer: {
        mute: mute.reducer,
        rate: rate.reducer
    }
})

export const { toggleMute } = mute.actions
export const { setRate } = rate.actions
export default Store