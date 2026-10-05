---------------------------- MODULE IdempotentRetry ----------------------------
(* One logical agent tool call (e.g. "charge card") over a lossy network.   *)
(* The agent retries on timeout; server workers handle deliveries.          *)
(* Mode: "none"     = no idempotency key                                     *)
(*       "check"    = key checked, then executed, then recorded (3 steps)    *)
(*       "reserve"  = key reserved atomically at check; duplicate replies    *)
(*                    immediately                                            *)
(*       "complete" = reserve atomically; duplicate replies only after the   *)
(*                    original's result is recorded                          *)
EXTENDS Naturals
CONSTANTS Workers, MaxRetries, Mode

VARIABLES agent, retries, net, resp, wpc, key, execs
vars == <<agent, retries, net, resp, wpc, key, execs>>

Init == /\ agent = "idle" /\ retries = 0 /\ net = 0 /\ resp = 0
        /\ wpc = [w \in Workers |-> "free"]
        /\ key = "absent"          \* absent | reserved | completed
        /\ execs = 0

Send    == agent = "idle" /\ agent' = "waiting" /\ net' = net + 1
           /\ UNCHANGED <<retries, resp, wpc, key, execs>>
Retry   == agent = "waiting" /\ retries < MaxRetries
           /\ retries' = retries + 1 /\ net' = net + 1
           /\ UNCHANGED <<agent, resp, wpc, key, execs>>
Escalate == agent = "waiting" /\ retries = MaxRetries /\ agent' = "escalated"
           /\ UNCHANGED <<retries, net, resp, wpc, key, execs>>
Deliver(w) == net > 0 /\ wpc[w] = "free" /\ net' = net - 1
           /\ wpc' = [wpc EXCEPT ![w] = "received"]
           /\ UNCHANGED <<agent, retries, resp, key, execs>>
Check(w) == wpc[w] = "received"
           /\ (IF Mode = "none" \/ key = "absent"
                  THEN /\ wpc' = [wpc EXCEPT ![w] = "owner"]
                       /\ key' = (IF Mode \in {"reserve", "complete"} THEN "reserved" ELSE key)
                  ELSE /\ wpc' = [wpc EXCEPT ![w] = "duplicate"] /\ UNCHANGED key)
           /\ UNCHANGED <<agent, retries, net, resp, execs>>
Execute(w) == wpc[w] = "owner" /\ execs' = execs + 1
           /\ wpc' = [wpc EXCEPT ![w] = "executed"]
           /\ UNCHANGED <<agent, retries, net, resp, key>>
Record(w) == wpc[w] = "executed" /\ key' = (IF Mode = "none" THEN key ELSE "completed")
           /\ wpc' = [wpc EXCEPT ![w] = "free"] /\ resp' = resp + 1
           /\ UNCHANGED <<agent, retries, net, execs>>
ReplyDup(w) == wpc[w] = "duplicate" /\ (Mode = "complete" => key = "completed")
           /\ wpc' = [wpc EXCEPT ![w] = "free"] /\ resp' = resp + 1
           /\ UNCHANGED <<agent, retries, net, key, execs>>
LoseRequest  == net > 0 /\ net' = net - 1
           /\ UNCHANGED <<agent, retries, resp, wpc, key, execs>>
LoseResponse == resp > 0 /\ resp' = resp - 1
           /\ UNCHANGED <<agent, retries, net, wpc, key, execs>>
Receive == agent = "waiting" /\ resp > 0 /\ agent' = "done" /\ resp' = resp - 1
           /\ UNCHANGED <<retries, net, wpc, key, execs>>

Next == \/ Send \/ Retry \/ Escalate \/ Receive \/ LoseRequest \/ LoseResponse
        \/ \E w \in Workers : Deliver(w) \/ Check(w) \/ Execute(w) \/ Record(w) \/ ReplyDup(w)

Spec == Init /\ [][Next]_vars

TypeOK == /\ agent \in {"idle", "waiting", "done", "escalated"}
          /\ retries \in 0..MaxRetries /\ net \in Nat /\ resp \in Nat /\ execs \in Nat
AtMostOnce       == execs <= 1                     \* no double charge
AckImpliesEffect == agent = "done" => execs >= 1   \* no phantom success
\* Vacuity probes: each MUST be violated (i.e. the good path is reachable).
NeverDone        == agent /= "done"
NeverDoneAfterRetry == ~(agent = "done" /\ retries > 0)
=============================================================================
