import React from "react";
import { View, StyleSheet, ActivityIndicator } from "react-native";
import { registerRootComponent } from "expo";
import { AppProvider } from "./src/context/AppContext";
import AppNavigator from "./src/navigation/AppNavigator";
import { useFonts, Inter_400Regular } from "@expo-google-fonts/inter";

function App() {
  const [fontsLoaded] = useFonts({ Inter_400Regular });

  if (!fontsLoaded) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0D9488" />
      </View>
    );
  }

  return (
    <AppProvider>
      <View style={styles.container}>
        <AppNavigator />
      </View>
    </AppProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F7FA" // light background from theme
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#F5F7FA"
  }
});

registerRootComponent(App);
export default App;
