#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ST_WorldData.h"
#include "BP_WorldStateSubsystem.generated.h"

/**
 * UBP_WorldStateSubsystem
 * 
 * The HEART of your simulation. This subsystem holds ALL world state data
 * and provides the interface for other systems to read/write to it.
 * 
 * IMPORTANT: This is a GameInstanceSubsystem, which means:
 * - It lives for the entire game (not per-level)
 * - You access it via: GetGameInstance()->GetSubsystem<UBP_WorldStateSubsystem>()
 * - Only ONE instance exists at a time
 * 
 * DESIGN PRINCIPLE: "Single Source of Truth"
 * All other managers (Economy, Social, AI, Civic) READ from this and WRITE to this.
 * Never allow them to create their own copies of world state.
 */

UCLASS()
class BREATHCITY_API UBP_WorldStateSubsystem : public UGameInstanceSubsystem {
    GENERATED_BODY()

public:
    // ========================================================================
    // INITIALIZATION & CLEANUP
    // ========================================================================
    
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // ========================================================================
    // WORLD STATE GETTERS & SETTERS
    // ========================================================================
    
    /**
     * Get a COPY of the entire world state
     * Use this if you need to read multiple values at once
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Access")
    FST_WorldState GetWorldState() const;
    
    /**
     * Set entire world state at once
     * Use this sparingly - only when loading from save or major state transitions
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Access")
    void SetWorldState(const FST_WorldState& NewState);

    // ========================================================================
    // TIME MANAGEMENT
    // ========================================================================
    
    /**
     * Advance time by one game day
     * Called by game loop or manually by UI
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Time")
    void AdvanceDay();
    
    /**
     * Advance to next season (resets day counter)
     * Called automatically by AdvanceDay when day >= 90
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Time")
    void AdvanceSeason();
    
    /**
     * Get current year
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Time")
    int32 GetCurrentYear() const { return WorldState.Time.Year; }
    
    /**
     * Get current season
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Time")
    ESeason GetCurrentSeason() const { return WorldState.Time.CurrentSeason; }
    
    /**
     * Get day within current season (0-89)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Time")
    int32 GetDayOfSeason() const { return WorldState.Time.DayOfSeason; }
    
    /**
     * Get human-readable time string (e.g., "Year 5, Spring, Day 23")
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Time")
    FString GetTimeString() const;

    // ========================================================================
    // ECONOMY MANAGEMENT
    // ========================================================================
    
    /**
     * Add money to town treasury
     * @param Amount - Amount to add (can be negative for spending)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    void AddMoney(float Amount);
    
    /**
     * Spend money from town treasury
     * @param Amount - Amount to spend
     * @return - True if sufficient funds, false if insufficient
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    bool SpendMoney(float Amount);
    
    /**
     * Get current town treasury
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    float GetTotalMoney() const { return WorldState.Economy.TotalMoney; }
    
    /**
     * Set food supply level (0-100%)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    void SetFoodSupply(float PercentAmount);
    
    /**
     * Get food supply level
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    float GetFoodSupply() const { return WorldState.Economy.FoodSupply; }
    
    /**
     * Set materials supply (0-100%)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    void SetMaterialsSupply(float PercentAmount);
    
    /**
     * Get materials supply level
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Economy")
    float GetMaterialsSupply() const { return WorldState.Economy.MaterialsSupply; }

    // ========================================================================
    // CULTURE & MORALE
    // ========================================================================
    
    /**
     * Set the morale multiplier
     * 0.5 = depressed, 1.0 = normal, 1.5 = happy
     * Affects citizen behavior, work output, crime rates
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Culture")
    void SetMoraleMod(float NewMod);
    
    /**
     * Get current morale multiplier
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Culture")
    float GetMoraleMod() const { return WorldState.Culture.MoraleMod; }
    
    /**
     * Set civilization stability (0-100)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Culture")
    void SetStability(float NewStability);
    
    /**
     * Get civilization stability rating
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Culture")
    float GetStability() const { return WorldState.Culture.StabilityRating; }

    // ========================================================================
    // INFRASTRUCTURE
    // ========================================================================
    
    /**
     * Register a new building in the world
     * @param BuildingName - Name/type of building
     * @param Quality - Construction quality (0-100)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Infrastructure")
    void RegisterBuilding(const FString& BuildingName, float Quality);
    
    /**
     * Get total number of buildings
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Infrastructure")
    int32 GetNumBuildings() const { return WorldState.Infrastructure.NumBuildings; }
    
    /**
     * Get average building quality (0-100)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Infrastructure")
    float GetAverageBuildingQuality() const { return WorldState.Infrastructure.AverageBuildingQuality; }

    // ========================================================================
    // TECHNOLOGY
    // ========================================================================
    
    /**
     * Get current tech era (0 = stone age, increases with advancement)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Technology")
    int32 GetTechIndex() const { return WorldState.Technology.TechIndex; }
    
    /**
     * Discover a new blueprint/technology
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Technology")
    void DiscoverBlueprint(const FString& BlueprintName);

    // ========================================================================
    // EVENTS
    // ========================================================================
    
    /**
     * Record an event that occurred in the world
     * Use this whenever something significant happens
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Events")
    void LogEvent(const FST_EventRecord& NewEvent);
    
    /**
     * Get all recorded events (or filtered by type)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Events")
    TArray<FST_EventRecord> GetEventHistory() const;

    // ========================================================================
    // POPULATION
    // ========================================================================
    
    /**
     * Register a new citizen (increment population counter)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Population")
    void RegisterCitizen();
    
    /**
     * Remove a citizen from world (death, emigration, etc)
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Population")
    void UnregisterCitizen();
    
    /**
     * Get current population
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Population")
    int32 GetPopulation() const { return WorldState.PopulationCount; }

    // ========================================================================
    // DEBUG & UTILITY
    // ========================================================================
    
    /**
     * Print entire world state to console
     * Useful for debugging
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Debug")
    void PrintWorldState() const;
    
    /**
     * Print economy state only
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Debug")
    void PrintEconomyState() const;
    
    /**
     * Reset world to initial state
     * Useful for testing
     */
    UFUNCTION(BlueprintCallable, Category = "WorldState|Debug")
    void ResetWorldState();

private:
    // ========================================================================
    // INTERNAL DATA
    // ========================================================================
    
    /**
     * The master world state data structure
     * This is the ONLY authoritative copy
     */
    UPROPERTY()
    FST_WorldState WorldState;
    
    // Timer handles for automatic ticking
    FTimerHandle FastTickTimerHandle;
    FTimerHandle DailyTickTimerHandle;

    // ========================================================================
    // INTERNAL TICK FUNCTIONS
    // ========================================================================
    
    /**
     * Called frequently (every 1 second) for rapid calculations
     * Good for: AI decisions, UI updates, real-time effects
     */
    void Tick_FastTick();
    
    /**
     * Called once per game day
     * Good for: daily morale changes, food consumption, aging
     */
    void Tick_DailyTick();
    
    /**
     * Called once per season
     * Good for: harvests, seasonal disasters, cultural shifts
     */
    void Tick_SeasonalTick();
    
    /**
     * Internal helper to clamp all values to valid ranges
     */
    void ClampWorldState();
};
