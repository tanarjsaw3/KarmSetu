import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  ActivityIndicator
} from "react-native";
import { colors } from "../theme/colors";
import { useApp } from "../context/AppContext";

export default function AttendanceScreen({ onNavigate }) {
  const { contract, attendanceLogs, addAttendance } = useApp();
  const [isVerifying, setIsVerifying] = useState(false);
  const [checkinStatus, setCheckinStatus] = useState(null); // null | success | error

  const handleSimulateCheckIn = () => {
    setIsVerifying(true);
    setCheckinStatus(null);

    setTimeout(() => {
      setIsVerifying(false);
      setCheckinStatus("success");

      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      const dateStr = now.toISOString().split("T")[0];

      const newEntry = {
        id: Date.now(),
        date: dateStr,
        time: timeStr,
        coords: "19.076032, 72.877710",
        distanceMeters: 4.6,
        livenessPassed: true,
        status: "VERIFIED"
      };
      addAttendance(newEntry);
    }, 2000);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.badgeRow}>
            <View style={styles.geoBadge}>
              <Text style={styles.geoBadgeText}>📍 GEOFENCE + BIOMETRIC WITNESS</Text>
            </View>
            <Text style={styles.stepText}>STEP 3 OF 5</Text>
          </View>
          <Text style={styles.title}>Daily Attendance</Text>
          <Text style={styles.subtitle}>
            One-tap verified workday logging. NPU verifies facial liveness and locks GPS coordinates directly to SQLite ledger.
          </Text>
        </View>

        {/* Locked Site Information Card */}
        <View style={styles.siteCard}>
          <View style={styles.siteHeader}>
            <Text style={styles.cardHeaderTitle}>AUTHORIZED SITE LOCATION</Text>
            <Text style={styles.lockedTag}>🔒 LOCKED GEOFENCE</Text>
          </View>
          <Text style={styles.siteName}>{contract.siteLocation}</Text>
          <Text style={styles.siteCoords}>
            Target GPS: {contract.siteLat.toFixed(4)}, {contract.siteLon.toFixed(4)} (Max radius: 1,500m)
          </Text>
        </View>

        {/* Prominent Check-In Hero Card */}
        <View style={styles.checkinCard}>
          <Text style={styles.checkinPromptTitle}>
            {isVerifying
              ? "⚡ VERIFYING BIOMETRICS & GPS SENSORS..."
              : checkinStatus === "success"
              ? "✓ TODAY'S WORKDAY OFFICIALLY VERIFIED"
              : "READY FOR DAILY WORKDAY LOGGING"}
          </Text>

          {/* Large Visual Check-In Button */}
          <TouchableOpacity
            style={[
              styles.checkinButton,
              isVerifying
                ? styles.checkinButtonVerifying
                : checkinStatus === "success"
                ? styles.checkinButtonSuccess
                : styles.checkinButtonReady
            ]}
            onPress={handleSimulateCheckIn}
            disabled={isVerifying}
            activeOpacity={0.85}
          >
            {isVerifying ? (
              <ActivityIndicator size="large" color={colors.primary} />
            ) : (
              <View style={styles.checkinInner}>
                <Text style={styles.checkinEmoji}>
                  {checkinStatus === "success" ? "✓" : "⚡"}
                </Text>
                <Text style={styles.checkinButtonText}>
                  {checkinStatus === "success" ? "CHECKED IN" : "CHECK-IN NOW"}
                </Text>
              </View>
            )}
          </TouchableOpacity>

          {/* Dual Verification Feedback Badges */}
          <View style={styles.verificationRow}>
            {/* Liveness Check Card */}
            <View style={styles.verifyItem}>
              <Text style={styles.verifyItemIcon}>👁️</Text>
              <View>
                <Text style={styles.verifyItemLabel}>FACIAL LIVENESS</Text>
                <Text style={styles.verifyItemStatus}>
                  {isVerifying ? "ANALYZING..." : "PASS (NPU VERIFIED)"}
                </Text>
              </View>
            </View>

            {/* GPS Geofence Check Card */}
            <View style={styles.verifyItem}>
              <Text style={styles.verifyItemIcon}>📡</Text>
              <View>
                <Text style={styles.verifyItemLabel}>SITE PROXIMITY</Text>
                <Text style={styles.verifyItemStatus}>
                  {isVerifying ? "LOCATING..." : "4.6m (INSIDE GEOFENCE)"}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Verified Attendance Ledger Log Feed */}
        <View style={styles.ledgerCard}>
          <View style={styles.ledgerHeader}>
            <Text style={styles.cardHeaderTitle}>VERIFIED ATTENDANCE LOGS</Text>
            <Text style={styles.ledgerCountBadge}>
              {attendanceLogs.length} DAYS LOGGED
            </Text>
          </View>

          {attendanceLogs.map((log, index) => (
            <View key={log.id || index} style={styles.logItem}>
              <View style={styles.logLeft}>
                <View style={styles.logStatusDot} />
                <View>
                  <Text style={styles.logDate}>
                    {log.date} • {log.time}
                  </Text>
                  <Text style={styles.logCoords}>GPS: {log.coords}</Text>
                </View>
              </View>
              <View style={styles.logRight}>
                <Text style={styles.logDistance}>~{log.distanceMeters}m away</Text>
                <View style={styles.verifiedTagBadge}>
                  <Text style={styles.verifiedTagText}>✓ VERIFIED</Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        {/* Next Step Action Button */}
        <TouchableOpacity
          style={styles.primaryActionButton}
          onPress={() => onNavigate && onNavigate("Wallet")}
        >
          <Text style={styles.primaryActionText}>View Wallet & Earnings Dashboard →</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background
  },
  container: {
    padding: 20,
    paddingBottom: 40
  },
  header: {
    marginBottom: 18
  },
  badgeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8
  },
  geoBadge: {
    backgroundColor: colors.successGlow,
    borderColor: colors.success,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6
  },
  geoBadgeText: {
    color: colors.success,
    fontSize: 11,
    fontWeight: "bold",
    letterSpacing: 1
  },
  stepText: {
    color: colors.textMuted,
    fontSize: 12,
    fontWeight: "600"
  },
  title: {
    color: colors.textPrimary,
    fontSize: 26,
    fontWeight: "800",
    letterSpacing: 0.5
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: 14,
    marginTop: 6,
    lineHeight: 20
  },
  siteCard: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 14,
    marginBottom: 16
  },
  siteHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6
  },
  cardHeaderTitle: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.8
  },
  lockedTag: {
    color: colors.primary,
    fontSize: 10,
    fontWeight: "700"
  },
  siteName: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 4
  },
  siteCoords: {
    color: colors.textMuted,
    fontSize: 12
  },
  checkinCard: {
    backgroundColor: colors.card,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 22,
    alignItems: "center",
    marginBottom: 16
  },
  checkinPromptTitle: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0.8,
    textAlign: "center",
    marginBottom: 18
  },
  checkinButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20
  },
  checkinButtonReady: {
    backgroundColor: colors.surface,
    borderColor: colors.primary,
    borderWidth: 4,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.5,
    shadowRadius: 16
  },
  checkinButtonVerifying: {
    backgroundColor: "#0A1E28",
    borderColor: colors.primary,
    borderWidth: 4
  },
  checkinButtonSuccess: {
    backgroundColor: "#062816",
    borderColor: colors.success,
    borderWidth: 4,
    shadowColor: colors.success,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.6,
    shadowRadius: 16
  },
  checkinInner: {
    alignItems: "center"
  },
  checkinEmoji: {
    fontSize: 36,
    marginBottom: 4
  },
  checkinButtonText: {
    color: colors.textPrimary,
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 0.8
  },
  verificationRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "100%",
    gap: 10
  },
  verifyItem: {
    flex: 1,
    backgroundColor: "#000000",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 10,
    flexDirection: "row",
    alignItems: "center",
    gap: 8
  },
  verifyItemIcon: {
    fontSize: 20
  },
  verifyItemLabel: {
    color: colors.textMuted,
    fontSize: 9,
    fontWeight: "700"
  },
  verifyItemStatus: {
    color: colors.success,
    fontSize: 11,
    fontWeight: "700"
  },
  ledgerCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 16,
    marginBottom: 20
  },
  ledgerHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12
  },
  ledgerCountBadge: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: "700"
  },
  logItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  logLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10
  },
  logStatusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.success
  },
  logDate: {
    color: colors.textPrimary,
    fontSize: 13,
    fontWeight: "700"
  },
  logCoords: {
    color: colors.textMuted,
    fontSize: 11,
    marginTop: 2
  },
  logRight: {
    alignItems: "flex-end"
  },
  logDistance: {
    color: colors.textSecondary,
    fontSize: 11,
    marginBottom: 4
  },
  verifiedTagBadge: {
    backgroundColor: "#00FF8822",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4
  },
  verifiedTagText: {
    color: colors.success,
    fontSize: 10,
    fontWeight: "800"
  },
  primaryActionButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center",
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8
  },
  primaryActionText: {
    color: colors.textInverse,
    fontSize: 15,
    fontWeight: "800",
    letterSpacing: 0.5
  }
});
