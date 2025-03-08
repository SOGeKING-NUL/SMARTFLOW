import React from 'react'
import { Slot, Stack } from 'expo-router'
import "@/global.css"

const RootLayout = () => {
  return (
    <Stack>
      <Stack.Screen name='main' options={{headerShown: true}} />
    </Stack>
  )
}

export default RootLayout