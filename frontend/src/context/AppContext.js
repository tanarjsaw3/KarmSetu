import React, { createContext, useState, useContext } from "react";

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // 1. Worker Profile
  const [worker, setWorker] = useState({
    idHash: "8f4a1c5b9e023478912bcdeff6541298710abcef1234567890abcdef12345678",
    name: "Ramesh Kumar",
    trade: "Master Mason / Concrete Specialist",
    dob: "1994-08-15",
    phone: "+91 98765 43210",
    isRegistered: true
  });

  // 2. Active Locked Contract
  const [contract, setContract] = useState({
    id: 1,
    workerName: "Ramesh Kumar",
    dailyRate: 850,
    durationDays: 30,
    trade: "Master Mason",
    siteLocation: "Metro Line 4 Pier Site, Mumbai (19.0760, 72.8777)",
    siteLat: 19.0760,
    siteLon: 72.8777,
    contractHash: "441868b822fa866779d478f6318be64ce9a4843c422622b9a7ddf88b627673be",
    isLocked: true,
    audioTranscript: "I, Contractor Verma, agree to hire Ramesh Kumar as Master Mason at INR 850 per day for 30 days at Metro Line 4 Site, Mumbai with weekly disbursements."
  });

  // 3. Verified Attendance Logs
  const [attendanceLogs, setAttendanceLogs] = useState([
    {
      id: 1,
      date: "2026-08-20",
      time: "08:30 AM",
      coords: "19.076012, 72.877715",
      distanceMeters: 4.2,
      livenessPassed: true,
      status: "VERIFIED"
    },
    {
      id: 2,
      date: "2026-08-21",
      time: "08:28 AM",
      coords: "19.076020, 72.877708",
      distanceMeters: 5.1,
      livenessPassed: true,
      status: "VERIFIED"
    },
    {
      id: 3,
      date: "2026-08-22",
      time: "08:31 AM",
      coords: "19.075995, 72.877690",
      distanceMeters: 6.8,
      livenessPassed: true,
      status: "VERIFIED"
    },
    {
      id: 4,
      date: "2026-08-23",
      time: "08:25 AM",
      coords: "19.076008, 72.877722",
      distanceMeters: 3.5,
      livenessPassed: true,
      status: "VERIFIED"
    },
    {
      id: 5,
      date: "2026-08-24",
      time: "08:29 AM",
      coords: "19.076015, 72.877705",
      distanceMeters: 4.9,
      livenessPassed: true,
      status: "VERIFIED"
    }
  ]);

  // 4. Financial & Payment Audit State
  const [paymentAudit, setPaymentAudit] = useState({
    receivedAmount: 2500, // Partial payment received
    disputeActive: true
  });

  // Derived financial metrics
  const verifiedWorkdays = attendanceLogs.filter(l => l.livenessPassed).length;
  const totalHoursWorked = verifiedWorkdays * 8.5; // Average 8.5 hrs/day
  const expectedEarnings = verifiedWorkdays * contract.dailyRate;
  const receivedAmount = paymentAudit.receivedAmount;
  const deficitAmount = Math.max(0, expectedEarnings - receivedAmount);
  const isDeficit = deficitAmount > 0;

  // Actions
  const addAttendance = (newLog) => {
    setAttendanceLogs((prev) => [newLog, ...prev]);
  };

  const updateReceivedPayment = (amount) => {
    setPaymentAudit({
      receivedAmount: parseFloat(amount) || 0,
      disputeActive: (expectedEarnings - (parseFloat(amount) || 0)) > 0
    });
  };

  return (
    <AppContext.Provider
      value={{
        worker,
        setWorker,
        contract,
        setContract,
        attendanceLogs,
        addAttendance,
        paymentAudit,
        updateReceivedPayment,
        verifiedWorkdays,
        totalHoursWorked,
        expectedEarnings,
        receivedAmount,
        deficitAmount,
        isDeficit
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
