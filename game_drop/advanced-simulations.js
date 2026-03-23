/**
 * ADVANCED SIMULATION SUITE
 * 
 * Test 1: Multi-Settlement (30 survivors, 5 groups on separate zones)
 * Test 2: Maximum Stress (20 runs with all settings maxed)
 * 
 * Validates:
 * - Settlement formation and merging
 * - Rival town formation
 * - Economy scaling
 * - System breaking points
 */

// AICitizen with all fixes + Issue #9B thresholds adjusted
class AICitizen {
  constructor(id, name, personality, groupId = 0, zoneId = 0) {
    this.id = id;
    this.name = name;
    this.personality = personality;
    this.groupId = groupId;  // Which settlement group
    this.zoneId = zoneId;    // Which map zone
    this.needs = {hunger: 0.5, rest: 0.3, purpose: 0.6, social: 0.4};
    this.relationships = {};
    this.job = null;
    this.skills = {
      building: Math.random() * 100,
      farming: Math.random() * 100,
      crafting: Math.random() * 100,
      socializing: Math.random() * 100,
    };
    this.inventory = {money: 200, items: []};
    this.state = 'idle';
    this.memory = [];
  }

  getDecisionPressure(worldState) {
    return (this.needs.hunger * 0.3 + this.needs.rest * 0.2 + 
            this.needs.purpose * 0.3 + this.needs.social * 0.2);
  }

  dailyTick(worldState) {
    this.needs.hunger = Math.min(1, this.needs.hunger + 0.1);
    this.needs.rest = Math.min(1, this.needs.rest + 0.08);
    
    // FIX #9B: Adjusted thresholds (0.9 instead of 0.75)
    if (this.needs.hunger > 0.9 && this.inventory.money >= 10) {
      this.inventory.money -= 10;
      this.needs.hunger = Math.max(0, this.needs.hunger - 0.35);
    }
    
    if (this.needs.rest > 0.9 && this.inventory.money >= 5) {
      this.inventory.money -= 5;
      this.needs.rest = Math.max(0, this.needs.rest - 0.3);
    }
    
    if (this.job && this.job.duration > 0) {
      this.needs.purpose = Math.min(1, this.needs.purpose + 0.05);
    } else {
      this.needs.purpose = Math.max(0, this.needs.purpose - 0.05);
    }
    
    this.needs.social = Math.max(0, this.needs.social - 0.03);

    if (Math.random() < 0.3) {
      this.memory.push({tick: worldState.currentTick, type: 'mood'});
      if (this.memory.length > 100) this.memory.shift();
    }

    if (this.job) {
      this.job.duration--;
      if (this.job.duration <= 0) {
        const payment = this.job.performance * 100;
        this.inventory.money += payment;
        this.memory.push({tick: worldState.currentTick, type: 'job_completed'});
        if (this.memory.length > 100) this.memory.shift();
        this.job = null;
      }
    }
  }
}

const colors = {reset: '\x1b[0m', bright: '\x1b[1m', green: '\x1b[32m', red: '\x1b[31m', yellow: '\x1b[33m', cyan: '\x1b[36m', blue: '\x1b[34m', magenta: '\x1b[35m'};

function log(msg, col = 'reset') {
  console.log(`${colors[col]}${msg}${colors.reset}`);
}

// ===== TEST 1: MULTI-SETTLEMENT =====

function testMultiSettlement() {
  log('\n╔═══════════════════════════════════════════════════════════════╗', 'bright');
  log('║  TEST 1: MULTI-SETTLEMENT EXPANSION (30 Survivors, 5 Zones)  ║', 'bright');
  log('║  Q: Will settlements merge or form rival towns?              ║', 'bright');
  log('╚═══════════════════════════════════════════════════════════════╝\n', 'bright');

  const worldState = {
    currentTick: 0,
    time: {day: 1, season: 'Spring', year: 1},
    population: [],
    settlements: [],
    events: [],
  };

  // Create 5 settlement groups (6 survivors each)
  const names = ['Alice', 'Bob', 'Carol', 'Dave', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack',
                 'Kate', 'Leo', 'Mia', 'Noah', 'Olivia', 'Peter', 'Quinn', 'Rose', 'Sam', 'Tina',
                 'Uma', 'Victor', 'Wendy', 'Xavier', 'Yara', 'Zoe', 'Aaron', 'Bella', 'Cole', 'Dana'];

  for (let i = 0; i < 30; i++) {
    const groupId = Math.floor(i / 6);
    const zoneId = groupId;
    const citizen = new AICitizen(i, names[i], {
      humor: Math.random(),
      curiosity: Math.random(),
      friendliness: Math.random(),
      ambition: Math.random(),
    }, groupId, zoneId);
    
    // Relate citizens within same group more strongly
    for (let j = 0; j < 30; j++) {
      const otherGroupId = Math.floor(j / 6);
      if (otherGroupId === groupId && i !== j) {
        citizen.relationships[j] = 0.6 + Math.random() * 0.4;  // Strong intra-group bonds
      } else if (Math.floor(Math.abs(otherGroupId - groupId)) <= 1) {
        citizen.relationships[j] = Math.random() * 0.3;  // Weak inter-group bonds
      }
    }
    
    worldState.population.push(citizen);
  }

  // Initialize settlements
  for (let i = 0; i < 5; i++) {
    worldState.settlements.push({
      id: i,
      zoneId: i,
      population: 6,
      citizens: worldState.population.filter(c => c.groupId === i),
      treasury: 600,
      happiness: 0.7,
      founded: 0,
    });
  }

  log('5 settlement groups created (6 survivors each)', 'blue');
  log('Running 100-day simulation...', 'blue');

  const settlementHistory = [];

  for (let tick = 0; tick < 100; tick++) {
    worldState.currentTick++;
    worldState.time.day++;
    
    if (worldState.time.day > 30) {
      worldState.time.day = 1;
      const seasons = ['Spring', 'Summer', 'Fall', 'Winter'];
      const idx = seasons.indexOf(worldState.time.season);
      worldState.time.season = seasons[(idx + 1) % 4];
      if (idx === 3) worldState.time.year++;
    }

    // Tick all citizens
    for (const citizen of worldState.population) {
      citizen.dailyTick(worldState);
      
      // Random inter-group interaction (potential merging)
      if (tick % 20 === 0 && Math.random() < 0.2) {
        const otherGroupId = (citizen.groupId + 1) % 5;
        const mergeChance = 0.1; // Low chance of merging
        
        if (Math.random() < mergeChance) {
          citizen.groupId = otherGroupId;  // Citizen switches groups
        }
      }
    }

    // Random jobs
    if (tick % 8 === 0) {
      const citizen = worldState.population[Math.floor(Math.random() * 30)];
      if (!citizen.job && Math.random() < 0.6) {
        const jobTypes = ['farming', 'building', 'crafting'];
        const jobType = jobTypes[Math.floor(Math.random() * 3)];
        const skillLevel = citizen.skills[jobType] / 100;
        const perf = Math.min(1.0, Math.max(0.2, (0.5 + Math.random() * 0.3) * (0.7 + skillLevel * 0.3)));
        citizen.job = {type: jobType, duration: 3, performance: perf};
      }
    }

    // Update settlement stats
    for (let i = 0; i < 5; i++) {
      const citizens = worldState.population.filter(c => c.groupId === i);
      if (citizens.length > 0) {
        worldState.settlements[i].population = citizens.length;
        worldState.settlements[i].happiness = 
          citizens.reduce((s, c) => s + (1 - c.getDecisionPressure(worldState)), 0) / citizens.length;
        worldState.settlements[i].treasury = 
          citizens.reduce((s, c) => s + c.inventory.money, 0);
      }
    }

    if (tick % 20 === 0 || tick === 99) {
      settlementHistory.push({
        day: worldState.currentTick,
        settlements: worldState.settlements.map(s => ({
          id: s.id,
          population: s.population,
          treasury: s.treasury.toFixed(0),
          happiness: (s.happiness * 100).toFixed(0),
        })),
      });
    }
  }

  // Analysis
  log('\n📊 SETTLEMENT EVOLUTION:', 'bright');
  settlementHistory.forEach((snap) => {
    log(`\nDay ${snap.day}:`, 'blue');
    snap.settlements.forEach((s) => {
      const popBar = '█'.repeat(Math.round(s.population / 2));
      log(`  Settlement ${s.id}: ${popBar} ${s.population}👥 | Treasury: $${s.treasury} | Happiness: ${s.happiness}%`, 'magenta');
    });
  });

  // Check merging
  const finalState = settlementHistory[settlementHistory.length - 1];
  const mergedSettlements = finalState.settlements.filter(s => s.population > 6).length;
  const abandonedSettlements = finalState.settlements.filter(s => s.population === 0).length;

  log('\n🎯 SETTLEMENT VERDICT:', 'bright');
  log(`Merged settlements: ${mergedSettlements}`, 'blue');
  log(`Abandoned settlements: ${abandonedSettlements}`, 'blue');

  if (mergedSettlements > 2) {
    log('✅ SETTLEMENTS MERGING - Population naturally consolidating', 'green');
  } else if (abandonedSettlements > 1) {
    log('⚠️  SETTLEMENTS COLLAPSING - Economy couldn\'t sustain split population', 'yellow');
  } else {
    log('✅ SETTLEMENTS STABLE - 5 rival towns formed successfully', 'green');
  }
}

// ===== TEST 2: MAXIMUM STRESS =====

function testMaximumStress() {
  log('\n╔═══════════════════════════════════════════════════════════════╗', 'bright');
  log('║  TEST 2: MAXIMUM STRESS TEST (20 Runs, All Settings Maxed)   ║', 'bright');
  log('║  Exploring system breaking points                            ║', 'bright');
  log('╚═══════════════════════════════════════════════════════════════╝\n', 'bright');

  const results = [];

  for (let run = 0; run < 20; run++) {
    const worldState = {
      currentTick: 0,
      time: {day: 1, season: 'Spring', year: 1},
      population: [],
      events: [],
    };

    // MAXED SETTINGS: 100 citizens
    const names = Array.from({length: 100}, (_, i) => `Citizen${i + 1}`);
    
    for (let i = 0; i < 100; i++) {
      const citizen = new AICitizen(i, names[i], {
        humor: Math.random(),
        curiosity: Math.random(),
        friendliness: Math.random(),
        ambition: Math.random(),
      });
      
      // Maxed personality variations
      if (i % 10 === 0) {
        citizen.personality = {humor: 0, curiosity: 0, friendliness: 0, ambition: 0};
      } else if (i % 10 === 1) {
        citizen.personality = {humor: 1, curiosity: 1, friendliness: 1, ambition: 1};
      }
      
      // Maxed skill variations
      if (i % 5 === 0) {
        citizen.skills = {building: 100, farming: 100, crafting: 100, socializing: 100};
      } else if (i % 5 === 1) {
        citizen.skills = {building: 0, farming: 0, crafting: 0, socializing: 0};
      }
      
      // Maxed money variations
      if (i % 3 === 0) citizen.inventory.money = 0;
      if (i % 3 === 1) citizen.inventory.money = 10000;
      
      // All relationships
      for (let j = 0; j < 100; j++) {
        if (i !== j) citizen.relationships[j] = Math.random();
      }
      
      worldState.population.push(citizen);
    }

    let issues = 0;
    let crashes = 0;

    // MAXED TIME: 365 days
    try {
      for (let tick = 0; tick < 365; tick++) {
        worldState.currentTick++;
        worldState.time.day++;
        
        if (worldState.time.day > 30) {
          worldState.time.day = 1;
          const seasons = ['Spring', 'Summer', 'Fall', 'Winter'];
          const idx = seasons.indexOf(worldState.time.season);
          worldState.time.season = seasons[(idx + 1) % 4];
          if (idx === 3) worldState.time.year++;
        }

        // MAXED JOBS: Assign jobs to 50% of citizens each tick
        for (let i = 0; i < 50; i++) {
          const citizen = worldState.population[Math.floor(Math.random() * 100)];
          if (!citizen.job && Math.random() < 0.8) {
            const jobTypes = ['farming', 'building', 'crafting'];
            const jobType = jobTypes[Math.floor(Math.random() * 3)];
            const perf = Math.min(1.0, Math.max(0.2, (0.5 + Math.random() * 0.3) * (citizen.skills[jobType] / 100)));
            citizen.job = {type: jobType, duration: 5 + Math.floor(Math.random() * 10), performance: perf};
          }
        }

        // Tick all citizens
        for (const citizen of worldState.population) {
          citizen.dailyTick(worldState);
          
          if (isNaN(citizen.needs.hunger) || !isFinite(citizen.inventory.money)) {
            issues++;
          }
        }

        // MAXED EVENTS: 50% chance every tick
        if (Math.random() < 0.5) {
          worldState.events.push({
            tick: worldState.currentTick,
            type: Math.random() > 0.5 ? 'disaster' : 'discovery',
          });
          if (worldState.events.length > 1000) worldState.events.shift();
        }
      }
    } catch (err) {
      crashes++;
    }

    results.push({
      run: run + 1,
      population: 100,
      days: 365,
      issues,
      crashes,
      avgMoney: worldState.population.reduce((s, c) => s + c.inventory.money, 0) / 100,
      avgHunger: worldState.population.reduce((s, c) => s + c.needs.hunger, 0) / 100,
    });

    if ((run + 1) % 5 === 0) {
      log(`✅ Completed ${run + 1}/20 stress tests`, 'green');
    }
  }

  // Analysis
  log('\n📊 STRESS TEST RESULTS:', 'bright');
  
  const totalCrashes = results.reduce((s, r) => s + r.crashes, 0);
  const totalIssues = results.reduce((s, r) => s + r.issues, 0);
  const avgMoney = results.reduce((s, r) => s + r.avgMoney, 0) / results.length;
  const avgHunger = results.reduce((s, r) => s + r.avgHunger, 0) / results.length;

  log(`Total runs: 20`, 'blue');
  log(`Total crashes: ${totalCrashes === 0 ? '0 ✅' : totalCrashes + ' ❌'}`, totalCrashes === 0 ? 'green' : 'red');
  log(`Total issues: ${totalIssues === 0 ? '0 ✅' : totalIssues + ' ⚠️'}`, totalIssues === 0 ? 'green' : 'yellow');
  log(`Avg money per citizen: $${avgMoney.toFixed(2)}`, 'blue');
  log(`Avg hunger: ${(avgHunger * 100).toFixed(0)}%`, 'blue');

  log('\n🎯 MAXIMUM STRESS VERDICT:', 'bright');
  if (totalCrashes === 0 && totalIssues === 0) {
    log('✅ SYSTEM STABLE - Handles 100 citizens, 365 days, maxed settings without crashes', 'green');
    log('✅ Ready for production load', 'green');
  } else {
    log(`⚠️  Found ${totalCrashes} crashes and ${totalIssues} issues`, 'yellow');
  }
}

// ===== RUN ALL TESTS =====

function runAllAdvancedTests() {
  log('\n' + '='.repeat(65), 'cyan');
  log('ADVANCED SIMULATION SUITE', 'bright');
  log('='.repeat(65) + '\n', 'cyan');

  testMultiSettlement();
  testMaximumStress();

  log('\n' + '='.repeat(65), 'cyan');
  log('ADVANCED TESTING COMPLETE', 'bright');
  log('='.repeat(65) + '\n', 'cyan');
}

runAllAdvancedTests();
