import React from "react";
import { View, Text } from "react-native";
import { Feather } from "@expo/vector-icons";
import { Dimensions } from "react-native";

interface DashboardItemProps {
  icon: keyof typeof Feather.glyphMap;
  value: string;
  label: string;
  color: string;
}

const { width } = Dimensions.get("window");

// Responsive sizing function
const rs = (size: number) => {
  const baseWidth = 375;
  return (width / baseWidth) * size;
};

export function DashboardItem({ icon, value, label, color }: DashboardItemProps) {
  return (
    <View className="items-center mb-4 w-[22%]">
      <View
        className="items-center justify-center w-12 h-12 rounded-full mb-2"
        style={{ backgroundColor: `${color}20` }}
      >
        <Feather name={icon} size={rs(20)} color={color} />
      </View>
      <Text className="text-[18px] font-bold" style={{ color }}>
        {value}
      </Text>
      <Text className="text-[12px] text-[#6B7280]">{label}</Text>
    </View>
  );
}
