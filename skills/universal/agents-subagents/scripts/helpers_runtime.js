// A small JSON-schema check: type, required, properties, items, enum, minItems, minLength.
function conforms(value, schema) {
  if (!schema) return true;
  if (schema.enum && !schema.enum.includes(value)) return false;
  switch (schema.type) {
    case 'object':
      if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
      if ((schema.required || []).some((key) => !(key in value))) return false;
      return Object.entries(schema.properties || {}).every(([key, sub]) => !(key in value) || conforms(value[key], sub));
    case 'array':
      return Array.isArray(value) && value.length >= (schema.minItems || 0) && value.every((item) => conforms(item, schema.items));
    case 'string':
      return typeof value === 'string' && value.trim().length >= (schema.minLength || 0);
    case 'boolean':
      return typeof value === 'boolean';
    case 'integer':
      return Number.isInteger(value);
    case 'number':
      return typeof value === 'number';
    default:
      return true;
  }
}

// One label line, then the value as one JSON line: text inside it never reads as a prompt line.
const dataBlock = (label, value) => [label + ' — ' + DATA_NOTE, JSON.stringify(value === undefined ? null : value)];

async function ask(prompt, options) {
  try {
    return await agent(prompt, options);
  } catch (error) {
    log('Agent ' + options.label + ' failed: ' + String((error && error.message) || error));
    return null;
  }
}
