import React from "react";
import { View, Text } from "react-native";
import { Feather } from "@expo/vector-icons";
import { Dimensions } from "react-native";

interface FeatureCardProps {
  icon: keyof typeof Feather.glyphMap;
  iconColor: string;
  iconBgColor: string;
  title: string;
  titleColor: string;
  description: string;
  isHighlighted?: boolean;
}

const { width } = Dimensions.get("window");

// Responsive sizing function
const rs = (size: number) => {
  const baseWidth = 375;
  return (width / baseWidth) * size;
};

export function FeatureCard({
  icon,
  iconColor,
  iconBgColor,
  title,
  titleColor,
  description,
  isHighlighted = false,
}: FeatureCardProps) {
  return (
    <View
      className={`bg-white rounded-[12px] p-[20px] m-[8px] w-[90%] md:w-[30%] mb-[16px] shadow ${
        isHighlighted ? "border border-[#00BFA5]" : "border-transparent"
      }`}
    >
      <View className="items-center mb-4">
        <View
          className={`p-[12px] rounded-[10px]`}
          style={{ backgroundColor: iconBgColor }}
        >
          <Feather name={icon} size={rs(24)} color={iconColor} />
        </View>
      </View>

      <Text
        className={`font-medium text-center mb-[8px] text-[16px]`}
        style={{ color: titleColor }}
      >
        {title}
      </Text>

      <Text className="text-[#4B5563] font-normal text-center text-[13px] leading-[20px]">
        {description}
      </Text>
    </View>
  );
}
