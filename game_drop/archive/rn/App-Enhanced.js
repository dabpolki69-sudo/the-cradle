import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Dimensions,
  SafeAreaView,
  StatusBar,
  Animated,
} from 'react-native';
import {
  ASCIIWorldMap,
  SVGSettlementMap,
  EconomySparkline,
  CitizenHeatmap,
  TimeProgressionDial,
} from './VisualizationComponents';

const API_BASE = 'http://localhost:5000';
const { width, height } = Dimensions.get('window');

const Colors = {
  background: '#0a0e27',
  surface: '#1a1f3a',
  surfaceLight: '#242d4a',
  accent: '#00d4ff',
  accentSecondary: '#7c3aed',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  text: '#e0e7ff',
  textSecondary: '#a0aec0',
  border: '#334155',
};

export default function App() {
  const [worldState, setWorldState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentScreen, setCurrentScreen] = useState('visualization');
  const [selectedCitizen, setSelectedCitizen] = useState(null);
  const [dialogueResponse, setDialogueResponse] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [economyHistory, setEconomyHistory] = useState([]);
  const pulseAnim = React.useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1, duration: 1000, useNativeDriver: false }),
        Animated.timing(pulseAnim, { toValue: 0, duration: 1000, useNativeDriver: false }),
      ])
    ).start();
  }, [pulseAnim]);

  useEffect(() => {
    initializeWorld();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchWorldState, 2000);
    return () => clearInterval(interval);
  }, []);

  const initializeWorld = async () => {
    try {
      setLoading(true);
      setConnectionStatus('connecting');
      const response = await fetch(`${API_BASE}/api/world/init`, { method: 'POST' });
      if (!response.ok) throw new Error('Server unavailable');
      await fetchWorldState();
    } catch (error) {
      setConnectionStatus('disconnected');
      Alert.alert('Connection Error', 'Backend not running on ' + API_BASE);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorldState = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/world/state`);
      if (!response.ok) throw new Error('Server error');
      const data = await response.json();
      if (!data.currentTick) throw new Error('Invalid state');
      setWorldState(data);
      setConnectionStatus('connected');

      // Track economy history
      setEconomyHistory(prev => [...prev.slice(-29), {
        day: data.time.day,
        funds: data.economy.townHallFunds,
        employed: data.population.filter(c => c.job).length,
        stability: data.culture.stability,
      }]);
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const advanceTime = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/world/tick`, { method: 'POST' });
      const data = await response.json();
      setWorldState(data.worldState);
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const interactWithCitizen = async (citizenId, context) => {
    try {
      const response = await fetch(`${API_BASE}/api/citizen/${citizenId}/interact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context }),
      });
      const data = await response.json();
      setDialogueResponse({
        name: data.name,
        text: data.response,
        timestamp: Date.now(),
      });
    } catch (error) {
      setDialogueResponse({
        name: 'Error',
        text: 'Connection lost',
        timestamp: Date.now(),
      });
    }
  };

  if (loading || !worldState) {
    return (
      <View style={[styles.container, styles.center]}>
        <StatusBar barStyle="light-content" backgroundColor={Colors.background} />
        <Animated.View style={{ opacity: pulseAnim }}>
          <Text style={styles.logo}>🏛️</Text>
        </Animated.View>
        <Text style={styles.appTitle}>BREATH CITY</Text>
        <Text style={styles.loadingText}>Initializing civilization...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.background} />
      
      {/* HEADER */}
      <View style={styles.header}>
        <View>
          <Text style={styles.appTitle}>🏛️ BREATH CITY</Text>
          <Text style={styles.timeInfo}>
            Day {worldState.time.day} • {worldState.time.season} • Year {worldState.time.year}
          </Text>
        </View>
        <View style={styles.statusBadge(connectionStatus)}>
          <Text style={styles.statusDot(connectionStatus)}>●</Text>
          <Text style={styles.statusText}>
            {connectionStatus === 'connected' ? 'Online' : 'Offline'}
          </Text>
        </View>
      </View>

      {/* NAVIGATION */}
      <View style={styles.navBar}>
        <NavButton
          icon="🎨"
          label="Dashboard"
          active={currentScreen === 'visualization'}
          onPress={() => setCurrentScreen('visualization')}
        />
        <NavButton
          icon="🗺️"
          label="World"
          active={currentScreen === 'world'}
          onPress={() => setCurrentScreen('world')}
        />
        <NavButton
          icon="👥"
          label="Citizens"
          active={currentScreen === 'citizen'}
          onPress={() => setCurrentScreen('citizen')}
        />
        <NavButton
          icon="💰"
          label="Economy"
          active={currentScreen === 'economy'}
          onPress={() => setCurrentScreen('economy')}
        />
      </View>

      {/* CONTENT */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {currentScreen === 'visualization' && (
          <VisualizationDashboard
            worldState={worldState}
            economyHistory={economyHistory}
            onAdvanceTime={advanceTime}
          />
        )}
        {currentScreen === 'world' && (
          <WorldScreen
            worldState={worldState}
            onAdvanceTime={advanceTime}
            dialogueResponse={dialogueResponse}
          />
        )}
        {currentScreen === 'citizen' && (
          <CitizenScreen
            worldState={worldState}
            selectedCitizen={selectedCitizen}
            setSelectedCitizen={setSelectedCitizen}
            onInteract={interactWithCitizen}
            dialogueResponse={dialogueResponse}
          />
        )}
        {currentScreen === 'economy' && (
          <EconomyScreen worldState={worldState} economyHistory={economyHistory} />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ===== VISUALIZATION DASHBOARD =====

function VisualizationDashboard({ worldState, economyHistory, onAdvanceTime }) {
  return (
    <View style={styles.screen}>
      <SectionHeader icon="🎨" title="World Overview" />

      {/* ASCII World Map */}
      <View style={styles.asciiContainer}>
        <ASCIIWorldMap worldState={worldState} />
      </View>

      {/* Time Dial */}
      <View style={styles.dialContainer}>
        <TimeProgressionDial worldState={worldState} />
      </View>

      {/* Settlement Network */}
      <SectionHeader icon="🌍" title="Settlement Network" />
      <SVGSettlementMap worlds={[]} />

      {/* Economy Sparkline */}
      <SectionHeader icon="📈" title="Economy Trend" />
      <EconomySparkline worldState={worldState} history={economyHistory} />

      {/* Citizen Status Heatmap */}
      <SectionHeader icon="👥" title="Citizen Health" />
      <CitizenHeatmap population={worldState.population} />

      <PrimaryButton label="⏭️  Advance Day" onPress={onAdvanceTime} />
    </View>
  );
}

// ===== WORLD SCREEN =====

function WorldScreen({ worldState, onAdvanceTime, dialogueResponse }) {
  return (
    <View style={styles.screen}>
      <SectionHeader icon="📊" title="World Status" />

      <StatGrid>
        <StatBox
          icon="💰"
          label="Town Funds"
          value={`$${worldState.economy.townHallFunds}`}
          color={Colors.success}
        />
        <StatBox
          icon="👨‍💼"
          label="Population"
          value={worldState.population.length}
          color={Colors.accent}
        />
        <StatBox
          icon="😊"
          label="Morale"
          value={`${(worldState.culture.morale * 100).toFixed(0)}%`}
          color={Colors.accentSecondary}
        />
        <StatBox
          icon="🏢"
          label="Stability"
          value={`${(worldState.culture.stability * 100).toFixed(0)}%`}
          color={Colors.warning}
        />
      </StatGrid>

      <Card>
        <SectionSubHeader icon="🏗️" title="Infrastructure" />
        <ProgressBar label="Roads" value={worldState.infrastructure.roads} color={Colors.accent} />
        <ProgressBar label="Housing" value={worldState.infrastructure.housing} color={Colors.accentSecondary} />
        <ProgressBar label="Water" value={worldState.infrastructure.waterSystem} color={Colors.success} />
      </Card>

      <PrimaryButton label="⏭️  Advance Day" onPress={onAdvanceTime} />

      {dialogueResponse && (
        <Card style={styles.dialogueCard}>
          <Text style={styles.dialogueName}>{dialogueResponse.name}</Text>
          <Text style={styles.dialogueText}>"{dialogueResponse.text}"</Text>
        </Card>
      )}
    </View>
  );
}

// ===== CITIZEN SCREEN =====

function CitizenScreen({ worldState, selectedCitizen, setSelectedCitizen, onInteract, dialogueResponse }) {
  return (
    <View style={styles.screen}>
      {selectedCitizen === null ? (
        <>
          <SectionHeader icon="👥" title="Citizens" />
          {worldState.population.map((citizen) => (
            <CitizenListItem
              key={citizen.id}
              citizen={citizen}
              onPress={() => setSelectedCitizen(citizen.id)}
            />
          ))}
        </>
      ) : (
        <CitizenDetail
          citizen={worldState.population.find((c) => c.id === selectedCitizen)}
          onBack={() => setSelectedCitizen(null)}
          onInteract={onInteract}
          dialogueResponse={dialogueResponse}
        />
      )}
    </View>
  );
}

function CitizenDetail({ citizen, onBack, onInteract, dialogueResponse }) {
  return (
    <View style={styles.screen}>
      <TouchableOpacity onPress={onBack} style={styles.backButton}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>

      <Card style={styles.citizenCard}>
        <Text style={styles.citizenName}>{citizen.name}</Text>
        <Text style={styles.citizenRole}>
          {citizen.job ? `Working as ${citizen.job.type}` : 'Unemployed'}
        </Text>
      </Card>

      <Card>
        <SectionSubHeader icon="❤️" title="Needs" />
        <NeedsMeter label="Hunger" value={citizen.needs.hunger} color={Colors.warning} />
        <NeedsMeter label="Rest" value={citizen.needs.rest} color={Colors.accentSecondary} />
        <NeedsMeter label="Purpose" value={citizen.needs.purpose} color={Colors.accent} />
        <NeedsMeter label="Social" value={citizen.needs.social} color={Colors.success} />
      </Card>

      <Card>
        <SectionSubHeader icon="💪" title="Skills" />
        <SkillRow label="Building" value={citizen.skills.building} />
        <SkillRow label="Farming" value={citizen.skills.farming} />
        <SkillRow label="Crafting" value={citizen.skills.crafting} />
      </Card>

      <Card>
        <SectionSubHeader icon="💬" title="Interaction" />
        <InteractionButton
          label="Ask how they're doing"
          onPress={() => onInteract(citizen.id, 'asked how they are doing')}
        />
        <InteractionButton
          label="Ask about their job"
          onPress={() => onInteract(citizen.id, 'asked about their work')}
        />
      </Card>

      {dialogueResponse && (
        <Card style={styles.dialogueCard}>
          <Text style={styles.dialogueName}>{dialogueResponse.name}</Text>
          <Text style={styles.dialogueText}>"{dialogueResponse.text}"</Text>
        </Card>
      )}
    </View>
  );
}

// ===== ECONOMY SCREEN =====

function EconomyScreen({ worldState, economyHistory }) {
  return (
    <View style={styles.screen}>
      <SectionHeader icon="💹" title="Economy" />

      <Card>
        <SectionSubHeader icon="📊" title="Commodities" />
        {Object.entries(worldState.economy.commodityPrices).map(([commodity, price]) => (
          <CommodityRow
            key={commodity}
            label={commodity.charAt(0).toUpperCase() + commodity.slice(1)}
            price={price}
          />
        ))}
      </Card>

      <Card>
        <SectionSubHeader icon="📈" title="Trends" />
        <EconomyRow label="Unemployment" value={`${(worldState.economy.unemployment * 100).toFixed(1)}%`} />
        <EconomyRow label="Inflation" value={`${(worldState.economy.inflation * 100).toFixed(1)}%`} />
      </Card>

      <EconomySparkline worldState={worldState} history={economyHistory} />
    </View>
  );
}

// ===== REUSABLE COMPONENTS =====

function NavButton({ icon, label, active, onPress }) {
  return (
    <TouchableOpacity
      style={[styles.navButton, active && styles.navButtonActive]}
      onPress={onPress}
    >
      <Text style={styles.navIcon}>{icon}</Text>
      <Text style={[styles.navLabel, active && styles.navLabelActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

function Card({ children, style }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

function SectionHeader({ icon, title }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionIcon}>{icon}</Text>
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );
}

function SectionSubHeader({ icon, title }) {
  return (
    <View style={styles.sectionSubHeader}>
      <Text style={styles.sectionIcon}>{icon}</Text>
      <Text style={styles.sectionSubTitle}>{title}</Text>
    </View>
  );
}

function StatGrid({ children }) {
  return <View style={styles.statGrid}>{children}</View>;
}

function StatBox({ icon, label, value, color }) {
  return (
    <View style={[styles.statBox, { borderLeftColor: color }]}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
    </View>
  );
}

function ProgressBar({ label, value, color }) {
  return (
    <View style={styles.progressContainer}>
      <View style={styles.progressLabelRow}>
        <Text style={styles.progressLabel}>{label}</Text>
        <Text style={styles.progressValue}>{(value * 100).toFixed(0)}%</Text>
      </View>
      <View style={styles.progressBarBg}>
        <View
          style={[styles.progressBarFill, { width: `${value * 100}%`, backgroundColor: color }]}
        />
      </View>
    </View>
  );
}

function NeedsMeter({ label, value, color }) {
  const emoji = value > 0.75 ? '😫' : value > 0.5 ? '😐' : value > 0.25 ? '😊' : '😄';
  return (
    <View style={styles.needsRow}>
      <Text style={styles.needsLabel}>{emoji} {label}</Text>
      <View style={styles.needsBar}>
        <View style={[styles.needsBarFill, { width: `${value * 100}%`, backgroundColor: color }]} />
      </View>
      <Text style={styles.needsPercent}>{(value * 100).toFixed(0)}%</Text>
    </View>
  );
}

function SkillRow({ label, value }) {
  const level = value > 75 ? '★★★★★' : value > 50 ? '★★★★☆' : value > 25 ? '★★★☆☆' : '★★☆☆☆';
  return (
    <View style={styles.skillRow}>
      <Text style={styles.skillLabel}>{label}</Text>
      <Text style={styles.skillLevel}>{level}</Text>
      <Text style={styles.skillValue}>{value.toFixed(0)}</Text>
    </View>
  );
}

function EconomyRow({ label, value }) {
  return (
    <View style={styles.economyRow}>
      <Text style={styles.economyLabel}>{label}</Text>
      <Text style={styles.economyValue}>{value}</Text>
    </View>
  );
}

function CommodityRow({ label, price }) {
  return (
    <View style={styles.commodityRow}>
      <Text style={styles.commodityLabel}>{label}</Text>
      <Text style={styles.commodityPrice}>${price}</Text>
    </View>
  );
}

function CitizenListItem({ citizen, onPress }) {
  const status = citizen.job ? `Working: ${citizen.job.type}` : 'Unemployed';
  const mood = citizen.needs.hunger > 0.75 ? '😫' : '😊';
  return (
    <TouchableOpacity style={styles.citizenListItem} onPress={onPress}>
      <View style={styles.citizenListContent}>
        <View>
          <Text style={styles.citizenListName}>{mood} {citizen.name}</Text>
          <Text style={styles.citizenListStatus}>{status}</Text>
        </View>
      </View>
      <Text style={styles.citizenListChevron}>›</Text>
    </TouchableOpacity>
  );
}

function InteractionButton({ label, onPress }) {
  return (
    <TouchableOpacity style={styles.interactionButton} onPress={onPress}>
      <Text style={styles.interactionButtonText}>{label}</Text>
    </TouchableOpacity>
  );
}

function PrimaryButton({ label, onPress }) {
  return (
    <TouchableOpacity style={styles.primaryButton} onPress={onPress}>
      <Text style={styles.primaryButtonText}>{label}</Text>
    </TouchableOpacity>
  );
}

// ===== STYLES =====

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  center: { justifyContent: 'center', alignItems: 'center' },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  appTitle: { fontSize: 24, fontWeight: '700', color: Colors.accent, letterSpacing: 1 },
  logo: { fontSize: 64, marginBottom: 16 },
  timeInfo: { fontSize: 13, color: Colors.textSecondary, marginTop: 4, fontFamily: 'monospace' },
  statusBadge: (status) => ({
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: status === 'connected' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: status === 'connected' ? Colors.success : Colors.danger,
  }),
  statusDot: (status) => ({ fontSize: 12, color: status === 'connected' ? Colors.success : Colors.danger, marginRight: 6 }),
  statusText: { fontSize: 12, color: Colors.text, fontWeight: '600' },
  navBar: { flexDirection: 'row', backgroundColor: Colors.surface, borderBottomWidth: 1, borderBottomColor: Colors.border },
  navButton: { flex: 1, paddingVertical: 12, alignItems: 'center', borderBottomWidth: 3, borderBottomColor: 'transparent' },
  navButtonActive: { borderBottomColor: Colors.accent },
  navIcon: { fontSize: 24, marginBottom: 4 },
  navLabel: { fontSize: 11, color: Colors.textSecondary, fontWeight: '600' },
  navLabelActive: { color: Colors.accent },
  content: { flex: 1, paddingHorizontal: 12, paddingVertical: 12 },
  screen: { paddingBottom: 20 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16, marginTop: 8 },
  sectionIcon: { fontSize: 28, marginRight: 10 },
  sectionTitle: { fontSize: 22, fontWeight: '700', color: Colors.text, letterSpacing: 0.5 },
  sectionSubHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  sectionSubTitle: { fontSize: 16, fontWeight: '600', color: Colors.text },
  card: { backgroundColor: Colors.surface, borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: Colors.border },
  dialogueCard: { backgroundColor: `${Colors.accentSecondary}20`, borderLeftWidth: 4, borderLeftColor: Colors.accentSecondary },
  asciiContainer: { backgroundColor: Colors.surfaceLight, borderRadius: 8, padding: 8, marginBottom: 12, borderWidth: 1, borderColor: Colors.border },
  dialContainer: { alignItems: 'center', marginBottom: 16 },
  statGrid: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 12, gap: 10 },
  statBox: { flex: 1, minWidth: '48%', backgroundColor: Colors.surfaceLight, borderRadius: 12, padding: 14, borderLeftWidth: 4, alignItems: 'center' },
  statIcon: { fontSize: 32, marginBottom: 8 },
  statLabel: { fontSize: 12, color: Colors.textSecondary, marginBottom: 4, fontWeight: '500' },
  statValue: { fontSize: 18, fontWeight: '700' },
  progressContainer: { marginBottom: 14 },
  progressLabelRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  progressLabel: { fontSize: 13, color: Colors.textSecondary, fontWeight: '500' },
  progressValue: { fontSize: 13, color: Colors.text, fontWeight: '600' },
  progressBarBg: { height: 6, backgroundColor: Colors.surfaceLight, borderRadius: 3, overflow: 'hidden' },
  progressBarFill: { height: '100%', borderRadius: 3 },
  needsRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  needsLabel: { flex: 1, fontSize: 13, color: Colors.text, fontWeight: '500' },
  needsBar: { flex: 2, height: 5, backgroundColor: Colors.surfaceLight, borderRadius: 2.5, marginHorizontal: 8, overflow: 'hidden' },
  needsBarFill: { height: '100%' },
  needsPercent: { fontSize: 11, color: Colors.textSecondary, fontWeight: '600', minWidth: 30, textAlign: 'right' },
  skillRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: Colors.border },
  skillLabel: { flex: 1, fontSize: 13, color: Colors.text, fontWeight: '500' },
  skillLevel: { flex: 1, fontSize: 12, color: Colors.accent, textAlign: 'center' },
  skillValue: { fontSize: 13, color: Colors.text, fontWeight: '600', minWidth: 40, textAlign: 'right' },
  economyRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: Colors.border },
  economyLabel: { fontSize: 13, color: Colors.textSecondary },
  economyValue: { fontSize: 13, color: Colors.text, fontWeight: '600' },
  commodityRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: Colors.border },
  commodityLabel: { fontSize: 13, color: Colors.text, fontWeight: '500' },
  commodityPrice: { fontSize: 14, color: Colors.success, fontWeight: '700' },
  citizenCard: { backgroundColor: Colors.surfaceLight, borderTopWidth: 4, borderTopColor: Colors.accent },
  citizenName: { fontSize: 20, fontWeight: '700', color: Colors.accent, marginBottom: 4 },
  citizenRole: { fontSize: 13, color: Colors.textSecondary },
  citizenListItem: { backgroundColor: Colors.surface, borderRadius: 10, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: Colors.border, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  citizenListContent: { flex: 1 },
  citizenListName: { fontSize: 14, fontWeight: '600', color: Colors.text },
  citizenListStatus: { fontSize: 12, color: Colors.textSecondary, marginTop: 4 },
  citizenListChevron: { fontSize: 20, color: Colors.textSecondary },
  backButton: { paddingVertical: 12, marginBottom: 16 },
  backButtonText: { fontSize: 16, color: Colors.accent, fontWeight: '600' },
  primaryButton: { backgroundColor: Colors.accent, borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginBottom: 12 },
  primaryButtonText: { fontSize: 15, fontWeight: '700', color: Colors.background, letterSpacing: 0.5 },
  interactionButton: { backgroundColor: Colors.surfaceLight, borderRadius: 8, paddingVertical: 11, paddingHorizontal: 12, marginBottom: 8, borderWidth: 1, borderColor: Colors.border },
  interactionButtonText: { fontSize: 13, color: Colors.text, fontWeight: '600', textAlign: 'center' },
  dialogueName: { fontSize: 14, fontWeight: '700', color: Colors.accentSecondary, marginBottom: 6 },
  dialogueText: { fontSize: 13, color: Colors.text, lineHeight: 18, fontStyle: 'italic' },
  loadingText: { fontSize: 16, color: Colors.textSecondary, marginTop: 12, letterSpacing: 0.5 },
});

export { TimeProgressionDial, EconomySparkline, CitizenHeatmap, SVGSettlementMap };
