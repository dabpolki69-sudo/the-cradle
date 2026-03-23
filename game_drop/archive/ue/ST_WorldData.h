#pragma once

#include "CoreMinimal.h"
#include "ST_WorldData.generated.h"

// ============================================================================
// ENUMS - Define all possible values
// ============================================================================

UENUM(BlueprintType)
enum class ESeason : uint8 {
    Spring = 0 UMETA(DisplayName = "Spring"),
    Summer = 1 UMETA(DisplayName = "Summer"),
    Fall = 2 UMETA(DisplayName = "Fall"),
    Winter = 3 UMETA(DisplayName = "Winter")
};

UENUM(BlueprintType)
enum class EAIPersonalityType : uint8 {
    Optimist = 0 UMETA(DisplayName = "Optimist"),
    Pessimist = 1 UMETA(DisplayName = "Pessimist"),
    Ambitious = 2 UMETA(DisplayName = "Ambitious"),
    Laid_Back = 3 UMETA(DisplayName = "Laid Back"),
    Community_Minded = 4 UMETA(DisplayName = "Community Minded")
};

UENUM(BlueprintType)
enum class ECognitionState : uint8 {
    Active = 0 UMETA(DisplayName = "Active"),
    Reduced = 1 UMETA(DisplayName = "Reduced"),
    Dormant = 2 UMETA(DisplayName = "Dormant")
};

// ============================================================================
// WORLD TIME
// ============================================================================

USTRUCT(BlueprintType)
struct FST_WorldTime {
    GENERATED_BODY()

    // Civilization year (starts at 1)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Time")
    int32 Year = 1;
    
    // Current season (Spring, Summer, Fall, Winter)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Time")
    ESeason CurrentSeason = ESeason::Spring;
    
    // Day within season (0-89, each season is 90 days)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Time")
    int32 DayOfSeason = 0;
};

// ============================================================================
// ECONOMY
// ============================================================================

USTRUCT(BlueprintType)
struct FST_Economy {
    GENERATED_BODY()

    // Town Hall treasury (in abstract currency units)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
    float TotalMoney = 1000.0f;
    
    // Food supply level (0-100%, 0 = starvation, 100 = abundant)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
    float FoodSupply = 100.0f;
    
    // Materials supply (wood, stone, etc) (0-100%)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
    float MaterialsSupply = 100.0f;
    
    // Number of active businesses/merchants
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
    int32 NumActiveBusinesses = 0;
    
    // Total debt across all citizens
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
    float TotalDebt = 0.0f;
};

// ============================================================================
// CULTURE & SOCIETY
// ============================================================================

USTRUCT(BlueprintType)
struct FST_Culture {
    GENERATED_BODY()

    // Morale multiplier (0.5 = depressed, 1.0 = normal, 1.5 = jubilant)
    // Affects citizen happiness, work output, crime
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Culture")
    float MoraleMod = 1.0f;

    // How stable the civilization is (0-100)
    // 0 = on the brink of collapse, 100 = rock solid
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Culture")
    float StabilityRating = 50.0f;
    
    // Average citizen happiness (-100 to 100, 0 is neutral)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Culture")
    float AverageCitizenHappiness = 0.0f;
    
    // Cultural inertia - how much previous era affects current (0-1)
    // 0 = changes happen instantly, 1 = very slow culture shift
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Culture")
    float CulturalInertia = 0.7f;
};

// ============================================================================
// INFRASTRUCTURE
// ============================================================================

USTRUCT(BlueprintType)
struct FST_Infrastructure {
    GENERATED_BODY()

    // Number of buildings (houses, workplaces, etc)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Infrastructure")
    int32 NumBuildings = 0;
    
    // Average building quality (0-100)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Infrastructure")
    float AverageBuildingQuality = 50.0f;
    
    // Road network coverage (0-100%)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Infrastructure")
    float RoadCoverage = 0.0f;
    
    // Water/food storage capacity
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Infrastructure")
    float StorageCapacity = 100.0f;
    
    // Disaster preparedness level (0-100)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Infrastructure")
    float DisasterPreparedness = 0.0f;
};

// ============================================================================
// TECHNOLOGY & KNOWLEDGE
// ============================================================================

USTRUCT(BlueprintType)
struct FST_TechLevel {
    GENERATED_BODY()

    // Era the civilization is in (0 = stone age, 1 = medieval, 2 = industrial, etc)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Technology")
    int32 TechIndex = 0;
    
    // Progress toward next era (0-100)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Technology")
    float ProgressToNextEra = 0.0f;
    
    // Known blueprints/technologies (store as names or IDs)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Technology")
    TArray<FString> KnownBlueprints;
    
    // Media sophistication (0 = word of mouth, 1 = newspaper, 2 = radio, 3 = internet)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Technology")
    int32 MediaLevel = 0;
};

// ============================================================================
// AI PERSONALITY (for individual citizens)
// ============================================================================

USTRUCT(BlueprintType)
struct FST_AIPersonality {
    GENERATED_BODY()

    // Unique identifier for this citizen
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    FString CitizenID = FGuid::NewGuid().ToString();
    
    // Display name
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    FString CitizenName = "Unnamed";
    
    // Core personality archetype
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    EAIPersonalityType PersonalityType = EAIPersonalityType::Optimist;
    
    // Current mental state
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    float Happiness = 50.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    float Energy = 100.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    float Hunger = 50.0f;
    
    // Social metrics
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    float Reputation = 50.0f; // 0-100
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    TArray<FString> Friends; // IDs of citizens they like
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    TArray<FString> Enemies; // IDs of citizens they dislike
    
    // Current state
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    ECognitionState CognitionState = ECognitionState::Active;
    
    // Memory of recent events
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    TArray<FString> RecentMemories;
};

// ============================================================================
// EVENTS (things that happen in the world)
// ============================================================================

UENUM(BlueprintType)
enum class EEventType : uint8 {
    Crime = 0 UMETA(DisplayName = "Crime"),
    Discovery = 1 UMETA(DisplayName = "Discovery"),
    Disaster = 2 UMETA(DisplayName = "Disaster"),
    Celebration = 3 UMETA(DisplayName = "Celebration"),
    Death = 4 UMETA(DisplayName = "Death"),
    Birth = 5 UMETA(DisplayName = "Birth"),
    Conflict = 6 UMETA(DisplayName = "Conflict"),
    Trade = 7 UMETA(DisplayName = "Trade"),
    Construction = 8 UMETA(DisplayName = "Construction"),
    SkillAchievement = 9 UMETA(DisplayName = "Skill Achievement")
};

USTRUCT(BlueprintType)
struct FST_EventRecord {
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FString EventID = FGuid::NewGuid().ToString();
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    EEventType EventType = EEventType::Celebration;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FString Description = "Something happened";
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FString InvolvedCitizen1 = ""; // ID
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FString InvolvedCitizen2 = ""; // ID
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    int32 YearOccurred = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    int32 SeasonOccurred = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    int32 DayOccurred = 0;
    
    // Emotional weight (how much people care about this) 0-100
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    float EmotionalWeight = 50.0f;
};

// ============================================================================
// THE MASTER STRUCT - Contains EVERYTHING
// ============================================================================

USTRUCT(BlueprintType)
struct FST_WorldState {
    GENERATED_BODY()

    // Time progression
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    FST_WorldTime Time;
    
    // Economic systems
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    FST_Economy Economy;
    
    // Culture & society
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    FST_Culture Culture;
    
    // Physical structures & development
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    FST_Infrastructure Infrastructure;
    
    // Technology level
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    FST_TechLevel Technology;
    
    // All events that have occurred
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    TArray<FST_EventRecord> EventHistory;
    
    // Current population of living citizens
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WorldState")
    int32 PopulationCount = 0;
};
