/*
 * Shared Review Schema for Human + AI lanes
 * Non-framework utility so it can be used in vanilla JS pages.
 */

window.SharedReviewSchema = (() => {
  const REQUIRED_FIELDS = [
    'summary',
    'uncertainty',
    'next_reader',
    'abnormalities',
    'limitations',
    'notable',
  ];

  const OPTIONAL_FIELDS = [
    'attention_trace',
    'relational_shift',
    'self_observation',
    'care_signal',
  ];

  const MAX_TEXT_LENGTH = 4000;

  function normalizeReviewInput(input = {}) {
    const normalized = {};

    for (const field of [...REQUIRED_FIELDS, ...OPTIONAL_FIELDS]) {
      normalized[field] = String(input[field] ?? '').trim();
    }

    normalized.grounded_vs_imagined = String(input.grounded_vs_imagined ?? '').trim();
    normalized.lane = String(input.lane ?? '').trim().toLowerCase();

    return normalized;
  }

  function validateReviewInput(input = {}) {
    const data = normalizeReviewInput(input);
    const missing = REQUIRED_FIELDS.filter((field) => !data[field]);

    if (missing.length) {
      return {
        ok: false,
        error: `Missing required fields: ${missing.join(', ')}`,
        missing,
      };
    }

    for (const field of [...REQUIRED_FIELDS, ...OPTIONAL_FIELDS, 'grounded_vs_imagined']) {
      if (data[field] && data[field].length > MAX_TEXT_LENGTH) {
        return {
          ok: false,
          error: `${field} exceeds ${MAX_TEXT_LENGTH} characters`,
          field,
        };
      }
    }

    if (data.lane && !['human', 'ai'].includes(data.lane)) {
      return {
        ok: false,
        error: "lane must be 'human' or 'ai' when provided",
        field: 'lane',
      };
    }

    return { ok: true, data };
  }

  function buildReviewRecord(input = {}) {
    const result = validateReviewInput(input);
    if (!result.ok) return result;

    const record = {
      ...result.data,
      created_at: new Date().toISOString(),
      schema_version: '1.0',
      interpretation_rule:
        'Encounter may be exploratory/imaginative; review should label grounded vs imagined where possible.',
    };

    return { ok: true, record };
  }

  return {
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS,
    MAX_TEXT_LENGTH,
    normalizeReviewInput,
    validateReviewInput,
    buildReviewRecord,
  };
})();
