import React from "react";
import { View, StyleSheet } from "react-native";
import { registerRootComponent } from "expo";
import { AppProvider } from "./src/context/AppContext";
import AppNavigator from "./src/navigation/AppNavigator";

function App() {
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
    backgroundColor: "#000000"
  }
});

registerRootComponent(App);
export default App;
