import React from "react";
import { View, Text } from "react-native";

interface InfoBoxProps {
  title: string;
  value: string;
  color: string;
}

export function InfoBox({ title, value, color }: InfoBoxProps) {
  return (
    <View className="items-center p-2 bg-[#F9FAFB] rounded-lg w-[30%]">
      <Text className="text-[12px] text-[#6B7280] mb-1">{title}</Text>
      <Text className="text-[18px] font-bold" style={{ color }}>
        {value}
      </Text>
    </View>
  );
}
