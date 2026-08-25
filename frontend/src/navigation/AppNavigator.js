import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  StatusBar
} from "react-native";
import { colors } from "../theme/colors";
import { useApp } from "../context/AppContext";

import OnboardingScreen from "../screens/OnboardingScreen";
import SpokenAgreementScreen from "../screens/SpokenAgreementScreen";
import AttendanceScreen from "../screens/AttendanceScreen";
import WalletDashboardScreen from "../screens/WalletDashboardScreen";
import DisputeTerminalScreen from "../screens/DisputeTerminalScreen";

const SCREENS = [
  { key: "Onboarding", label: "Sign-Up", icon: "🪪" },
  { key: "Agreement", label: "Agreement", icon: "🎙️" },
  { key: "Attendance", label: "Check-In", icon: "⚡" },
  { key: "Wallet", label: "Wallet", icon: "💰" },
  { key: "Dispute", label: "Dispute", icon: "🚨" }
];

export default function AppNavigator() {
  const [currentScreen, setCurrentScreen] = useState("Onboarding");
  const { isDeficit } = useApp();

  const renderScreen = () => {
    switch (currentScreen) {
      case "Onboarding":
        return <OnboardingScreen onNavigate={setCurrentScreen} />;
      case "Agreement":
        return <SpokenAgreementScreen onNavigate={setCurrentScreen} />;
      case "Attendance":
        return <AttendanceScreen onNavigate={setCurrentScreen} />;
      case "Wallet":
        return <WalletDashboardScreen onNavigate={setCurrentScreen} />;
      case "Dispute":
        return <DisputeTerminalScreen onNavigate={setCurrentScreen} />;
      default:
        return <OnboardingScreen onNavigate={setCurrentScreen} />;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />

      {/* Top Application Bar with Navigation Quick Switcher */}
      <View style={styles.topBar}>
        <View style={styles.brandRow}>
          <Text style={styles.brandLogo}>⚡ KARMSETU</Text>
          <View style={styles.statusPill}>
            <View style={[styles.statusDot, isDeficit ? styles.dotAlert : styles.dotOk]} />
            <Text style={[styles.statusText, isDeficit ? styles.textAlert : styles.textOk]}>
              {isDeficit ? "DEFICIT ALERT" : "NPU SECURE"}
            </Text>
          </View>
        </View>

        {/* Screen Breadcrumb / Step Indicator */}
        <View style={styles.stepBar}>
          {SCREENS.map((s, idx) => {
            const isActive = currentScreen === s.key;
            return (
              <TouchableOpacity
                key={s.key}
                style={[
                  styles.stepSegment,
                  isActive && styles.stepSegmentActive,
                  s.key === "Dispute" && isDeficit && styles.stepSegmentAlert
                ]}
                onPress={() => setCurrentScreen(s.key)}
              >
                <Text style={styles.stepIndex}>{idx + 1}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Active Screen Content */}
      <View style={styles.screenContainer}>
        {renderScreen()}
      </View>

      {/* High-Contrast AMOLED Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        {SCREENS.map((screen) => {
          const isActive = currentScreen === screen.key;
          const isAlertTab = screen.key === "Dispute" && isDeficit;

          return (
            <TouchableOpacity
              key={screen.key}
              style={[styles.tabButton, isActive && styles.tabButtonActive]}
              onPress={() => setCurrentScreen(screen.key)}
              activeOpacity={0.8}
            >
              {isActive && <View style={[styles.activeIndicator, isAlertTab && styles.activeIndicatorAlert]} />}
              <Text style={styles.tabIcon}>{screen.icon}</Text>
              <Text
                style={[
                  styles.tabLabel,
                  isActive && styles.tabLabelActive,
                  isAlertTab && styles.tabLabelAlert
                ]}
              >
                {screen.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000000"
  },
  topBar: {
    backgroundColor: "#000000",
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 8
  },
  brandRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8
  },
  brandLogo: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: "900",
    letterSpacing: 1.5
  },
  statusPill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#0A0F18",
    borderWidth: 1,
    borderColor: colors.cardBorder,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6
  },
  dotOk: {
    backgroundColor: colors.success
  },
  dotAlert: {
    backgroundColor: colors.danger
  },
  statusText: {
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.5
  },
  textOk: {
    color: colors.success
  },
  textAlert: {
    color: colors.danger
  },
  stepBar: {
    flexDirection: "row",
    gap: 6
  },
  stepSegment: {
    flex: 1,
    height: 4,
    backgroundColor: "#1E2433",
    borderRadius: 2,
    justifyContent: "center",
    alignItems: "center"
  },
  stepSegmentActive: {
    backgroundColor: colors.primary
  },
  stepSegmentAlert: {
    backgroundColor: colors.danger
  },
  stepIndex: {
    display: "none"
  },
  screenContainer: {
    flex: 1,
    backgroundColor: "#000000"
  },
  bottomNav: {
    flexDirection: "row",
    backgroundColor: "#000000",
    borderTopWidth: 1,
    borderTopColor: colors.cardBorder,
    paddingVertical: 6,
    paddingHorizontal: 4,
    justifyContent: "space-around"
  },
  tabButton: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 6,
    position: "relative"
  },
  tabButtonActive: {
    backgroundColor: "#080C14",
    borderRadius: 8
  },
  activeIndicator: {
    position: "absolute",
    top: 0,
    width: 24,
    height: 2,
    backgroundColor: colors.primary,
    borderRadius: 1
  },
  activeIndicatorAlert: {
    backgroundColor: colors.danger
  },
  tabIcon: {
    fontSize: 18,
    marginBottom: 2
  },
  tabLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "600"
  },
  tabLabelActive: {
    color: colors.primary,
    fontWeight: "800"
  },
  tabLabelAlert: {
    color: colors.danger,
    fontWeight: "800"
  }
});
