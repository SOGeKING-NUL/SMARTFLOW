import React from 'react'
import { Slot, Stack } from 'expo-router'
import { Text } from 'react-native'
import "@/global.css"

const RootLayout = () => {
  return (
    <Stack>
      <Stack.Screen name='main' options={{headerShown: false}} />
    </Stack>
  )
}

export default RootLayout