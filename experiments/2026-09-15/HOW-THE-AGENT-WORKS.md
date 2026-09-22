# How the Kaggriculture agent works

V43 is one submitted Python game policy with several cooperating controllers. The parallel research agents are developing and evaluating changes outside the game; they are not additional Kaggle players and do not call an LLM during play.

Each turn, the policy receives the public farms, current prices and shops, plus its own private stock. It returns one command per available worker and an ordered list of market transactions.

1. **Farm plan.** A stored schedule coordinates movement, planting, watering, animal care, harvesting and transport. A router selects a schedule using the early shops; it changes to the closing schedule near the end of the season.
2. **Worker and supply controllers.** Reactive layers handle weeds, missing inputs, delayed jobs, extra crop workers and livestock workers. They reserve food, seeds, money and shed room so an attractive immediate action does not break later work.
3. **Market controller.** V43 moves eligible, stock-backed sales up to six turns earlier within its guarded scheduling window. It records the quantities sold early so the future scheduled sale is reduced. For similar farms, it also optimizes all-sale order queues under an explicit equal-stock opponent scenario.
4. **Endgame controller.** A bounded local simulation can improve the final seven turns, collect remaining goods and sell available stock. It abstains when the shadow model cannot safely represent active obligations.

The market model does not know the opponent's private shed inventory. Similar visible farms are evidence of similar production, not proof that the opponent will sell the same goods at the same moment.

## What could improve results

- **Sale timing conditioned on competition.** Longer sale advances can win contested sales but may give up later price recovery. Test timing against several opponent behaviors, not only a mirror.
- **Worker actions with measurable value.** Diagnose wasted actions, input shortages and missed collections. Preserve feeding, transport and scheduled commitments before changing a worker's job.
- **Shop-aware production.** Repeated shop draws create different demand patterns. A production change should pay for its seeds, animals, labor and travel before the season ends.
- **Broader validation.** Win/loss against strong, different policies is the primary local criterion. Coins help explain changes; high earnings against the starter bot alone do not establish competitive strength.

## Promotion requirements

Keep submitted V43 frozen. Screen a small number of variants, then test the selected candidate on unused seeds in both seats. Include V43 in tests against the same external opponents. Report failures, minimum margin, decision time and actual shop sequences. A shared seed does not necessarily produce the same town after a physical policy change, because weed processing and shop draws share random-number consumption.

No new submission or live Kaggle result check is part of this offline experiment batch.
