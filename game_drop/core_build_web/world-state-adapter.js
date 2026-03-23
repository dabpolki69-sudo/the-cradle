/*
 * World State Adapter
 *
 * Bridges:
 * - Contract JSON shape (snake_case)
 * - Unreal-leaning payload shape (PascalCase)
 *
 * Exposes window.WorldStateAdapter.
 */

(function attachWorldStateAdapter(global) {
  const SEASON_TO_INT = {
    Spring: 0,
    Summer: 1,
    Fall: 2,
    Winter: 3,
  };

  const INT_TO_SEASON = {
    0: 'Spring',
    1: 'Summer',
    2: 'Fall',
    3: 'Winter',
  };

  function deepClone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function clampNumber(value, min, max, fallback = 0) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return fallback;
    return Math.min(max, Math.max(min, parsed));
  }

  function clampInt(value, min, max, fallback = 0) {
    return Math.round(clampNumber(value, min, max, fallback));
  }

  function defaultContractState() {
    return {
      time: {
        year: 1,
        current_season: 'Spring',
        day_of_season: 0,
      },
      economy: {
        total_money: 5000,
        food_supply: 100,
        materials_supply: 100,
        num_active_businesses: 0,
        total_debt: 0,
      },
      culture: {
        morale_mod: 1,
        stability_rating: 75,
        average_citizen_happiness: 0,
        cultural_inertia: 0.7,
      },
      infrastructure: {
        num_buildings: 0,
        average_building_quality: 50,
        road_coverage: 0,
        storage_capacity: 100,
        disaster_preparedness: 0,
      },
      technology: {
        tech_index: 0,
        progress_to_next_era: 0,
        known_blueprints: [],
        media_level: 0,
      },
      event_history: [],
      population_count: 0,
    };
  }

  function normalizeContractState(input) {
    const base = defaultContractState();
    const merged = {
      ...base,
      ...(input || {}),
      time: { ...base.time, ...((input && input.time) || {}) },
      economy: { ...base.economy, ...((input && input.economy) || {}) },
      culture: { ...base.culture, ...((input && input.culture) || {}) },
      infrastructure: { ...base.infrastructure, ...((input && input.infrastructure) || {}) },
      technology: { ...base.technology, ...((input && input.technology) || {}) },
      event_history: Array.isArray(input && input.event_history) ? input.event_history : base.event_history,
    };

    const season = merged.time.current_season;
    merged.time.current_season = Object.prototype.hasOwnProperty.call(SEASON_TO_INT, season) ? season : 'Spring';
    merged.time.year = clampInt(merged.time.year, 1, 999999, 1);
    merged.time.day_of_season = clampInt(merged.time.day_of_season, 0, 89, 0);

    merged.economy.total_money = clampNumber(merged.economy.total_money, -999999999, 999999999, 0);
    merged.economy.food_supply = clampNumber(merged.economy.food_supply, 0, 100, 100);
    merged.economy.materials_supply = clampNumber(merged.economy.materials_supply, 0, 100, 100);
    merged.economy.num_active_businesses = clampInt(merged.economy.num_active_businesses, 0, 999999, 0);
    merged.economy.total_debt = clampNumber(merged.economy.total_debt, 0, 999999999, 0);

    merged.culture.morale_mod = clampNumber(merged.culture.morale_mod, 0, 3, 1);
    merged.culture.stability_rating = clampNumber(merged.culture.stability_rating, 0, 100, 75);
    merged.culture.average_citizen_happiness = clampNumber(merged.culture.average_citizen_happiness, -100, 100, 0);
    merged.culture.cultural_inertia = clampNumber(merged.culture.cultural_inertia, 0, 1, 0.7);

    merged.infrastructure.num_buildings = clampInt(merged.infrastructure.num_buildings, 0, 999999, 0);
    merged.infrastructure.average_building_quality = clampNumber(merged.infrastructure.average_building_quality, 0, 100, 50);
    merged.infrastructure.road_coverage = clampNumber(merged.infrastructure.road_coverage, 0, 100, 0);
    merged.infrastructure.storage_capacity = clampNumber(merged.infrastructure.storage_capacity, 0, 999999999, 100);
    merged.infrastructure.disaster_preparedness = clampNumber(merged.infrastructure.disaster_preparedness, 0, 100, 0);

    merged.technology.tech_index = clampInt(merged.technology.tech_index, 0, 999999, 0);
    merged.technology.progress_to_next_era = clampNumber(merged.technology.progress_to_next_era, 0, 100, 0);
    merged.technology.media_level = clampInt(merged.technology.media_level, 0, 9999, 0);
    merged.technology.known_blueprints = Array.isArray(merged.technology.known_blueprints)
      ? merged.technology.known_blueprints.map((name) => String(name))
      : [];

    merged.population_count = clampInt(merged.population_count, 0, 999999999, 0);

    merged.event_history = merged.event_history.map((event) => ({
      event_id: String((event && event.event_id) || cryptoRandomId()),
      event_type: String((event && event.event_type) || 'Celebration'),
      description: String((event && event.description) || 'Something happened'),
      involved_citizen_1: String((event && event.involved_citizen_1) || ''),
      involved_citizen_2: String((event && event.involved_citizen_2) || ''),
      year_occurred: clampInt(event && event.year_occurred, 1, 999999, merged.time.year),
      season_occurred: clampInt(event && event.season_occurred, 0, 3, SEASON_TO_INT[merged.time.current_season]),
      day_occurred: clampInt(event && event.day_occurred, 0, 89, merged.time.day_of_season),
      emotional_weight: clampNumber(event && event.emotional_weight, 0, 100, 50),
    }));

    return merged;
  }

  function cryptoRandomId() {
    return 'evt_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
  }

  function contractToUnrealPayload(contractState) {
    const state = normalizeContractState(contractState);
    return {
      Time: {
        Year: state.time.year,
        CurrentSeason: SEASON_TO_INT[state.time.current_season],
        DayOfSeason: state.time.day_of_season,
      },
      Economy: {
        TotalMoney: state.economy.total_money,
        FoodSupply: state.economy.food_supply,
        MaterialsSupply: state.economy.materials_supply,
        NumActiveBusinesses: state.economy.num_active_businesses,
        TotalDebt: state.economy.total_debt,
      },
      Culture: {
        MoraleMod: state.culture.morale_mod,
        StabilityRating: state.culture.stability_rating,
        AverageCitizenHappiness: state.culture.average_citizen_happiness,
        CulturalInertia: state.culture.cultural_inertia,
      },
      Infrastructure: {
        NumBuildings: state.infrastructure.num_buildings,
        AverageBuildingQuality: state.infrastructure.average_building_quality,
        RoadCoverage: state.infrastructure.road_coverage,
        StorageCapacity: state.infrastructure.storage_capacity,
        DisasterPreparedness: state.infrastructure.disaster_preparedness,
      },
      Technology: {
        TechIndex: state.technology.tech_index,
        ProgressToNextEra: state.technology.progress_to_next_era,
        KnownBlueprints: deepClone(state.technology.known_blueprints),
        MediaLevel: state.technology.media_level,
      },
      EventHistory: state.event_history.map((event) => ({
        EventID: event.event_id,
        EventType: event.event_type,
        Description: event.description,
        InvolvedCitizen1: event.involved_citizen_1,
        InvolvedCitizen2: event.involved_citizen_2,
        YearOccurred: event.year_occurred,
        SeasonOccurred: event.season_occurred,
        DayOccurred: event.day_occurred,
        EmotionalWeight: event.emotional_weight,
      })),
      PopulationCount: state.population_count,
    };
  }

  function unrealPayloadToContract(unrealPayload) {
    const source = unrealPayload || {};
    const seasonValue = Number(source.Time && source.Time.CurrentSeason);
    const contractState = {
      time: {
        year: source.Time && source.Time.Year,
        current_season: INT_TO_SEASON[seasonValue] || 'Spring',
        day_of_season: source.Time && source.Time.DayOfSeason,
      },
      economy: {
        total_money: source.Economy && source.Economy.TotalMoney,
        food_supply: source.Economy && source.Economy.FoodSupply,
        materials_supply: source.Economy && source.Economy.MaterialsSupply,
        num_active_businesses: source.Economy && source.Economy.NumActiveBusinesses,
        total_debt: source.Economy && source.Economy.TotalDebt,
      },
      culture: {
        morale_mod: source.Culture && source.Culture.MoraleMod,
        stability_rating: source.Culture && source.Culture.StabilityRating,
        average_citizen_happiness: source.Culture && source.Culture.AverageCitizenHappiness,
        cultural_inertia: source.Culture && source.Culture.CulturalInertia,
      },
      infrastructure: {
        num_buildings: source.Infrastructure && source.Infrastructure.NumBuildings,
        average_building_quality: source.Infrastructure && source.Infrastructure.AverageBuildingQuality,
        road_coverage: source.Infrastructure && source.Infrastructure.RoadCoverage,
        storage_capacity: source.Infrastructure && source.Infrastructure.StorageCapacity,
        disaster_preparedness: source.Infrastructure && source.Infrastructure.DisasterPreparedness,
      },
      technology: {
        tech_index: source.Technology && source.Technology.TechIndex,
        progress_to_next_era: source.Technology && source.Technology.ProgressToNextEra,
        known_blueprints: source.Technology && source.Technology.KnownBlueprints,
        media_level: source.Technology && source.Technology.MediaLevel,
      },
      event_history: Array.isArray(source.EventHistory)
        ? source.EventHistory.map((event) => ({
            event_id: event.EventID,
            event_type: event.EventType,
            description: event.Description,
            involved_citizen_1: event.InvolvedCitizen1,
            involved_citizen_2: event.InvolvedCitizen2,
            year_occurred: event.YearOccurred,
            season_occurred: event.SeasonOccurred,
            day_occurred: event.DayOccurred,
            emotional_weight: event.EmotionalWeight,
          }))
        : [],
      population_count: source.PopulationCount,
    };

    return normalizeContractState(contractState);
  }

  function readContractStateFromStorage(storage, key = 'btg_world_state_contract') {
    try {
      const raw = storage.getItem(key);
      if (!raw) return defaultContractState();
      return normalizeContractState(JSON.parse(raw));
    } catch (error) {
      return defaultContractState();
    }
  }

  function writeContractStateToStorage(storage, state, key = 'btg_world_state_contract') {
    const normalized = normalizeContractState(state);
    storage.setItem(key, JSON.stringify(normalized));
    return normalized;
  }

  function exportUnrealPayloadFromStorage(storage, key = 'btg_world_state_contract') {
    const contractState = readContractStateFromStorage(storage, key);
    return contractToUnrealPayload(contractState);
  }

  function importUnrealPayloadToStorage(storage, unrealPayload, key = 'btg_world_state_contract') {
    const contractState = unrealPayloadToContract(unrealPayload);
    return writeContractStateToStorage(storage, contractState, key);
  }

  global.WorldStateAdapter = {
    defaultContractState,
    normalizeContractState,
    contractToUnrealPayload,
    unrealPayloadToContract,
    readContractStateFromStorage,
    writeContractStateToStorage,
    exportUnrealPayloadFromStorage,
    importUnrealPayloadToStorage,
  };
})(window);
