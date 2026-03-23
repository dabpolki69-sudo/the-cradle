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
  LinearGradient,
} from 'react-native';

const API_BASE = 'http://localhost:5000';
const { width, height } = Dimensions.get('window');

// =======================
// COLOR SCHEME (Premium)
// =======================
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

// =======================
// MAIN APP
// =======================
export default function App() {
  const [worldState, setWorldState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentScreen, setCurrentScreen] = useState('world');
  const [selectedCitizen, setSelectedCitizen] = useState(null);
  const [dialogueResponse, setDialogueResponse] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const pulseAnim = React.useRef(new Animated.Value(0)).current;

  // Pulse animation for loading
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
      const response = await fetch(`${API_BASE}/api/world/init`, { method: 'POST', timeout: 5000 });
      if (!response.ok) throw new Error('Server unavailable');
      await fetchWorldState();
    } catch (error) {
      setConnectionStatus('disconnected');
      Alert.alert('Connection Error', 'Make sure backend is running on ' + API_BASE);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorldState = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/world/state`, { timeout: 5000 });
      if (!response.ok) throw new Error('Server error');
      const data = await response.json();
      if (!data.currentTick) throw new Error('Invalid state');
      setWorldState(data);
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Fetch error:', error);
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
      console.error('Tick error:', error);
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
      <LinearGradient
        colors={[Colors.surface, 'transparent']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
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
      </LinearGradient>

      {/* NAVIGATION */}
      <View style={styles.navBar}>
        <NavButton
          icon="🌍"
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
          icon="⚒️"
          label="Jobs"
          active={currentScreen === 'work'}
          onPress={() => setCurrentScreen('work')}
        />
        <NavButton
          icon="💰"
          label="Economy"
          active={currentScreen === 'market'}
          onPress={() => setCurrentScreen('market')}
        />
      </View>

      {/* CONTENT */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
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
        {currentScreen === 'work' && <WorkScreen worldState={worldState} />}
        {currentScreen === 'market' && <MarketScreen worldState={worldState} />}
      </ScrollView>
    </SafeAreaView>
  );
}

// =======================
// WORLD SCREEN
// =======================
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
        <ProgressBar
          label="Roads"
          value={worldState.infrastructure.roads}
          color={Colors.accent}
        />
        <ProgressBar
          label="Housing"
          value={worldState.infrastructure.housing}
          color={Colors.accentSecondary}
        />
        <ProgressBar
          label="Water"
          value={worldState.infrastructure.waterSystem}
          color={Colors.success}
        />
      </Card>

      <Card>
        <SectionSubHeader icon="💹" title="Economy" />
        <EconomyRow
          label="Unemployment"
          value={`${(worldState.economy.unemployment * 100).toFixed(1)}%`}
        />
        <EconomyRow
          label="Inflation"
          value={`${(worldState.economy.inflation * 100).toFixed(1)}%`}
        />
      </Card>

      {worldState.events.length > 0 && (
        <Card>
          <SectionSubHeader icon="📰" title="Recent Events" />
          {worldState.events.slice(-3).map((event, idx) => (
            <EventItem key={idx} event={event} />
          ))}
        </Card>
      )}

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

// =======================
// CITIZEN SCREEN
// =======================
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
        <SkillRow label="Socializing" value={citizen.skills.socializing} />
      </Card>

      <Card>
        <SectionSubHeader icon="🎭" title="Personality" />
        <TraitRow label="Humor" value={citizen.personality.humor} />
        <TraitRow label="Curiosity" value={citizen.personality.curiosity} />
        <TraitRow label="Friendliness" value={citizen.personality.friendliness} />
        <TraitRow label="Ambition" value={citizen.personality.ambition} />
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
        <InteractionButton
          label="Share news"
          onPress={() => onInteract(citizen.id, 'shared town news')}
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

// =======================
// WORK SCREEN
// =======================
function WorkScreen({ worldState }) {
  return (
    <View style={styles.screen}>
      <SectionHeader icon="⚒️" title="Available Work" />
      
      <Card>
        <Text style={styles.infoText}>
          Assign jobs to citizens to boost their skills and earn money for the town.
        </Text>
      </Card>

      {['farming', 'building', 'crafting'].map((job) => (
        <JobCard key={job} jobType={job} />
      ))}
    </View>
  );
}

// =======================
// MARKET SCREEN
// =======================
function MarketScreen({ worldState }) {
  return (
    <View style={styles.screen}>
      <SectionHeader icon="💰" title="Market Prices" />

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
        <Text style={styles.infoText}>
          Prices fluctuate based on supply and demand. Build a strong economy by managing resources wisely.
        </Text>
      </Card>
    </View>
  );
}

// =======================
// REUSABLE COMPONENTS
// =======================

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
  return (
    <View style={[styles.card, style]}>
      {children}
    </View>
  );
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
          style={[
            styles.progressBarFill,
            { width: `${value * 100}%`, backgroundColor: color },
          ]}
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
        <View
          style={[
            styles.needsBarFill,
            { width: `${value * 100}%`, backgroundColor: color },
          ]}
        />
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

function TraitRow({ label, value }) {
  const percent = Math.round(value * 100);
  const bar = '█'.repeat(Math.round(percent / 10)).padEnd(10, '░');
  return (
    <View style={styles.traitRow}>
      <Text style={styles.traitLabel}>{label}</Text>
      <Text style={styles.traitBar}>{bar}</Text>
      <Text style={styles.traitValue}>{percent}%</Text>
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

function EventItem({ event }) {
  const icons = {
    discovery: '🔍',
    accident: '⚠️',
    celebration: '🎉',
    conflict: '⚡',
    meeting: '🤝',
  };
  return (
    <View style={styles.eventItem}>
      <Text style={styles.eventIcon}>{icons[event.type] || '📝'}</Text>
      <Text style={styles.eventText}>{event.description}</Text>
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

function JobCard({ jobType }) {
  const icons = {
    farming: '🌾',
    building: '🏗️',
    crafting: '🔨',
  };
  const descriptions = {
    farming: 'Grow food and gather resources',
    building: 'Construct buildings and infrastructure',
    crafting: 'Create tools and items',
  };
  return (
    <Card>
      <View style={styles.jobCard}>
        <Text style={styles.jobIcon}>{icons[jobType]}</Text>
        <View style={{ flex: 1 }}>
          <Text style={styles.jobTitle}>
            {jobType.charAt(0).toUpperCase() + jobType.slice(1)}
          </Text>
          <Text style={styles.jobDescription}>{descriptions[jobType]}</Text>
        </View>
      </View>
    </Card>
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

// =======================
// STYLES (Premium Clean Design)
// =======================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // HEADER
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  appTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: Colors.accent,
    letterSpacing: 1,
  },
  logo: {
    fontSize: 64,
    marginBottom: 16,
  },
  timeInfo: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginTop: 4,
    fontFamily: 'monospace',
  },
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
  statusDot: (status) => ({
    fontSize: 12,
    color: status === 'connected' ? Colors.success : Colors.danger,
    marginRight: 6,
  }),
  statusText: {
    fontSize: 12,
    color: Colors.text,
    fontWeight: '600',
  },

  // NAVIGATION
  navBar: {
    flexDirection: 'row',
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  navButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  navButtonActive: {
    borderBottomColor: Colors.accent,
  },
  navIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  navLabel: {
    fontSize: 11,
    color: Colors.textSecondary,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  navLabelActive: {
    color: Colors.accent,
  },

  // CONTENT
  content: {
    flex: 1,
    paddingHorizontal: 12,
    paddingVertical: 12,
  },
  screen: {
    paddingBottom: 20,
  },

  // SECTIONS
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    marginTop: 8,
  },
  sectionIcon: {
    fontSize: 28,
    marginRight: 10,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: Colors.text,
    letterSpacing: 0.5,
  },
  sectionSubHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionSubTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.text,
  },

  // CARD
  card: {
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  dialogueCard: {
    backgroundColor: `${Colors.accentSecondary}20`,
    borderLeftWidth: 4,
    borderLeftColor: Colors.accentSecondary,
  },

  // STAT GRID
  statGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
    gap: 10,
  },
  statBox: {
    flex: 1,
    minWidth: '48%',
    backgroundColor: Colors.surfaceLight,
    borderRadius: 12,
    padding: 14,
    borderLeftWidth: 4,
    borderLeftColor: Colors.accent,
    alignItems: 'center',
  },
  statIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 4,
    fontWeight: '500',
  },
  statValue: {
    fontSize: 18,
    fontWeight: '700',
    color: Colors.accent,
  },

  // PROGRESS
  progressContainer: {
    marginBottom: 14,
  },
  progressLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  progressLabel: {
    fontSize: 13,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
  progressValue: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: '600',
  },
  progressBarBg: {
    height: 6,
    backgroundColor: Colors.surfaceLight,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },

  // NEEDS
  needsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  needsLabel: {
    flex: 1,
    fontSize: 13,
    color: Colors.text,
    fontWeight: '500',
  },
  needsBar: {
    flex: 2,
    height: 5,
    backgroundColor: Colors.surfaceLight,
    borderRadius: 2.5,
    marginHorizontal: 8,
    overflow: 'hidden',
  },
  needsBarFill: {
    height: '100%',
  },
  needsPercent: {
    fontSize: 11,
    color: Colors.textSecondary,
    fontWeight: '600',
    minWidth: 30,
    textAlign: 'right',
  },

  // SKILLS
  skillRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  skillLabel: {
    flex: 1,
    fontSize: 13,
    color: Colors.text,
    fontWeight: '500',
  },
  skillLevel: {
    flex: 1,
    fontSize: 12,
    color: Colors.accent,
    textAlign: 'center',
  },
  skillValue: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: '600',
    minWidth: 40,
    textAlign: 'right',
  },

  // TRAITS
  traitRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  traitLabel: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: '500',
    minWidth: 80,
  },
  traitBar: {
    flex: 1,
    fontSize: 10,
    color: Colors.accent,
    fontFamily: 'monospace',
    marginHorizontal: 8,
  },
  traitValue: {
    fontSize: 12,
    color: Colors.text,
    fontWeight: '600',
    minWidth: 35,
    textAlign: 'right',
  },

  // ECONOMY
  economyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  economyLabel: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  economyValue: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: '600',
  },

  // COMMODITIES
  commodityRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  commodityLabel: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: '500',
  },
  commodityPrice: {
    fontSize: 14,
    color: Colors.success,
    fontWeight: '700',
  },

  // EVENTS
  eventItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  eventIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  eventText: {
    flex: 1,
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 18,
  },

  // CITIZEN
  citizenCard: {
    backgroundColor: Colors.surfaceLight,
    borderTopWidth: 4,
    borderTopColor: Colors.accent,
  },
  citizenName: {
    fontSize: 20,
    fontWeight: '700',
    color: Colors.accent,
    marginBottom: 4,
  },
  citizenRole: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  citizenListItem: {
    backgroundColor: Colors.surface,
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: Colors.border,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  citizenListContent: {
    flex: 1,
  },
  citizenListName: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  citizenListStatus: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  citizenListChevron: {
    fontSize: 20,
    color: Colors.textSecondary,
  },
  backButton: {
    paddingVertical: 12,
    marginBottom: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: Colors.accent,
    fontWeight: '600',
  },

  // BUTTONS
  primaryButton: {
    backgroundColor: Colors.accent,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: Colors.accent,
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 5,
  },
  primaryButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: Colors.background,
    letterSpacing: 0.5,
  },
  interactionButton: {
    backgroundColor: Colors.surfaceLight,
    borderRadius: 8,
    paddingVertical: 11,
    paddingHorizontal: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  interactionButtonText: {
    fontSize: 13,
    color: Colors.text,
    fontWeight: '600',
    textAlign: 'center',
  },

  // JOBS
  jobCard: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  jobIcon: {
    fontSize: 36,
    marginRight: 12,
  },
  jobTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: Colors.text,
  },
  jobDescription: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
  },

  // DIALOGUE
  dialogueName: {
    fontSize: 14,
    fontWeight: '700',
    color: Colors.accentSecondary,
    marginBottom: 6,
  },
  dialogueText: {
    fontSize: 13,
    color: Colors.text,
    lineHeight: 18,
    fontStyle: 'italic',
  },

  // MISC
  loadingText: {
    fontSize: 16,
    color: Colors.textSecondary,
    marginTop: 12,
    letterSpacing: 0.5,
  },
  infoText: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
});
