# Offline improvement results, 2026-09-15

V43's displayed Kaggle score was2596.5 at20:49UTC on September15; V4 was2430.2. These are observed scores and may change. The signed-in submission page was checked only after the user requested it.

| Experiment | Result | Decision |
|---|---|---|
| Seven-turn sale advance |24/24wins vsV43 on12freshseeds, meanmargin+1869.6; noerrorgames |Retain research candidate; external comparison not yet run |
| Eight-turn sale advance |24/24wins vsV43, meanmargin+1790.4;12/12wins vsV4/Barnyard |Packaged asV44 and submitted at user's request |
| Extra care/watering during idle turns |10exactties despite500added actions |Rejected |
| Worker/storage audit |53units actually discarded overnight across3games; no final sellable inventory |Next targeted improvement: avoid storage losses while preserving feed reserves |
| Wider evaluation |V43/V4 each8/8wins againsttwo independent policies; someV43coinmargin regressions |Do not assume mirror gains transfer universally |
| Market uncertainty stress |Counterexamples when rival hiddenstock/order differs from assumedmirror |Next improvement: condition timing/ordering on opponent evidence |

V44 changes one constant in the testedV43 source: the stock-backed sale reservation bound grows from6to8turns. Field commands and the queue optimizer are unchanged. Both actual Kaggle file-loader games completed720states in both seats.24official-market optimizer checks passed. Maximum observed V44 holdout decision time455.976ms under concurrent local load.

H8's external wins were preserved, but it did not dominateV43: againstV4 its margin was10to152coins lower pergame; againstBarnyard changes ranged-21to+427. The user requested submission after reviewing the score. Local wins do not guarantee a higher Kaggle rating.

The submitted policy is one Python agent with cooperating farm-schedule, worker-repair, supply, market and endgame controllers. The research tasks operate outside the game. See HOW-THE-AGENT-WORKS.md for the turn-by-turn explanation.

Reports, raw game records, candidate sources, build hashes and reproduction scripts are under offline-research. V44's exact archive and source are under v44. Original V43 artifacts remain at the output root. This experiment snapshot is also copied to H:/Kaggriculture/experiments/2026-09-15.

Seat swaps are paired observations. The original80games used20seedvalues and44finalshopsequences, with36/40seatpairs returning identical balances. Weed and shop generation share random-number consumption; changes to either farm can affect later shops even at the same seed. Per-game shop sequences are recorded in the evidence.

Actual discarded stock:19eggs,27wheat,2strawberries,1milk,4fertilizer. Its2513quote-marked value is descriptive, not promised recoverable profit: fertilizer is not sellable, feed has future uses, and extra sales change market prices.

Submission update: the user subsequently requested submission. The exact testedH8source was packaged asV44 and Kaggle accepted it withPendingstatus. H7 remains unsubmitted. See v44/submission-status.json.
