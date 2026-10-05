# LiveKit Agents patterns

Use LiveKit Agents when a call needs a LiveKit room, SIP participant, or room media. The Python [v0.x migration guide](https://docs.livekit.io/reference/migration-guides/v0-migration/python/) replaces the old voice pipeline class with `AgentSession` and `Agent`; check the installed SDK against the [current voice quickstart](https://docs.livekit.io/agents/start/voice-ai/) before copying a sample. The older class was deprecated at the 1.0 migration. The migration guide does not establish a later removal version.

## Single caller: chained STT, LLM, TTS

This is the current session and server shape from LiveKit's [Python migration example](https://docs.livekit.io/reference/migration-guides/v0-migration/python/) and [quickstart](https://docs.livekit.io/agents/start/voice-ai/). Install the agents package and the selected provider plugins, then supply their credentials through the deployment environment. The sample has not been exercised against live provider accounts.

```python
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession
from livekit.plugins import deepgram, elevenlabs, google, silero


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a phone assistant. Keep responses short and spoken."
        )


server = AgentServer()


@server.rtc_session(agent_name="phone-assistant")
async def phone_assistant(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(),
        llm=google.LLM(),
        tts=elevenlabs.TTS(),
        vad=silero.VAD.load(),
    )
    await session.start(room=ctx.room, agent=Assistant())
    await session.generate_reply(
        instructions="Greet the caller and explain how you can help."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
```

`AgentSession` owns listening, turn handling, interruption, speech output, and cleanup. Start it with `room=ctx.room`; do not separately start an agent on a participant or call a legacy `say()` method. For a fixed greeting, use `session.say(...)`; for a contextual greeting, use `session.generate_reply(...)`. Configure endpointing and interruptions with [TurnHandlingOptions](https://docs.livekit.io/reference/agents/turn-handling-options/) only after measuring target calls. Test a user speaking over the bot and a false interruption, because either can fail despite a good median latency.

## Participant and room lifecycle

By default, a session links to the first eligible participant. For a known caller identity, pass `room_io.RoomOptions(participant_identity=...)` to `session.start`; see [room options](https://docs.livekit.io/agents/logic/sessions/#room-options). Do not create a new session in a `participant_connected` callback for every room event. For one agent process per participant, use the [publisher job type](https://docs.livekit.io/agents/server/options/#request-handler) and inspect `JobContext.publisher`; for a shared room agent, define which participant may issue commands and what happens when that participant leaves. The session's close options and job lifecycle are documented in [Agent session](https://docs.livekit.io/agents/logic/sessions/) and [Job lifecycle](https://docs.livekit.io/agents/server/job/).

```python
from livekit.agents import room_io

await session.start(
    room=ctx.room,
    agent=Assistant(),
    room_options=room_io.RoomOptions(participant_identity=caller_identity),
)
```

Use [agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch/) for named agent routing. If a call transfers to a human or another bot, use an explicit handoff and preserve the call state required after transfer; see [agents and handoffs](https://docs.livekit.io/agents/logic/agents-handoffs/). Close resources on session end, and test disconnect and reconnect rather than assuming the old room persists.

## Tools and handoff

Put callable tools on an `Agent` with `@function_tool`; the old free-form function-call event and `tools=` on a provider LLM do not define the current tool contract. The [function-tool guide](https://docs.livekit.io/agents/logic/tools/definition/) documents `RunContext`, error handling, interruption and tool result behavior.

```python
from livekit.agents import Agent, RunContext, function_tool


class ServiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="Help callers with order status.")

    @function_tool()
    async def lookup_order(self, context: RunContext, order_id: str) -> str:
        """Read an order's status.

        Args:
            order_id: The caller's order identifier.
        """
        # Replace with an authenticated lookup; never trust a spoken ID alone.
        return await order_store.status_for_verified_caller(order_id)
```

The tool body assumes an application-owned `order_store` and caller verification; it is an integration seam, not a runnable database example. For writes such as changing an order or initiating a transfer, confirm the action in code and use the interruption handling documented in the tool guide so a barge-in cannot leave a partial write. Keep credentials out of source and tool output.

## DTMF and IVR

Subscribe to `room.on("sip_dtmf_received")` with a synchronous callback receiving one `rtc.SipDTMF` object. Run the validated digit through the IVR state machine and schedule speech from the session. LiveKit's [DTMF guide](https://docs.livekit.io/telephony/features/dtmf/) defines the event shape and the separate outbound `publish_dtmf` API. Use its [GetDtmfTask](https://docs.livekit.io/telephony/features/dtmf/) when collecting a sequence of digits. Do not put payment-card digits into transcripts or model context; use the payment path in [voice-safety-compliance.md](voice-safety-compliance.md).

## Observability and recording

Use `AgentSession` events (`user_input_transcribed`, `conversation_item_added`, state changes, `close`) for per-call traces and completion metrics; the previous speech-committed callbacks do not apply. See [session events](https://docs.livekit.io/agents/logic/sessions/#events) and [data hooks](https://docs.livekit.io/agents/build/record). Gate transcript and recording capture on the call's consent policy, redact sensitive fields before storage, and correlate logs by call ID without logging raw identity by default. For room recording, use the [egress API](https://docs.livekit.io/home/egress/overview/) with deployment-managed storage credentials; do not embed keys in examples or call source.

Measure end-of-turn, first-audio, interruption success, and tail latency on recorded or replayed target-call conditions. For cost and concurrency, obtain the current [LiveKit Cloud pricing](https://livekit.io/pricing) and [deployment guidance](https://docs.livekit.io/agents/ops/deployment/) at planning time, then load-test the exact agent, plugins, region and codecs. A fixed worker-to-call ratio is not portable across those choices.

## S2S

Use the same `AgentSession` and `Agent` shape with a realtime model as the session LLM; the [voice quickstart](https://docs.livekit.io/agents/start/voice-ai/) shows the current provider class and constructor. A realtime model does not require a separate STT and TTS pair. Verify model availability, transcript access, interruptions and tool behavior against the chosen provider before deployment; see [s2s-and-native-voice-apis.md](s2s-and-native-voice-apis.md).
