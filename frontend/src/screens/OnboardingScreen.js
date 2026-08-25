import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView
} from "react-native";
import { colors } from "../theme/colors";
import { useApp } from "../context/AppContext";

export default function OnboardingScreen({ onNavigate }) {
  const { worker, setWorker } = useApp();
  const [name, setName] = useState(worker.name || "");
  const [trade, setTrade] = useState(worker.trade || "Master Mason");
  const [dob, setDob] = useState(worker.dob || "1994-08-15");
  const [scanning, setScanning] = useState(false);
  const [scanComplete, setScanComplete] = useState(true);

  const handleSimulateScan = () => {
    setScanning(true);
    setTimeout(() => {
      setScanning(false);
      setScanComplete(true);
      const generatedHash = "8f4a1c5b9e023478912bcdeff6541298710abcef1234567890abcdef12345678";
      setWorker((prev) => ({
        ...prev,
        name: name || "Ramesh Kumar",
        trade: trade || "Master Mason",
        dob: dob || "1994-08-15",
        idHash: generatedHash,
        isRegistered: true
      }));
    }, 1500);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.badgeRow}>
            <View style={styles.npuBadge}>
              <Text style={styles.npuBadgeText}>NPU SECURE ID</Text>
            </View>
            <Text style={styles.stepText}>STEP 1 OF 5</Text>
          </View>
          <Text style={styles.title}>Worker Onboarding</Text>
          <Text style={styles.subtitle}>
            Instant biometric identity hash registration. Zero physical paper required.
          </Text>
        </View>

        {/* Camera Viewfinder Placeholder for ID Scan */}
        <View style={styles.viewfinderCard}>
          <View style={styles.viewfinderHeader}>
            <Text style={styles.viewfinderTitle}>📷 ID SCAN VIEWFINDER</Text>
            <View style={styles.liveIndicator}>
              <View style={[styles.dot, scanning ? styles.dotScanning : styles.dotActive]} />
              <Text style={styles.liveText}>{scanning ? "SCANNING..." : "SENSOR READY"}</Text>
            </View>
          </View>

          {/* Viewfinder Target Area */}
          <View style={styles.viewfinderFrame}>
            {/* Viewfinder Corner Brackets */}
            <View style={[styles.corner, styles.cornerTL]} />
            <View style={[styles.corner, styles.cornerTR]} />
            <View style={[styles.corner, styles.cornerBL]} />
            <View style={[styles.corner, styles.cornerBR]} />

            {/* Viewfinder Center Content */}
            <View style={styles.viewfinderCenter}>
              <Text style={styles.viewfinderIcon}>{scanning ? "⚡" : "🪪"}</Text>
              <Text style={styles.viewfinderInstruction}>
                {scanning
                  ? "Extracting Government ID & Biometrics..."
                  : "Align Aadhaar / Labor Card inside frame"}
              </Text>
              {scanning && <View style={styles.scanLaser} />}
            </View>
          </View>

          {/* Scan Action Button */}
          <TouchableOpacity
            style={[styles.scanButton, scanning && styles.scanButtonDisabled]}
            onPress={handleSimulateScan}
            disabled={scanning}
          >
            <Text style={styles.scanButtonText}>
              {scanning ? "Processing Optical OCR..." : "⚡ Scan & Extract Identity"}
            </Text>
          </TouchableOpacity>
        </View>

        {/* SHA-256 Hash Badge Result */}
        {scanComplete && (
          <View style={styles.hashCard}>
            <View style={styles.hashHeaderRow}>
              <Text style={styles.hashLabel}>🔒 LOCKED WORKER ID HASH (SHA-256)</Text>
              <Text style={styles.verifiedTag}>✓ VERIFIED</Text>
            </View>
            <Text style={styles.hashValue} numberOfLines={2}>
              {worker.idHash}
            </Text>
            <Text style={styles.hashMeta}>
              Cryptographically derived • Stored strictly as a hash for total privacy
            </Text>
          </View>
        )}

        {/* Rapid Sign-Up Input Prompts */}
        <View style={styles.formCard}>
          <Text style={styles.formTitle}>Worker Profile Information</Text>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>FULL WORKER NAME</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Ramesh Arjun Kumar"
              placeholderTextColor={colors.textMuted}
              value={name}
              onChangeText={setName}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>PRIMARY TRADE / SPECIALTY</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Master Mason / Electrician"
              placeholderTextColor={colors.textMuted}
              value={trade}
              onChangeText={setTrade}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>DATE OF BIRTH (YYYY-MM-DD)</Text>
            <TextInput
              style={styles.input}
              placeholder="1994-08-15"
              placeholderTextColor={colors.textMuted}
              value={dob}
              onChangeText={setDob}
            />
          </View>
        </View>

        {/* Next Step Action Button */}
        <TouchableOpacity
          style={styles.primaryActionButton}
          onPress={() => onNavigate && onNavigate("Agreement")}
        >
          <Text style={styles.primaryActionText}>Continue to Spoken Agreement →</Text>
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
    marginBottom: 20
  },
  badgeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10
  },
  npuBadge: {
    backgroundColor: colors.primaryGlow,
    borderColor: colors.primary,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6
  },
  npuBadgeText: {
    color: colors.primary,
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
  viewfinderCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 16,
    marginBottom: 16
  },
  viewfinderHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14
  },
  viewfinderTitle: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 1
  },
  liveIndicator: {
    flexDirection: "row",
    alignItems: "center"
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6
  },
  dotActive: {
    backgroundColor: colors.success
  },
  dotScanning: {
    backgroundColor: colors.warning
  },
  liveText: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "600"
  },
  viewfinderFrame: {
    height: 180,
    backgroundColor: "#000000",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#1E293B",
    position: "relative",
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden"
  },
  corner: {
    position: "absolute",
    width: 24,
    height: 24,
    borderColor: colors.primary
  },
  cornerTL: {
    top: 10,
    left: 10,
    borderTopWidth: 3,
    borderLeftWidth: 3
  },
  cornerTR: {
    top: 10,
    right: 10,
    borderTopWidth: 3,
    borderRightWidth: 3
  },
  cornerBL: {
    bottom: 10,
    left: 10,
    borderBottomWidth: 3,
    borderLeftWidth: 3
  },
  cornerBR: {
    bottom: 10,
    right: 10,
    borderBottomWidth: 3,
    borderRightWidth: 3
  },
  viewfinderCenter: {
    alignItems: "center",
    paddingHorizontal: 20
  },
  viewfinderIcon: {
    fontSize: 36,
    marginBottom: 8
  },
  viewfinderInstruction: {
    color: colors.textSecondary,
    fontSize: 13,
    textAlign: "center",
    fontWeight: "500"
  },
  scanLaser: {
    width: 200,
    height: 2,
    backgroundColor: colors.primary,
    marginTop: 12,
    shadowColor: colors.primary,
    shadowOpacity: 1,
    shadowRadius: 10
  },
  scanButton: {
    backgroundColor: colors.surface,
    borderColor: colors.primary,
    borderWidth: 1.5,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 14
  },
  scanButtonDisabled: {
    opacity: 0.6
  },
  scanButtonText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 0.5
  },
  hashCard: {
    backgroundColor: "#06151E",
    borderWidth: 1,
    borderColor: "#0E3A4E",
    borderRadius: 14,
    padding: 14,
    marginBottom: 16
  },
  hashHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6
  },
  hashLabel: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.8
  },
  verifiedTag: {
    color: colors.success,
    fontSize: 11,
    fontWeight: "800"
  },
  hashValue: {
    color: "#E2E8F0",
    fontFamily: "monospace",
    fontSize: 12,
    lineHeight: 18,
    marginBottom: 6
  },
  hashMeta: {
    color: colors.textMuted,
    fontSize: 11
  },
  formCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 16,
    marginBottom: 20
  },
  formTitle: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 16
  },
  inputGroup: {
    marginBottom: 14
  },
  inputLabel: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.8,
    marginBottom: 6
  },
  input: {
    backgroundColor: "#000000",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: colors.textPrimary,
    fontSize: 14
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
