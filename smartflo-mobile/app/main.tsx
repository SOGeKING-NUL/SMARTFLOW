import React, { useState, useEffect } from "react";
import { StatusBar } from "expo-status-bar";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Dimensions,
  Modal,
  Image,
  FlatList,
  Alert,
} from "react-native";
import { useFonts } from "expo-font";
import { Feather } from "@expo/vector-icons";
import {
  Poppins_500Medium,
  Poppins_400Regular,
  Poppins_700Bold,
} from "@expo-google-fonts/poppins";
import { DashboardItem } from "@/components/DashboardItem";
import { FeatureCard } from "@/components/FeatureCard";
import { InfoBox } from "@/components/InfoBox";

// Get device dimensions
const { width } = Dimensions.get("window");

// Responsive sizing function
const rs = (size: number) => {
  const baseWidth = 375;
  return (width / baseWidth) * size;
};

// Traffic incident interface
interface TrafficIncident {
  id: string;
  type: string;
  location: string;
  severity: "Low" | "Medium" | "High";
  timestamp: string;
  description: string;
}

// Traffic data interface
interface TrafficData {
  congestionLevel: number;
  averageSpeed: number;
  incidents: number;
  emergencyVehicles: number;
}

export default function App() {
  const [fontsLoaded] = useFonts({
    Poppins_500Medium,
    Poppins_400Regular,
    Poppins_700Bold,
  });

  // State management
  const [showDemoModal, setShowDemoModal] = useState(false);
  const [showEmergencyAlert, setShowEmergencyAlert] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [trafficData, setTrafficData] = useState<TrafficData>({
    congestionLevel: 65,
    averageSpeed: 28,
    incidents: 2,
    emergencyVehicles: 1,
  });

  // Mock incidents data
  const [incidents, setIncidents] = useState<TrafficIncident[]>([
    {
      id: "1",
      type: "Accident",
      location: "Main St & 5th Ave",
      severity: "High",
      timestamp: "10:30 AM",
      description: "Multi-vehicle collision blocking two lanes",
    },
    {
      id: "2",
      type: "Construction",
      location: "Cedar Rd & Park Ave",
      severity: "Medium",
      timestamp: "09:15 AM",
      description: "Road work causing lane closure",
    },
  ]);

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate traffic data changes
      setTrafficData((prevData) => ({
        congestionLevel: Math.min(
          100,
          Math.max(0, prevData.congestionLevel + (Math.random() > 0.5 ? 3 : -2))
        ),
        averageSpeed: Math.min(
          60,
          Math.max(10, prevData.averageSpeed + (Math.random() > 0.5 ? 2 : -1))
        ),
        incidents: prevData.incidents,
        emergencyVehicles:
          Math.random() > 0.9
            ? prevData.emergencyVehicles + 1
            : prevData.emergencyVehicles,
      }));
    }, 5000);

    // Simulate emergency vehicle alert
    const emergencyTimer = setTimeout(() => {
      setShowEmergencyAlert(true);
    }, 10000);

    return () => {
      clearInterval(interval);
      clearTimeout(emergencyTimer);
    };
  }, []);

  // Handle emergency priority
  const handleEmergencyPriority = () => {
    Alert.alert(
      "Emergency Vehicle Detected",
      "Rerouting traffic and prioritizing signals for emergency vehicle on Main St.",
      [{ text: "OK", onPress: () => setShowEmergencyAlert(false) }]
    );
  };

  // Handle demo view
  const handleViewDemo = () => {
    setShowDemoModal(true);
  };

  if (!fontsLoaded) {
    return <Text>Loading fonts...</Text>;
  }

  return (
    <View className="flex-1 bg-[#f8fff8]">
      <StatusBar style="dark" />
      <SafeAreaView className="flex-1">
        <ScrollView showsVerticalScrollIndicator={false}>
          <View className="items-center justify-center py-10 px-4">
            {/* Logo with gradient text */}
            <View className="mb-8">
              <Text className="text-center text-[60px] font-extrabold tracking-tighter">
                <Text className="text-[#FFC107]">SMART</Text>
                <Text className="text-[#FF5252]">FLOW</Text>
              </Text>
            </View>

            <Text className="text-[#00BFA5] text-[20px] mb-[20px] font-medium">
              AI-Driven Traffic Management
            </Text>

            <Text className="text-[15px] leading-[22px] max-w-[360px] text-center text-[#4B5563] mb-[32px] font-normal">
              Revolutionizing urban mobility with intelligent traffic systems
              that prioritize emergency vehicles and optimize flow in real-time.
            </Text>

            {/* Real-time Traffic Dashboard */}
            <View className="w-full bg-white rounded-[15px] p-[20px] mb-[30px] shadow">
              <Text className="text-[18px] font-medium text-[#374151] mb-[15px]">
                Real-Time Traffic Dashboard
              </Text>

              <View className="flex-row flex-wrap justify-between">
                <DashboardItem
                  icon="bar-chart-2"
                  value={`${Math.round(trafficData.congestionLevel)}%`}
                  label="Congestion"
                  color={
                    trafficData.congestionLevel > 70 ? "#FF5252" : "#00BFA5"
                  }
                />
                <DashboardItem
                  icon="alert-triangle"
                  value={trafficData.incidents.toString()}
                  label="Incidents"
                  color="#FFC107"
                />
                <DashboardItem
                  icon="wind"
                  value={`${Math.round(trafficData.averageSpeed)} mph`}
                  label="Avg Speed"
                  color="#00BFA5"
                />
                <DashboardItem
                  icon="zap"
                  value={trafficData.emergencyVehicles.toString()}
                  label="Emergency"
                  color="#9D4EDD"
                />
              </View>
            </View>

            {/* Traffic Incidents List */}
            {incidents.length > 0 && (
              <View className="w-full bg-white rounded-[15px] p-[20px] mb-[30px] shadow">
                <Text className="text-[18px] font-medium text-[#374151] mb-[15px]">
                  Current Traffic Incidents
                </Text>

                {incidents.map((incident) => (
                  <View
                    key={incident.id}
                    className="mb-4 p-3 bg-[#F9FAFB] rounded-lg border-l-4"
                    style={{
                      borderLeftColor:
                        incident.severity === "High"
                          ? "#FF5252"
                          : incident.severity === "Medium"
                          ? "#FFC107"
                          : "#00BFA5",
                    }}
                  >
                    <View className="flex-row justify-between items-center mb-1">
                      <Text className="text-[16px] font-medium text-[#374151]">
                        {incident.type}
                      </Text>
                      <Text className="text-[12px] text-[#6B7280]">
                        {incident.timestamp}
                      </Text>
                    </View>
                    <Text className="text-[14px] text-[#4B5563] mb-1">
                      {incident.location}
                    </Text>
                    <Text className="text-[13px] text-[#6B7280]">
                      {incident.description}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Action buttons with improved styling */}
            <View className="flex-row w-full justify-center space-x-4 mb-12">
              <TouchableOpacity
                className="bg-[#00BFA5] rounded-[8px] py-[12px] px-[20px] w-[45%] items-center justify-center shadow-md"
                onPress={handleViewDemo}
              >
                <Text className="text-white font-medium text-[15px]">
                  See It In Action
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                className="bg-white rounded-[8px] py-[12px] px-[20px] w-[45%] items-center justify-center shadow-sm"
                onPress={() => {
                  setActiveTab("features");
                  // Scroll to the features section
                  Alert.alert(
                    "Features Explored",
                    "Discover our AI-driven traffic management capabilities that prioritize emergency vehicles and optimize traffic flow in real-time.",
                    [
                      {
                        text: "Learn More",
                        onPress: () =>
                          console.log(
                            "User wants to learn more about features"
                          ),
                      },
                      { text: "Close", style: "cancel" },
                    ]
                  );
                }}
              >
                <Text className="text-[#374151] font-medium text-[15px]">
                  Explore Features
                </Text>
              </TouchableOpacity>
            </View>

            {/* Scroll indicator */}
            <TouchableOpacity className="my-4">
              <Feather name="chevron-down" size={rs(24)} color="#6B7280" />
            </TouchableOpacity>

            {/* Features section with gradient title */}
            <View className="w-full mt-16 mb-8">
              <View className="mb-10">
                <Text className="text-[36px] font-extrabold text-center">
                  <Text className="text-[#FFC107]">Key </Text>
                  <Text className="text-[#FF5252]">Features</Text>
                </Text>

                <Text className="text-[14px] max-w-[360px] self-center text-center text-[#4B5563] mt-[8px] font-normal">
                  Our cutting-edge technology transforms traffic management with
                  these powerful capabilities
                </Text>
              </View>

              {/* Feature cards */}
              <View className="flex-row flex-wrap justify-center">
                <FeatureCard
                  icon="alert-triangle"
                  iconColor="#FF8C42"
                  iconBgColor="#FFF1E6"
                  title="Emergency Priority"
                  titleColor="#FF8C42"
                  description="Intelligent system that automatically prioritizes ambulances and emergency vehicles to save critical minutes."
                />

                <FeatureCard
                  icon="bar-chart-2"
                  iconColor="#00BFA5"
                  iconBgColor="#E8F8F5"
                  title="Real-Time Data Analysis"
                  titleColor="#00BFA5"
                  description="Advanced algorithms monitor and manage congestion effectively, reducing wait times by up to 40%."
                />

                <FeatureCard
                  icon="zap"
                  iconColor="#9D4EDD"
                  iconBgColor="#F5F3FF"
                  title="AI-Powered Optimization"
                  titleColor="#9D4EDD"
                  description="Smart traffic signals adjust dynamically based on real-time traffic patterns and density analysis."
                  isHighlighted={true}
                />

                <FeatureCard
                  icon="navigation"
                  iconColor="#3B82F6"
                  iconBgColor="#EFF6FF"
                  title="Route Optimization"
                  titleColor="#3B82F6"
                  description="Intelligent routing algorithms suggest alternative paths to avoid congestion and minimize travel time."
                />

                <FeatureCard
                  icon="shield"
                  iconColor="#10B981"
                  iconBgColor="#ECFDF5"
                  title="Incident Detection"
                  titleColor="#10B981"
                  description="Advanced sensors and cameras detect accidents and obstructions, enabling rapid response to clear roadways."
                />
              </View>
            </View>
          </View>
        </ScrollView>

        {/* Emergency Alert Modal */}
        {showEmergencyAlert && (
          <View className="absolute top-0 left-0 right-0 bg-[#FF5252] p-4 flex-row items-center justify-between">
            <View className="flex-row items-center">
              <Feather name="alert-circle" size={24} color="white" />
              <Text className="text-white font-medium ml-2">
                Emergency Vehicle Approaching
              </Text>
            </View>
            <TouchableOpacity onPress={handleEmergencyPriority}>
              <Text className="text-white font-medium">View</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Demo Modal */}
        <Modal
          visible={showDemoModal}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setShowDemoModal(false)}
        >
          <View className="flex-1 justify-center items-center bg-black/50">
            <View className="bg-white w-[90%] rounded-xl p-6">
              <View className="flex-row justify-between items-center mb-4">
                <Text className="text-[20px] font-bold text-[#374151]">
                  Traffic Simulation
                </Text>
                <TouchableOpacity onPress={() => setShowDemoModal(false)}>
                  <Feather name="x" size={24} color="#6B7280" />
                </TouchableOpacity>
              </View>

              <Text className="text-[16px] text-[#4B5563] mb-4">
                Watch how our AI system optimizes traffic flow in real-time,
                prioritizing emergency vehicles and reducing congestion.
              </Text>

              <View className="h-[200px] bg-[#F3F4F6] rounded-lg mb-4 items-center justify-center">
                <Text className="text-[#6B7280]">
                  Simulation visualization would appear here
                </Text>
              </View>

              <View className="flex-row justify-between mb-4">
                <InfoBox
                  title="Traffic Reduction"
                  value="42%"
                  color="#00BFA5"
                />
                <InfoBox title="Response Time" value="-30%" color="#FF5252" />
                <InfoBox title="Fuel Saved" value="25%" color="#FFC107" />
              </View>

              <TouchableOpacity
                className="bg-[#00BFA5] py-3 rounded-lg items-center"
                onPress={() => setShowDemoModal(false)}
              >
                <Text className="text-white font-medium">Close Demo</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      </SafeAreaView>
    </View>
  );
}
