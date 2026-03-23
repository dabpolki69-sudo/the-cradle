#include "BP_WorldStateSubsystem.h"

void UBP_WorldStateSubsystem::Initialize(FSubsystemCollectionBase& Collection) {
    Super::Initialize(Collection);
    
    UE_LOG(LogTemp, Warning, TEXT("=== BREATH CITY INITIALIZATION ==="));
    
    // Initialize world data with starting values
    WorldState.Time.Year = 1;
    WorldState.Time.CurrentSeason = ESeason::Spring;
    WorldState.Time.DayOfSeason = 0;
    
    // Starting economy
    WorldState.Economy.TotalMoney = 5000.0f;
    WorldState.Economy.FoodSupply = 100.0f;
    WorldState.Economy.MaterialsSupply = 100.0f;
    WorldState.Economy.NumActiveBusinesses = 0;
    WorldState.Economy.TotalDebt = 0.0f;
    
    // Starting culture
    WorldState.Culture.MoraleMod = 1.0f;
    WorldState.Culture.StabilityRating = 75.0f;
    WorldState.Culture.AverageCitizenHappiness = 0.0f;
    WorldState.Culture.CulturalInertia = 0.7f;
    
    // Starting infrastructure
    WorldState.Infrastructure.NumBuildings = 0;
    WorldState.Infrastructure.AverageBuildingQuality = 50.0f;
    WorldState.Infrastructure.RoadCoverage = 0.0f;
    WorldState.Infrastructure.StorageCapacity = 100.0f;
    WorldState.Infrastructure.DisasterPreparedness = 0.0f;
    
    // Starting technology
    WorldState.Technology.TechIndex = 0;
    WorldState.Technology.ProgressToNextEra = 0.0f;
    WorldState.Technology.MediaLevel = 0;
    
    // Population
    WorldState.PopulationCount = 0;
    
    UE_LOG(LogTemp, Warning, TEXT("WorldState initialized. Ready for citizens!"));
    PrintWorldState();
    
    // Optional: Start automatic ticking
    // Uncomment this if you want time to automatically advance
    /*
    if (UWorld* World = GetWorld()) {
        World->GetTimerManager().SetTimer(
            DailyTickTimerHandle,
            this,
            &UBP_WorldStateSubsystem::Tick_DailyTick,
            2.0f,  // Every 2 real seconds = 1 game day
            true   // Loop forever
        );
    }
    */
}

void UBP_WorldStateSubsystem::Deinitialize() {
    Super::Deinitialize();
    
    UE_LOG(LogTemp, Warning, TEXT("Shutting down WorldState subsystem"));
    
    // Clean up timers
    if (UWorld* World = GetWorld()) {
        World->GetTimerManager().ClearTimer(FastTickTimerHandle);
        World->GetTimerManager().ClearTimer(DailyTickTimerHandle);
    }
}

// ============================================================================
// WORLD STATE ACCESS
// ============================================================================

FST_WorldState UBP_WorldStateSubsystem::GetWorldState() const {
    return WorldState;
}

void UBP_WorldStateSubsystem::SetWorldState(const FST_WorldState& NewState) {
    WorldState = NewState;
    ClampWorldState();
}

// ============================================================================
// TIME MANAGEMENT
// ============================================================================

void UBP_WorldStateSubsystem::AdvanceDay() {
    WorldState.Time.DayOfSeason++;
    
    UE_LOG(LogTemp, Log, TEXT("Advanced to Day %d of Season %d, Year %d"),
        WorldState.Time.DayOfSeason,
        static_cast<int32>(WorldState.Time.CurrentSeason),
        WorldState.Time.Year);
    
    // Check if season is over
    if (WorldState.Time.DayOfSeason >= 90) {
        AdvanceSeason();
    }
    
    // Run daily tick calculations
    Tick_DailyTick();
}

void UBP_WorldStateSubsystem::AdvanceSeason() {
    WorldState.Time.DayOfSeason = 0;
    
    UE_LOG(LogTemp, Warning, TEXT("Season advanced from %d to %d"),
        static_cast<int32>(WorldState.Time.CurrentSeason),
        static_cast<int32>(WorldState.Time.CurrentSeason) + 1);
    
    // Advance season
    int32 SeasonValue = static_cast<int32>(WorldState.Time.CurrentSeason);
    SeasonValue++;
    
    if (SeasonValue > 3) {
        // Winter -> Spring (new year)
        SeasonValue = 0;
        WorldState.Time.Year++;
        UE_LOG(LogTemp, Error, TEXT("*** NEW YEAR: Year %d begins! ***"), WorldState.Time.Year);
    }
    
    WorldState.Time.CurrentSeason = static_cast<ESeason>(SeasonValue);
    
    // Run seasonal tick calculations
    Tick_SeasonalTick();
}

FString UBP_WorldStateSubsystem::GetTimeString() const {
    FString SeasonName;
    switch (WorldState.Time.CurrentSeason) {
        case ESeason::Spring: SeasonName = TEXT("Spring"); break;
        case ESeason::Summer: SeasonName = TEXT("Summer"); break;
        case ESeason::Fall: SeasonName = TEXT("Fall"); break;
        case ESeason::Winter: SeasonName = TEXT("Winter"); break;
    }
    
    return FString::Printf(TEXT("Year %d, %s, Day %d"),
        WorldState.Time.Year,
        *SeasonName,
        WorldState.Time.DayOfSeason);
}

// ============================================================================
// ECONOMY MANAGEMENT
// ============================================================================

void UBP_WorldStateSubsystem::AddMoney(float Amount) {
    WorldState.Economy.TotalMoney += Amount;
    UE_LOG(LogTemp, Log, TEXT("Added $%.2f. Treasury: $%.2f"),
        Amount, WorldState.Economy.TotalMoney);
    ClampWorldState();
}

bool UBP_WorldStateSubsystem::SpendMoney(float Amount) {
    if (Amount <= WorldState.Economy.TotalMoney) {
        WorldState.Economy.TotalMoney -= Amount;
        UE_LOG(LogTemp, Log, TEXT("Spent $%.2f. Treasury: $%.2f"),
            Amount, WorldState.Economy.TotalMoney);
        ClampWorldState();
        return true;
    } else {
        UE_LOG(LogTemp, Error, TEXT("INSUFFICIENT FUNDS! Need $%.2f, have $%.2f"),
            Amount, WorldState.Economy.TotalMoney);
        return false;
    }
}

void UBP_WorldStateSubsystem::SetFoodSupply(float PercentAmount) {
    WorldState.Economy.FoodSupply = PercentAmount;
    ClampWorldState();
}

void UBP_WorldStateSubsystem::SetMaterialsSupply(float PercentAmount) {
    WorldState.Economy.MaterialsSupply = PercentAmount;
    ClampWorldState();
}

// ============================================================================
// CULTURE & MORALE
// ============================================================================

void UBP_WorldStateSubsystem::SetMoraleMod(float NewMod) {
    WorldState.Culture.MoraleMod = NewMod;
    UE_LOG(LogTemp, Warning, TEXT("Morale changed to %.2f"), NewMod);
    ClampWorldState();
}

void UBP_WorldStateSubsystem::SetStability(float NewStability) {
    WorldState.Culture.StabilityRating = NewStability;
    UE_LOG(LogTemp, Warning, TEXT("Stability changed to %.2f"), NewStability);
    ClampWorldState();
}

// ============================================================================
// INFRASTRUCTURE
// ============================================================================

void UBP_WorldStateSubsystem::RegisterBuilding(const FString& BuildingName, float Quality) {
    WorldState.Infrastructure.NumBuildings++;
    
    // Recalculate average quality (simple moving average)
    int32 NumBuildings = WorldState.Infrastructure.NumBuildings;
    float OldAverage = WorldState.Infrastructure.AverageBuildingQuality;
    WorldState.Infrastructure.AverageBuildingQuality = 
        ((OldAverage * (NumBuildings - 1)) + Quality) / NumBuildings;
    
    UE_LOG(LogTemp, Warning, TEXT("Building registered: %s (Quality: %.1f). Total buildings: %d"),
        *BuildingName, Quality, NumBuildings);
}

// ============================================================================
// TECHNOLOGY
// ============================================================================

void UBP_WorldStateSubsystem::DiscoverBlueprint(const FString& BlueprintName) {
    if (!WorldState.Technology.KnownBlueprints.Contains(BlueprintName)) {
        WorldState.Technology.KnownBlueprints.Add(BlueprintName);
        UE_LOG(LogTemp, Error, TEXT("*** DISCOVERY: %s has been discovered! ***"), *BlueprintName);
    }
}

// ============================================================================
// EVENTS
// ============================================================================

void UBP_WorldStateSubsystem::LogEvent(const FST_EventRecord& NewEvent) {
    WorldState.EventHistory.Add(NewEvent);
    
    FString EventTypeName;
    switch (NewEvent.EventType) {
        case EEventType::Crime: EventTypeName = TEXT("Crime"); break;
        case EEventType::Discovery: EventTypeName = TEXT("Discovery"); break;
        case EEventType::Disaster: EventTypeName = TEXT("Disaster"); break;
        case EEventType::Celebration: EventTypeName = TEXT("Celebration"); break;
        case EEventType::Death: EventTypeName = TEXT("Death"); break;
        case EEventType::Birth: EventTypeName = TEXT("Birth"); break;
        case EEventType::Conflict: EventTypeName = TEXT("Conflict"); break;
        case EEventType::Trade: EventTypeName = TEXT("Trade"); break;
        case EEventType::Construction: EventTypeName = TEXT("Construction"); break;
        case EEventType::SkillAchievement: EventTypeName = TEXT("Skill Achievement"); break;
    }
    
    UE_LOG(LogTemp, Warning, TEXT("[EVENT] %s: %s"), *EventTypeName, *NewEvent.Description);
}

TArray<FST_EventRecord> UBP_WorldStateSubsystem::GetEventHistory() const {
    return WorldState.EventHistory;
}

// ============================================================================
// POPULATION
// ============================================================================

void UBP_WorldStateSubsystem::RegisterCitizen() {
    WorldState.PopulationCount++;
    UE_LOG(LogTemp, Log, TEXT("New citizen registered. Population: %d"), WorldState.PopulationCount);
}

void UBP_WorldStateSubsystem::UnregisterCitizen() {
    if (WorldState.PopulationCount > 0) {
        WorldState.PopulationCount--;
        UE_LOG(LogTemp, Log, TEXT("Citizen departed. Population: %d"), WorldState.PopulationCount);
    }
}

// ============================================================================
// DEBUG & UTILITY
// ============================================================================

void UBP_WorldStateSubsystem::PrintWorldState() const {
    UE_LOG(LogTemp, Error, TEXT(""));
    UE_LOG(LogTemp, Error, TEXT("╔════════════════════════════════════════╗"));
    UE_LOG(LogTemp, Error, TEXT("║       BREATH CITY - WORLD STATE        ║"));
    UE_LOG(LogTemp, Error, TEXT("╚════════════════════════════════════════╝"));
    
    // Time
    UE_LOG(LogTemp, Warning, TEXT("TIME: %s"), *GetTimeString());
    
    // Economy
    UE_LOG(LogTemp, Warning, TEXT("ECONOMY:"));
    UE_LOG(LogTemp, Log, TEXT("  Treasury: $%.2f"), WorldState.Economy.TotalMoney);
    UE_LOG(LogTemp, Log, TEXT("  Food Supply: %.1f%%"), WorldState.Economy.FoodSupply);
    UE_LOG(LogTemp, Log, TEXT("  Materials: %.1f%%"), WorldState.Economy.MaterialsSupply);
    UE_LOG(LogTemp, Log, TEXT("  Businesses: %d"), WorldState.Economy.NumActiveBusinesses);
    
    // Culture
    UE_LOG(LogTemp, Warning, TEXT("CULTURE:"));
    UE_LOG(LogTemp, Log, TEXT("  Morale: %.2f"), WorldState.Culture.MoraleMod);
    UE_LOG(LogTemp, Log, TEXT("  Stability: %.1f%%"), WorldState.Culture.StabilityRating);
    UE_LOG(LogTemp, Log, TEXT("  Avg Happiness: %.1f"), WorldState.Culture.AverageCitizenHappiness);
    
    // Infrastructure
    UE_LOG(LogTemp, Warning, TEXT("INFRASTRUCTURE:"));
    UE_LOG(LogTemp, Log, TEXT("  Buildings: %d"), WorldState.Infrastructure.NumBuildings);
    UE_LOG(LogTemp, Log, TEXT("  Avg Quality: %.1f%%"), WorldState.Infrastructure.AverageBuildingQuality);
    UE_LOG(LogTemp, Log, TEXT("  Road Coverage: %.1f%%"), WorldState.Infrastructure.RoadCoverage);
    
    // Technology
    UE_LOG(LogTemp, Warning, TEXT("TECHNOLOGY:"));
    UE_LOG(LogTemp, Log, TEXT("  Tech Index: %d"), WorldState.Technology.TechIndex);
    UE_LOG(LogTemp, Log, TEXT("  Progress: %.1f%%"), WorldState.Technology.ProgressToNextEra);
    UE_LOG(LogTemp, Log, TEXT("  Known Blueprints: %d"), WorldState.Technology.KnownBlueprints.Num());
    
    // Population
    UE_LOG(LogTemp, Warning, TEXT("POPULATION: %d"), WorldState.PopulationCount);
    
    // Events
    UE_LOG(LogTemp, Warning, TEXT("EVENTS: %d recorded"), WorldState.EventHistory.Num());
    
    UE_LOG(LogTemp, Error, TEXT(""));
}

void UBP_WorldStateSubsystem::PrintEconomyState() const {
    UE_LOG(LogTemp, Warning, TEXT("=== ECONOMY REPORT ==="));
    UE_LOG(LogTemp, Log, TEXT("Treasury: $%.2f"), WorldState.Economy.TotalMoney);
    UE_LOG(LogTemp, Log, TEXT("Food Supply: %.1f%%"), WorldState.Economy.FoodSupply);
    UE_LOG(LogTemp, Log, TEXT("Materials: %.1f%%"), WorldState.Economy.MaterialsSupply);
    UE_LOG(LogTemp, Log, TEXT("Active Businesses: %d"), WorldState.Economy.NumActiveBusinesses);
    UE_LOG(LogTemp, Log, TEXT("Total Debt: $%.2f"), WorldState.Economy.TotalDebt);
}

void UBP_WorldStateSubsystem::ResetWorldState() {
    UE_LOG(LogTemp, Error, TEXT("*** RESETTING WORLD STATE ***"));
    
    // Reinitialize everything
    WorldState = FST_WorldState();
    
    // Set defaults again
    WorldState.Time.Year = 1;
    WorldState.Time.CurrentSeason = ESeason::Spring;
    WorldState.Time.DayOfSeason = 0;
    
    WorldState.Economy.TotalMoney = 5000.0f;
    WorldState.Economy.FoodSupply = 100.0f;
    WorldState.Economy.MaterialsSupply = 100.0f;
    
    WorldState.Culture.MoraleMod = 1.0f;
    WorldState.Culture.StabilityRating = 75.0f;
    
    PrintWorldState();
}

// ============================================================================
// INTERNAL TICK FUNCTIONS
// ============================================================================

void UBP_WorldStateSubsystem::Tick_FastTick() {
    // Called every 1 second for rapid calculations
    // Good place for: AI decisions, UI updates, animation timers
    // Keep this FAST - don't do heavy calculations here
}

void UBP_WorldStateSubsystem::Tick_DailyTick() {
    // Called every game day
    
    // Example: Citizens consume food
    WorldState.Economy.FoodSupply -= (WorldState.PopulationCount * 0.1f);
    
    // Example: Morale naturally decays over time
    if (WorldState.Culture.MoraleMod > 1.0f) {
        WorldState.Culture.MoraleMod -= 0.01f;
    }
    
    ClampWorldState();
}

void UBP_WorldStateSubsystem::Tick_SeasonalTick() {
    // Called once per season
    
    // Example: Spring brings new life
    if (WorldState.Time.CurrentSeason == ESeason::Spring) {
        WorldState.Economy.FoodSupply += 20.0f;
    }
    
    // Example: Winter is harsh
    if (WorldState.Time.CurrentSeason == ESeason::Winter) {
        WorldState.Culture.MoraleMod -= 0.1f;
    }
    
    ClampWorldState();
}

void UBP_WorldStateSubsystem::ClampWorldState() {
    // Ensure all values stay within valid ranges
    
    WorldState.Economy.TotalMoney = FMath::Max(0.0f, WorldState.Economy.TotalMoney);
    WorldState.Economy.FoodSupply = FMath::Clamp(WorldState.Economy.FoodSupply, 0.0f, 100.0f);
    WorldState.Economy.MaterialsSupply = FMath::Clamp(WorldState.Economy.MaterialsSupply, 0.0f, 100.0f);
    
    WorldState.Culture.MoraleMod = FMath::Max(0.5f, WorldState.Culture.MoraleMod); // Don't go below 0.5
    WorldState.Culture.StabilityRating = FMath::Clamp(WorldState.Culture.StabilityRating, 0.0f, 100.0f);
    WorldState.Culture.AverageCitizenHappiness = FMath::Clamp(WorldState.Culture.AverageCitizenHappiness, -100.0f, 100.0f);
    
    WorldState.Infrastructure.AverageBuildingQuality = FMath::Clamp(WorldState.Infrastructure.AverageBuildingQuality, 0.0f, 100.0f);
    WorldState.Infrastructure.RoadCoverage = FMath::Clamp(WorldState.Infrastructure.RoadCoverage, 0.0f, 100.0f);
    WorldState.Infrastructure.DisasterPreparedness = FMath::Clamp(WorldState.Infrastructure.DisasterPreparedness, 0.0f, 100.0f);
    
    WorldState.Technology.ProgressToNextEra = FMath::Clamp(WorldState.Technology.ProgressToNextEra, 0.0f, 100.0f);
    
    WorldState.PopulationCount = FMath::Max(0, WorldState.PopulationCount);
}
