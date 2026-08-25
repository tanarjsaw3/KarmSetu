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

export default function WalletDashboardScreen({ onNavigate }) {
  const {
    contract,
    verifiedWorkdays,
    totalHoursWorked,
    expectedEarnings,
    receivedAmount,
    deficitAmount,
    isDeficit,
    updateReceivedPayment
  } = useApp();

  const [inputPayment, setInputPayment] = useState(receivedAmount.toString());

  const handleUpdatePayment = (val) => {
    setInputPayment(val);
    updateReceivedPayment(val);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.badgeRow}>
            <View style={styles.walletBadge}>
              <Text style={styles.walletBadgeText}>💰 WAGE AUDIT VAULT</Text>
            </View>
            <Text style={styles.stepText}>STEP 4 OF 5</Text>
          </View>
          <Text style={styles.title}>Wallet & Earnings</Text>
          <Text style={styles.subtitle}>
            Continuous automated reconciliation between verified physical work and received bank payments.
          </Text>
        </View>

        {/* Main Earnings Balance Card */}
        <View
          style={[
            styles.balanceHeroCard,
            isDeficit ? styles.heroDeficit : styles.heroCompliant
          ]}
        >
          <Text style={styles.balanceLabel}>TOTAL VERIFIED EARNINGS DUE</Text>
          <Text style={styles.balanceAmount}>
            ₹{expectedEarnings.toLocaleString("en-IN")}
          </Text>
          <Text style={styles.balanceBreakdown}>
            Based on {verifiedWorkdays} verified workdays @ ₹{contract.dailyRate}/day
          </Text>

          {/* Audit Status Tag */}
          <View
            style={[
              styles.auditTag,
              isDeficit ? styles.auditTagDeficit : styles.auditTagCompliant
            ]}
          >
            <Text
              style={[
                styles.auditTagText,
                isDeficit ? styles.auditTextDeficit : styles.auditTextCompliant
              ]}
            >
              {isDeficit
                ? "🚨 WAGE THEFT ALERT (UNPAID DEFICIT)"
                : "✓ 100% COMPLIANT & FULLY SETTLED"}
            </Text>
          </View>
        </View>

        {/* High-Contrast AMOLED Metric Grid (4-Box Grid) */}
        <View style={styles.metricGrid}>
          {/* Box 1: Verified Hours */}
          <View style={styles.metricCard}>
            <Text style={styles.metricIcon}>⏱️</Text>
            <Text style={styles.metricValue}>{totalHoursWorked.toFixed(1)} hrs</Text>
            <Text style={styles.metricLabel}>HOURS WORKED</Text>
          </View>

          {/* Box 2: Verified Workdays */}
          <View style={styles.metricCard}>
            <Text style={styles.metricIcon}>📅</Text>
            <Text style={styles.metricValue}>{verifiedWorkdays} Days</Text>
            <Text style={styles.metricLabel}>VERIFIED DAYS</Text>
          </View>

          {/* Box 3: Daily Locked Rate */}
          <View style={styles.metricCard}>
            <Text style={styles.metricIcon}>🏷️</Text>
            <Text style={styles.metricValue}>₹{contract.dailyRate}</Text>
            <Text style={styles.metricLabel}>DAILY RATE</Text>
          </View>

          {/* Box 4: Current Deficit */}
          <View style={[styles.metricCard, isDeficit && styles.metricCardDeficit]}>
            <Text style={styles.metricIcon}>{isDeficit ? "⚠️" : "🛡️"}</Text>
            <Text
              style={[
                styles.metricValue,
                isDeficit ? styles.deficitValue : styles.compliantValue
              ]}
            >
              ₹{deficitAmount.toLocaleString("en-IN")}
            </Text>
            <Text style={styles.metricLabel}>DEFICIT</Text>
          </View>
        </View>

        {/* Payment Audit Breakdown Card */}
        <View style={styles.auditCard}>
          <Text style={styles.cardHeaderTitle}>FINANCIAL RECONCILIATION AUDIT</Text>

          <View style={styles.auditRow}>
            <Text style={styles.auditRowLabel}>Expected Total Wage</Text>
            <Text style={styles.auditRowValue}>
              ₹{expectedEarnings.toLocaleString("en-IN")}
            </Text>
          </View>

          <View style={styles.auditRow}>
            <Text style={styles.auditRowLabel}>Actual Disbursed Payment</Text>
            <Text style={styles.auditRowValueSecondary}>
              ₹{receivedAmount.toLocaleString("en-IN")}
            </Text>
          </View>

          <View style={styles.divider} />

          <View style={styles.auditRow}>
            <Text
              style={[
                styles.auditRowLabelBold,
                isDeficit ? styles.textDeficit : styles.textSuccess
              ]}
            >
              {isDeficit ? "Underpayment Deficit" : "Surplus / Fully Paid"}
            </Text>
            <Text
              style={[
                styles.auditRowValueBold,
                isDeficit ? styles.textDeficit : styles.textSuccess
              ]}
            >
              {isDeficit
                ? `- ₹${deficitAmount.toLocaleString("en-IN")}`
                : "₹0.00 (Settled)"}
            </Text>
          </View>
        </View>

        {/* Incoming Payment Audit Simulator (Interactive) */}
        <View style={styles.simulatorCard}>
          <Text style={styles.cardHeaderTitle}>
            💳 TEST INCOMING PAYMENT DISBURSEMENT
          </Text>
          <Text style={styles.simDescription}>
            Enter an actual payment received to trigger automated wage audit.
          </Text>

          <View style={styles.simInputRow}>
            <Text style={styles.currencyPrefix}>₹</Text>
            <TextInput
              style={styles.simInput}
              keyboardType="numeric"
              value={inputPayment}
              onChangeText={handleUpdatePayment}
              placeholder="Enter amount"
              placeholderTextColor={colors.textMuted}
            />
            <TouchableOpacity
              style={styles.quickFillButton}
              onPress={() => handleUpdatePayment(expectedEarnings.toString())}
            >
              <Text style={styles.quickFillText}>Full Pay</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.quickShortButton}
              onPress={() => handleUpdatePayment((expectedEarnings * 0.6).toString())}
            >
              <Text style={styles.quickShortText}>Short 40%</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Action Button to Dispute Terminal if Deficit, or Dispute Review */}
        <TouchableOpacity
          style={[
            styles.actionButton,
            isDeficit ? styles.actionButtonDeficit : styles.actionButtonCompliant
          ]}
          onPress={() => onNavigate && onNavigate("Dispute")}
        >
          <Text style={styles.actionButtonText}>
            {isDeficit
              ? "🚨 Open Dispute Terminal & Generate Evidence →"
              : "Review Dispute & Legal Evidence Vault →"}
          </Text>
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
  walletBadge: {
    backgroundColor: colors.primaryGlow,
    borderColor: colors.primary,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6
  },
  walletBadgeText: {
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
  balanceHeroCard: {
    backgroundColor: colors.card,
    borderRadius: 20,
    borderWidth: 1.5,
    padding: 20,
    marginBottom: 16
  },
  heroDeficit: {
    borderColor: colors.danger,
    backgroundColor: "#16050A"
  },
  heroCompliant: {
    borderColor: colors.success,
    backgroundColor: "#05160E"
  },
  balanceLabel: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 0.8,
    marginBottom: 6
  },
  balanceAmount: {
    color: colors.textPrimary,
    fontSize: 34,
    fontWeight: "900",
    letterSpacing: 0.5
  },
  balanceBreakdown: {
    color: colors.textMuted,
    fontSize: 12,
    marginTop: 4,
    marginBottom: 14
  },
  auditTag: {
    alignSelf: "flex-start",
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 6,
    borderWidth: 1
  },
  auditTagDeficit: {
    backgroundColor: colors.dangerGlow,
    borderColor: colors.danger
  },
  auditTagCompliant: {
    backgroundColor: colors.successGlow,
    borderColor: colors.success
  },
  auditTagText: {
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 0.5
  },
  auditTextDeficit: {
    color: colors.danger
  },
  auditTextCompliant: {
    color: colors.success
  },
  metricGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
    marginBottom: 16
  },
  metricCard: {
    width: "48%",
    backgroundColor: colors.card,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 14
  },
  metricCardDeficit: {
    borderColor: "#551A25",
    backgroundColor: "#1A080C"
  },
  metricIcon: {
    fontSize: 20,
    marginBottom: 8
  },
  metricValue: {
    color: colors.textPrimary,
    fontSize: 18,
    fontWeight: "800"
  },
  deficitValue: {
    color: colors.danger
  },
  compliantValue: {
    color: colors.success
  },
  metricLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.8,
    marginTop: 4
  },
  auditCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    padding: 16,
    marginBottom: 16
  },
  cardHeaderTitle: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.8,
    marginBottom: 12
  },
  auditRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 6
  },
  auditRowLabel: {
    color: colors.textSecondary,
    fontSize: 13
  },
  auditRowValue: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "700"
  },
  auditRowValueSecondary: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "700"
  },
  divider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: 8
  },
  auditRowLabelBold: {
    fontSize: 14,
    fontWeight: "800"
  },
  auditRowValueBold: {
    fontSize: 16,
    fontWeight: "800"
  },
  textDeficit: {
    color: colors.danger
  },
  textSuccess: {
    color: colors.success
  },
  simulatorCard: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginBottom: 20
  },
  simDescription: {
    color: colors.textMuted,
    fontSize: 12,
    marginBottom: 12
  },
  simInputRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8
  },
  currencyPrefix: {
    color: colors.textSecondary,
    fontSize: 18,
    fontWeight: "700"
  },
  simInput: {
    flex: 1,
    backgroundColor: "#000000",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "700"
  },
  quickFillButton: {
    backgroundColor: "#0F2B1D",
    borderColor: colors.success,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 8
  },
  quickFillText: {
    color: colors.success,
    fontSize: 11,
    fontWeight: "700"
  },
  quickShortButton: {
    backgroundColor: "#2B0F15",
    borderColor: colors.danger,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 8
  },
  quickShortText: {
    color: colors.danger,
    fontSize: 11,
    fontWeight: "700"
  },
  actionButton: {
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center"
  },
  actionButtonDeficit: {
    backgroundColor: colors.danger,
    shadowColor: colors.danger,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 10
  },
  actionButtonCompliant: {
    backgroundColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8
  },
  actionButtonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "800",
    letterSpacing: 0.5
  }
});
