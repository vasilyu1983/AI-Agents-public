# Completed synthetic example: rollback coordination

This fictional software example demonstrates traceability, not a measured safety result.

**Boundary:** deployment controller, rollback controller, database schema and running services. **Loss L1:** irreversible corruption of stored records. **Hazard H1:** a running writer uses an incompatible schema. **Assumption A1:** schema compatibility can be represented by a maintained version relation; this relation needs implementation evidence.

**Control structure:** deployment controller issues Deploy; rollback controller issues Rollback; services write records. Feedback includes active writer versions and schema version. Both controllers may follow their local rules yet act from inconsistent feedback.

| UCA | Context/category | Constraint | Verification/owner |
|---|---|---|---|
| U1: rollback controller issues Rollback | Provision while schema is incompatible with the old writer; H1/L1 | C1: execute rollback only if target writer is compatible with observed schema and active-write state | V1: injected incompatible-schema scenario must reject rollback; platform owner; planned |
| U2: deployment controller omits coordinated writer stop | Omission when incompatible migration begins; H1/L1 | C2: incompatible migration requires confirmed exclusion of incompatible writers | V2: migration with delayed stop acknowledgment must not proceed; platform owner; planned |
| U3: controller starts migration before writer-stop completion | Timing/order with delayed acknowledgment; H1/L1 | C3: migration transition must validate completion, not merely command dispatch | V3: reorder/delay acknowledgments and assert transition guard; platform owner; planned |

Duration is N/A for the discrete Rollback command. A continuous migration lock would need separate duration analysis if included in scope.

**Loss scenario S1:** stale writer feedback makes both controllers believe rollback is compatible. Proposed mechanism: coordinated state/version checks with concurrency control; design remains unresolved until implemented and reviewed. C1–C3 are analysis outputs; all tests are planned, so no safety or deployment-readiness claim follows. Residual unknowns: compatibility-map errors and external writers. Review trigger: changes to migration mode or feedback/coordination protocol.
