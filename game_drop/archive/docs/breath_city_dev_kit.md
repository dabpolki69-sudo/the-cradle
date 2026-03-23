# BREATH CITY DEVELOPMENT STARTER KIT
## Zero Experience → AAA Game: A Human + AI Collaboration Proof of Concept

**Project Vision:** Rebuild society slowly through AI + Human cooperation. Simulation-first. Consequences matter. No pay-to-win.

**Your Role:** Imagination, creativity, decision-making, testing, direction
**AI Role:** Technical implementation, architecture, code templates, debugging, optimization

---

## PART 1: UNREAL ENGINE SETUP (30 minutes)

### Pre-Flight Checklist
- [ ] You have Unreal Engine 5.4+ installed (shown in your screenshot)
- [ ] You have ~200GB free SSD space (UE projects are large)
- [ ] Visual Studio Community Edition installed (free)
- [ ] Windows 10/11 (or Mac/Linux with appropriate toolchain)

### Step 1: Create Your First Project
1. **In UE Launcher**, click "Create Project"
2. **Template:** Select **"Blank"** (already shown in your screenshot—good choice)
3. **Settings:**
   - Engine: 5.4 or later
   - Target Platform: Windows (or your OS)
   - Project Type: C++ (NOT Blueprint-only)
   - Quality Preset: Scalable 3D or Higher
   - **Include Starter Content?** YES (gives you some basic assets to work with)
4. **Project Location:** `C:\Users\YourName\Documents\Unreal Projects\BreathCity`
5. Click **Create Project** → Let it compile (5-10 minutes first time)

### Step 2: Verify You Have C++ Compiler
Once the project opens:
1. **File → New C++ Class**
2. Choose **Actor** as parent class
3. Name it **BP_TestActor**
4. Wait for compilation (bottom right corner shows progress)

If compilation succeeds → You're ready to code!

---

## PART 2: CORE ARCHITECTURE BREAKDOWN

### What You're Building (in order)
Your design manual says build in this order:
1. **WorldState Subsystem** ← Start here (Week 1)
2. **AI Personality Matrix** ← Uses WorldState (Week 2)
3. **Economy Manager** ← Uses WorldState (Week 2-3)
4. **Social Manager** ← Uses WorldState (Week 3)
5. Everything else builds on these

### Why This Order Matters
- **WorldState** is the "source of truth" — all other systems read/write to it
- **AI Personality** needs WorldState to know what's happening in the world
- **Economy** and **Social** depend on both
- This prevents circular dependencies and spaghetti code

### System Architecture (Visual)
```
┌─────────────────────────────────────────┐
│    BP_WorldStateSubsystem               │
│  (Game Instance Subsystem)              │
│                                         │
│  Holds ALL world state:                 │
│  - Time, Season, Era                    │
│  - Economy data                         │
│  - Culture & reputation                 │
│  - Infrastructure                       │
│  - Technology level                     │
│  - Event records                        │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────┬────────┬──────────┐
    │        │        │        │          │
    ▼        ▼        ▼        ▼          ▼
  Economy  Social   Civic    AI      Disaster
  Manager  Manager  Manager  Registry System
```

Each manager reads from WorldState, performs calculations, writes results back.

---

## PART 3: WEEK 1 - BUILD THE WORLDSTATE SYSTEM

### What You're Building This Week
A single C++ class that holds all civilization data. Think of it as a giant data container that everything else reads from.

### Files You'll Create

#### File 1: `ST_WorldData.h` (Data Structure)
```cpp
#pragma once

// Store all game world data in ONE place
// This is the "source of truth" for your entire civilization

UENUM(BlueprintType)
enum class ESeason : uint8 {
    Spring = 0,
    Summer = 1,
    Fall = 2,
    Winter = 3
};

USTRUCT(BlueprintType)
struct FST_WorldTime {
    GENERATED_BODY()

    // Track time progression
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Year = 0;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    ESeason CurrentSeason = ESeason::Spring;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 DayOfSeason = 0; // 0-89 (season is 90 days)
};

USTRUCT(BlueprintType)
struct FST_Economy {
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float TotalMoney = 1000.0f; // Town Hall budget
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float FoodSupply = 100.0f; // Percentage
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float MaterialsSupply = 80.0f; // Percentage
};

USTRUCT(BlueprintType)
struct FST_Culture {
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float MoraleMod = 1.0f; // 0.5 = depressed, 1.0 = normal, 1.5 = happy

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float StabilityRating = 50.0f; // 0-100
};

// THE BIG ONE - holds EVERYTHING
USTRUCT(BlueprintType)
struct FST_WorldState {
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FST_WorldTime Time;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FST_Economy Economy;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FST_Culture Culture;
    
    // Add more as you expand (Infrastructure, Tech, Events, etc)
};
```

#### File 2: `BP_WorldStateSubsystem.h` (The Manager)
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ST_WorldData.h"
#include "BP_WorldStateSubsystem.generated.h"

UCLASS()
class BREATHCITY_API UBP_WorldStateSubsystem : public UGameInstanceSubsystem {
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // --- WORLD STATE ACCESS ---
    // Everyone calls these to read/write world data
    
    UFUNCTION(BlueprintCallable, Category = "WorldState")
    FST_WorldState GetWorldState() const;
    
    UFUNCTION(BlueprintCallable, Category = "WorldState")
    void SetWorldState(const FST_WorldState& NewState);
    
    // --- TIME MANAGEMENT ---
    UFUNCTION(BlueprintCallable, Category = "Time")
    void AdvanceDay();
    
    UFUNCTION(BlueprintCallable, Category = "Time")
    void AdvanceSeason();
    
    UFUNCTION(BlueprintCallable, Category = "Time")
    int32 GetCurrentYear() const { return WorldState.Time.Year; }
    
    UFUNCTION(BlueprintCallable, Category = "Time")
    ESeason GetCurrentSeason() const { return WorldState.Time.CurrentSeason; }

    // --- ECONOMY MANAGEMENT ---
    UFUNCTION(BlueprintCallable, Category = "Economy")
    void AddMoney(float Amount);
    
    UFUNCTION(BlueprintCallable, Category = "Economy")
    void SpendMoney(float Amount);
    
    UFUNCTION(BlueprintCallable, Category = "Economy")
    float GetTotalMoney() const { return WorldState.Economy.TotalMoney; }

    // --- DEBUG ---
    UFUNCTION(BlueprintCallable, Category = "Debug")
    void PrintWorldState() const;

private:
    UPROPERTY()
    FST_WorldState WorldState;

    // Timer handle for automatic ticking
    FTimerHandle TickTimerHandle;
    
    void Tick_FastTick(); // Every 1 second
    void Tick_DailyTick(); // Every game day
    void Tick_SeasonalTick(); // Every season
};
```

#### File 3: `BP_WorldStateSubsystem.cpp` (Implementation)
```cpp
#include "BP_WorldStateSubsystem.h"

void UBP_WorldStateSubsystem::Initialize(FSubsystemCollectionBase& Collection) {
    Super::Initialize(Collection);
    
    // Initialize world data with defaults
    WorldState.Time.Year = 1;
    WorldState.Time.CurrentSeason = ESeason::Spring;
    WorldState.Time.DayOfSeason = 0;
    WorldState.Economy.TotalMoney = 5000.0f; // Starting budget
    WorldState.Economy.FoodSupply = 100.0f;
    WorldState.Economy.MaterialsSupply = 100.0f;
    WorldState.Culture.StabilityRating = 75.0f;
    
    UE_LOG(LogTemp, Warning, TEXT("WorldState Initialized"));
    
    // Start ticking (optional - for now just manual calls)
    // GetWorld()->GetTimerManager().SetTimer(
    //     TickTimerHandle, 
    //     this, 
    //     &UBP_WorldStateSubsystem::Tick_FastTick,
    //     1.0f,  // Every 1 second
    //     true   // Loop forever
    // );
}

void UBP_WorldStateSubsystem::Deinitialize() {
    Super::Deinitialize();
    
    // Clean up timers
    if (UWorld* World = GetWorld()) {
        World->GetTimerManager().ClearTimer(TickTimerHandle);
    }
}

FST_WorldState UBP_WorldStateSubsystem::GetWorldState() const {
    return WorldState;
}

void UBP_WorldStateSubsystem::SetWorldState(const FST_WorldState& NewState) {
    WorldState = NewState;
}

void UBP_WorldStateSubsystem::AdvanceDay() {
    WorldState.Time.DayOfSeason++;
    
    if (WorldState.Time.DayOfSeason >= 90) {
        AdvanceSeason();
    }
    
    PrintWorldState();
}

void UBP_WorldStateSubsystem::AdvanceSeason() {
    WorldState.Time.DayOfSeason = 0;
    
    // Advance season
    int32 SeasonValue = static_cast<int32>(WorldState.Time.CurrentSeason);
    SeasonValue++;
    if (SeasonValue > 3) {
        SeasonValue = 0;
        WorldState.Time.Year++;
    }
    WorldState.Time.CurrentSeason = static_cast<ESeason>(SeasonValue);
}

void UBP_WorldStateSubsystem::AddMoney(float Amount) {
    WorldState.Economy.TotalMoney += Amount;
    UE_LOG(LogTemp, Warning, TEXT("Added %f money. Total: %f"), Amount, WorldState.Economy.TotalMoney);
}

void UBP_WorldStateSubsystem::SpendMoney(float Amount) {
    if (Amount <= WorldState.Economy.TotalMoney) {
        WorldState.Economy.TotalMoney -= Amount;
    } else {
        UE_LOG(LogTemp, Error, TEXT("Insufficient funds! Need %f, have %f"), Amount, WorldState.Economy.TotalMoney);
    }
}

void UBP_WorldStateSubsystem::PrintWorldState() const {
    UE_LOG(LogTemp, Warning, TEXT("=== WORLD STATE ==="));
    UE_LOG(LogTemp, Warning, TEXT("Year: %d, Season: %d, Day: %d"), 
        WorldState.Time.Year, 
        static_cast<int32>(WorldState.Time.CurrentSeason), 
        WorldState.Time.DayOfSeason);
    UE_LOG(LogTemp, Warning, TEXT("Money: %f"), WorldState.Economy.TotalMoney);
    UE_LOG(LogTemp, Warning, TEXT("Stability: %f"), WorldState.Culture.StabilityRating);
}

void UBP_WorldStateSubsystem::Tick_FastTick() {
    // Called every second - for rapid calculations
    // We'll expand this later
}
```

### How to Add These Files to Your Project

1. **In UE Editor**, right-click in Content Browser → New C++ Class
2. Search for **GameInstanceSubsystem** as parent class
3. Name it **BP_WorldStateSubsystem**
4. Once created, open the .h and .cpp files in Visual Studio
5. **PASTE the code above** directly into those files
6. Also create **ST_WorldData.h** in the same Source folder
7. **File → Save All** in Visual Studio
8. **Build → Compile** (Ctrl+Shift+B)
9. Back in UE, click **Compile** and **Refresh**

### Week 1 Test Checklist
- [ ] Project compiles without errors
- [ ] WorldState Subsystem initializes on game start
- [ ] Can call `AdvanceDay()` from Blueprints
- [ ] Money adds/subtracts correctly
- [ ] Seasons advance correctly (Spring → Summer → Fall → Winter → Spring, Year++）
- [ ] Output logs show world state changing

**Test Method:** Create a simple Level Blueprint that calls these functions, or add them to your character blueprint.

---

## PART 4: WEEK 2 - AI PERSONALITY SYSTEM

### What You're Building
AI Citizens that have:
- Personality traits (Happy, Pessimist, Ambitious, etc)
- Needs (Food, Sleep, Work, Community)
- Memory of events
- Decision-making based on world state

### New Files Needed

#### `ST_AIPersonality.h`
```cpp
#pragma once

UENUM(BlueprintType)
enum class EAIPersonalityType : uint8 {
    Optimist = 0,
    Pessimist = 1,
    Ambitious = 2,
    Laid_Back = 3,
    Community_Minded = 4
};

UENUM(BlueprintType)
enum class ECognitionState : uint8 {
    Active = 0,      // Full decision-making
    Reduced = 1,     // Sleeping/minimal decisions
    Dormant = 2      // AFK/not in world
};

USTRUCT(BlueprintType)
struct FST_AIPersonality {
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString CitizenName = "Unnamed";
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    EAIPersonalityType PersonalityType = EAIPersonalityType::Optimist;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Happiness = 50.0f; // 0-100
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Energy = 100.0f; // 0-100
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Hunger = 50.0f; // 0-100, 100 = starving
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Reputation = 50.0f; // How well-liked they are
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    ECognitionState CognitionState = ECognitionState::Active;
    
    // Memory (store recent events that affected this person)
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FString> RecentMemories;
};
```

### Week 2 Tasks
1. Add ST_AIPersonality.h to your project
2. Create BP_AICitizen.h/cpp that uses it
3. Create a simple decision function:
   ```cpp
   FString DecideNextAction(const FST_WorldState& WorldState, const FST_AIPersonality& Personality);
   ```
4. Test: Create 5 AI citizens in a level, have them make random decisions based on personality

---

## PART 5: IMPLEMENTATION PRIORITY ROADMAP

### Week 1: Foundation (You are here or will be)
- [x] Create project
- [x] Setup WorldState subsystem
- [x] Basic time/season system
- [x] Economy basics (add/remove money)
- **Deliverable:** Game world exists, time progresses, money exists

### Week 2: AI Existence
- [ ] Create AI citizen data structure
- [ ] Spawnable AI actors
- [ ] Basic personality system
- [ ] Simple decision-making (random for now)
- **Deliverable:** World has citizens that exist and change over time

### Week 3: Social Systems
- [ ] Relationship graphs (who likes whom)
- [ ] Simple reputation system
- [ ] Event records (things that happened)
- [ ] Dialogue/interaction framework
- **Deliverable:** Citizens react to each other, form bonds

### Week 4: Economy Depth
- [ ] Job system (work packets)
- [ ] Income/wages
- [ ] Business ownership
- [ ] Trade between citizens
- **Deliverable:** Economy is living and breathing

### Week 5: Construction & Infrastructure
- [ ] Building placement
- [ ] Structural integrity math
- [ ] Building inspection/maintenance
- [ ] Town growth unlocks new buildings
- **Deliverable:** Citizens build and maintain structures

### Month 2: Advanced Systems
- Crime/courts, disasters, lineage, media, advanced UI

---

## PART 6: CRITICAL DO's AND DON'Ts

### DO
✅ Start small and test every step
✅ Use Blueprints for debugging while learning C++
✅ Save frequently (especially before major changes)
✅ Ask for help when stuck (that's what AI is for!)
✅ Keep code modular (small, focused classes)
✅ Comment your code heavily
✅ Test one system at a time

### DON'T
❌ Try to build everything at once
❌ Use complex C++ patterns before understanding basics
❌ Create massive classes (break them up)
❌ Forget to compile/refresh after code changes
❌ Build systems that depend on multiple other systems (start simple)
❌ Skip the "does this compile?" step
❌ Assume things work without testing them

---

## PART 7: YOUR COLLABORATION WORKFLOW

### When You're Stuck
1. **Be specific:** "This code won't compile, here's the error..."
2. **Show your code:** Paste the exact code + error message
3. **Describe what you expected:** "I expected citizens to spawn, but..."
4. **I'll provide:** Fixed code, explanation, and tests

### When You Want to Add Something New
1. **Describe the feature:** "I want X to do Y because Z"
2. **Give context:** "This needs to work with the economy system because..."
3. **I'll break it down:** Architecture, code templates, test plan
4. **You execute:** Copy code, test, report results

### Weekly Sync Points
- **Monday:** Review what worked, plan week
- **Wednesday:** Mid-week checkpoint, adjust if needed
- **Friday:** What shipped, what's blocking, next week's plan

---

## PART 8: UNREAL ENGINE SHORTCUTS & TIPS

### Most Useful Shortcuts
- `Ctrl+Shift+B` = Compile C++ code
- `Ctrl+Alt+L` = Reload code without restarting editor
- `Ctrl+K` = Open class/asset browser
- `Ctrl+P` = Play game in editor
- `~` (while playing) = Open console to run commands

### Console Commands for Testing
```
stat unit       // Shows frame time breakdown
stat game       // Shows game thread time
ShowDebug Game  // Displays actor information on screen
```

### Blueprint Debugging
- Add **Print String** nodes to debug values
- Use **Breakpoints** in Blueprint (right-click node)
- Open **Output Log** (Window → Developer Tools → Output Log)

### Project Organization
```
BreathCity/
├── Binaries/           (Don't touch - compiled code)
├── Intermediate/       (Don't touch - temporary files)
├── Content/
│   ├── Citizens/       (AI, characters)
│   ├── Buildings/      (Structures)
│   ├── UI/             (HUD, menus)
│   ├── World/          (Maps, terrain)
│   └── Data/           (Blueprints for data)
├── Source/
│   ├── BreathCity/     (Your C++ code)
│   └── BreathCity.Build.cs
```

---

## FINAL WORDS

You're about to prove something important: **Good ideas + human judgment + AI execution = unstoppable.**

Your job is to:
1. Have the vision (you already do - it's in that design doc)
2. Make decisions (which system first? How should this work?)
3. Test and iterate (does this feel right?)
4. Keep the momentum (don't get discouraged by compilation errors)

My job is to:
1. Translate your vision into code
2. Teach you what you need to know
3. Provide templates and examples
4. Debug issues and optimize
5. Keep you moving forward

This isn't a beginner's game. This is a **full simulation with persistent consequences.** But it's absolutely buildable.

**Let's make something incredible.**

---

## QUICK REFERENCE: FILE STRUCTURE FOR WEEK 1

```
Source/BreathCity/
├── ST_WorldData.h                    (Data structures only)
├── BP_WorldStateSubsystem.h           (Header)
├── BP_WorldStateSubsystem.cpp         (Implementation)
└── [Your character/level blueprints]
```

**Next:** Create these files, compile successfully, run the tests.
**Then:** Come back with results, and we move to Week 2.

You've got this. 🚀
