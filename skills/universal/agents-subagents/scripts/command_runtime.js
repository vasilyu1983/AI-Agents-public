// Engine `command`: check each enumerated arg, then return one deterministic shell command. No model agents.
const spec = WORKFLOW_MANIFEST.command;
const chosen = {};
for (const [name, option] of Object.entries(spec.options)) {
  const value = (args && args[name]) || option.default;
  if (!option.choices.includes(value)) {
    const last = option.choices[option.choices.length - 1];
    const list = option.choices.length > 2
      ? option.choices.slice(0, -1).join(', ') + ', or ' + last
      : option.choices.join(' or ');
    throw new Error(name + ' must be ' + list);
  }
  chosen[name] = value;
}

phase(spec.phase);
const command = spec.run + Object.entries(chosen).map(([name, value]) => ' --' + name + ' ' + value).join('');
log(command);

return { command, ...chosen, modelAgents: 0 };
