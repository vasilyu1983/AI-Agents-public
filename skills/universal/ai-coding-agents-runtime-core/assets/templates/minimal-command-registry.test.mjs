import assert from 'node:assert/strict';
import test from 'node:test';
import { CommandRegistry } from './minimal-command-registry.ts';

const command = (name, source, promptPath) => ({
  name, source, promptPath, description: name,
});

test('registerAll replaces the snapshot, shadow events, and cached resolutions', async () => {
  const registry = new CommandRegistry();
  registry.registerAll([
    command('review', 'builtin', 'old/review.md'),
    command('review', 'project', 'project/review.md'),
    command('removed', 'user', 'user/removed.md'),
  ]);
  assert.deepEqual(registry.shadowed(), [
    { name: 'review', winner: 'project', loser: 'builtin' },
  ]);
  await registry.resolve('review');
  await registry.resolve('removed');

  registry.registerAll([command('review', 'builtin', 'new/review.md')]);

  assert.deepEqual(registry.shadowed(), []);
  assert.deepEqual(registry.list().map(({ name }) => name), ['review']);
  assert.equal((await registry.resolve('review')).promptContent, '[prompt loaded from new/review.md]');
  await assert.rejects(registry.resolve('removed'), /Command not found/);
});

test('in-flight resolution cannot resurrect a command removed by reload', async () => {
  const registry = new CommandRegistry();
  registry.registerAll([command('gone', 'user', 'old/gone.md')]);

  const pending = registry.resolve('gone');
  registry.registerAll([]);

  await assert.rejects(pending, /changed during resolution: \/gone/);
  assert.equal(registry.has('gone'), false);
  await assert.rejects(registry.resolve('gone'), /Command not found/);
});

test('in-flight old definition cannot overwrite a replacement after reload', async () => {
  const registry = new CommandRegistry();
  registry.registerAll([command('review', 'builtin', 'old/review.md')]);

  const pending = registry.resolve('review');
  registry.registerAll([command('review', 'project', 'new/review.md')]);

  await assert.rejects(pending, /changed during resolution: \/review/);
  const current = await registry.resolve('review');
  assert.equal(current.source, 'project');
  assert.equal(current.promptContent, '[prompt loaded from new/review.md]');
});

test('invalidating another command does not abort an unrelated in-flight resolution', async () => {
  const registry = new CommandRegistry();
  registry.registerAll([command('a', 'user', 'a.md'), command('b', 'user', 'b.md')]);

  const pending = registry.resolve('a');
  registry.invalidate('b');

  assert.equal((await pending).promptContent, '[prompt loaded from a.md]');
});

test('invalidating the same command, or all commands, still aborts its in-flight resolution', async () => {
  const registry = new CommandRegistry();
  registry.registerAll([command('a', 'user', 'a.md')]);

  const pending = registry.resolve('a');
  registry.invalidate('a');
  await assert.rejects(pending, /changed during resolution: \/a/);

  const pendingAll = registry.resolve('a');
  registry.invalidateAll();
  await assert.rejects(pendingAll, /changed during resolution: \/a/);
});
