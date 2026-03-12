# Async Eventual Assertions

## Purpose
Use this guide for message-driven or eventually consistent flows.

## Polling Pattern
- Poll on a bounded interval.
- Stop immediately when condition matches.
- Fail with clear timeout diagnostics.

## Template
```csharp
public static async Task Eventually(
    Func<Task<bool>> condition,
    TimeSpan timeout,
    TimeSpan interval)
{
    DateTimeOffset deadline = DateTimeOffset.UtcNow + timeout;

    while (DateTimeOffset.UtcNow < deadline)
    {
        if (await condition())
        {
            return;
        }

        await Task.Delay(interval);
    }

    Assert.Fail($"Condition not met within {timeout}.");
}
```

## Rules
- Avoid `Thread.Sleep` in tests.
- Keep timeout and interval explicit per scenario.
- Log key ids and state snapshots on timeout.
