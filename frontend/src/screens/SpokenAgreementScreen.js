import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView
} from "react-native";
import { colors } from "../theme/colors";
import { useApp } from "../context/AppContext";

export default function SpokenAgreementScreen({ onNavigate }) {
  const { contract, setContract } = useApp();
  const [isRecording, setIsRecording] = useState(false);
  const [isLocked, setIsLocked] = useState(contract.isLocked);
  const [activeTab, setActiveTab] = useState("terms"); // terms | audio

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      setTimeout(() => {
        setIsRecording(false);
      }, 4000);
    } else {
      setIsRecording(false);
    }
  };

  const lockContract = () => {
    setIsLocked(true);
    setContract((prev) => ({
      ...prev,
      isLocked: true,
      contractHash: "441868b822fa866779d478f6318be64ce9a4843c422622b9a7ddf88b627673be"
    }));
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.badgeRow}>
            <View style={styles.voiceBadge}>
              <Text style={styles.voiceBadgeText}>🎙️ NPU VOICE WITNESS</Text>
            </View>
            <Text style={styles.stepText}>STEP 2 OF 5</Text>
          </View>
          <Text style={styles.title}>Spoken Agreement</Text>
          <Text style={styles.subtitle}>
            Capture verbal commitments directly at the worksite. AI converts spoken words into a locked cryptographic contract.
          </Text>
        </View>

        {/* Prominent Microphone Capture Hero Card */}
        <View style={styles.micCard}>
          <Text style={styles.micStatusLabel}>
            {isRecording
              ? "🔴 LISTENING & TRANSCRIBING VERBAL TERMS..."
              : isLocked
              ? "🔒 CONTRACT TERMS CRYPTOGRAPHICALLY LOCKED"
              : "READY TO CAPTURE SPOKEN CONTRACT"}
          </Text>

          {/* Prominent Microphone Toggle Button */}
          <TouchableOpacity
            style={[
              styles.micButton,
              isRecording ? styles.micButtonRecording : styles.micButtonIdle
            ]}
            onPress={toggleRecording}
            activeOpacity={0.8}
          >
            <View style={styles.micIconContainer}>
              <Text style={styles.micEmoji}>{isRecording ? "⏹️" : "🎙️"}</Text>
            </View>
            {isRecording && <View style={styles.pulsingRing} />}
          </TouchableOpacity>

          <Text style={styles.micActionPrompt}>
            {isRecording
              ? "Tap to stop recording"
              : "Tap microphone to record spoken work agreement"}
          </Text>

          {/* Audio Waveform Equalizer Visualizer */}
          <View style={styles.waveformContainer}>
            {[8, 16, 28, 42, 24, 38, 50, 32, 18, 45, 22, 12, 34, 48, 20].map(
              (height, index) => (
                <View
                  key={index}
                  style={[
                    styles.waveBar,
                    {
                      height: isRecording ? Math.max(6, height) : 6,
                      backgroundColor: isRecording ? colors.warning : colors.border
                    }
                  ]}
                />
              )
            )}
          </View>
        </View>

        {/* Live Spoken Transcript Card */}
        <View style={styles.transcriptCard}>
          <View style={styles.transcriptHeader}>
            <Text style={styles.cardHeaderTitle}>SPEECH-TO-TEXT TRANSCRIPT</Text>
            <Text style={styles.langTag}>HINDI / ENGLISH NLP</Text>
          </View>
          <Text style={styles.transcriptText}>
            "{contract.audioTranscript}"
          </Text>
        </View>

        {/* Extracted Structured Contract Parameters */}
        <View style={styles.contractTermsCard}>
          <Text style={styles.cardHeaderTitle}>EXTRACTED LEGAL WORK TERMS</Text>

          <View style={styles.termGrid}>
            <View style={styles.termItem}>
              <Text style={styles.termLabel}>DAILY WAGE RATE</Text>
              <Text style={styles.termValueHighlight}>₹{contract.dailyRate} / day</Text>
            </View>

            <View style={styles.termItem}>
              <Text style={styles.termLabel}>CONTRACT DURATION</Text>
              <Text style={styles.termValue}>{contract.durationDays} Days</Text>
            </View>

            <View style={styles.termItem}>
              <Text style={styles.termLabel}>ASSIGNED TRADE</Text>
              <Text style={styles.termValue}>{contract.trade}</Text>
            </View>

            <View style={styles.termItem}>
              <Text style={styles.termLabel}>LOCKED WORK SITE</Text>
              <Text style={styles.termValueSmall}>{contract.siteLocation}</Text>
            </View>
          </View>
        </View>

        {/* Locked SHA-256 Hash Card */}
        <View style={styles.hashBadgeCard}>
          <View style={styles.hashRow}>
            <Text style={styles.hashBadgeLabel}>LOCKED CONTRACT SHA-256 HASH</Text>
            <View style={styles.tamperProofBadge}>
              <Text style={styles.tamperProofText}>IMMUTABLE</Text>
            </View>
          </View>
          <Text style={styles.hashText}>{contract.contractHash}</Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonGroup}>
          {!isLocked ? (
            <TouchableOpacity style={styles.lockButton} onPress={lockContract}>
              <Text style={styles.lockButtonText}>🔒 Lock Contract to Hash</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={styles.primaryActionButton}
              onPress={() => onNavigate && onNavigate("Attendance")}
            >
              <Text style={styles.primaryActionText}>
                Go to Attendance Terminal →
              </Text>
            </TouchableOpacity>
          )}
        </View>
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
  voiceBadge: {
    backgroundColor: colors.warningGlow,
    borderColor: colors.warning,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6
  },
  voiceBadgeText: {
    color: colors.warning,
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
  micCard: {
    backgroundColor: colors.card,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 22,
    alignItems: "center",
    marginBottom: 16
  },
  micStatusLabel: {
    color: colors.warning,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0.8,
    textAlign: "center",
    marginBottom: 18
  },
  micButton: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
    marginBottom: 14
  },
  micButtonIdle: {
    backgroundColor: colors.surface,
    borderColor: colors.warning,
    borderWidth: 3,
    shadowColor: colors.warning,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12
  },
  micButtonRecording: {
    backgroundColor: "#2E1500",
    borderColor: colors.danger,
    borderWidth: 3.5,
    shadowColor: colors.danger,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.8,
    shadowRadius: 16
  },
  micIconContainer: {
    justifyContent: "center",
    alignItems: "center"
  },
  micEmoji: {
    fontSize: 40
  },
  pulsingRing: {
    position: "absolute",
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: colors.warning,
    opacity: 0.6
  },
  micActionPrompt: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "600",
    marginBottom: 16
  },
  waveformContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    height: 50,
    width: "100%",
    gap: 4
  },
  waveBar: {
    width: 5,
    borderRadius: 3
  },
  transcriptCard: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginBottom: 16
  },
  transcriptHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10
  },
  cardHeaderTitle: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.8
  },
  langTag: {
    color: colors.purple,
    fontSize: 10,
    fontWeight: "700"
  },
  transcriptText: {
    color: colors.textPrimary,
    fontSize: 14,
    fontStyle: "italic",
    lineHeight: 22
  },
  contractTermsCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 16,
    marginBottom: 16
  },
  termGrid: {
    marginTop: 12,
    gap: 12
  },
  termItem: {
    backgroundColor: "#000000",
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.border
  },
  termLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.8,
    marginBottom: 4
  },
  termValue: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: "700"
  },
  termValueHighlight: {
    color: colors.success,
    fontSize: 18,
    fontWeight: "800"
  },
  termValueSmall: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "600"
  },
  hashBadgeCard: {
    backgroundColor: "#06151E",
    borderWidth: 1,
    borderColor: "#0E3A4E",
    borderRadius: 14,
    padding: 14,
    marginBottom: 20
  },
  hashRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6
  },
  hashBadgeLabel: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.8
  },
  tamperProofBadge: {
    backgroundColor: "#00F0FF22",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4
  },
  tamperProofText: {
    color: colors.primary,
    fontSize: 9,
    fontWeight: "800"
  },
  hashText: {
    color: "#CBD5E1",
    fontFamily: "monospace",
    fontSize: 12,
    lineHeight: 18
  },
  buttonGroup: {
    marginTop: 6
  },
  lockButton: {
    backgroundColor: colors.warning,
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center"
  },
  lockButtonText: {
    color: "#000000",
    fontSize: 15,
    fontWeight: "800",
    letterSpacing: 0.5
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
