# V50 experimental build

V50 is based on V48 and adds a narrow delivery-scheduling repair for a confirmed end-of-day strawberry overflow. The planner only intervenes when its replay predicts carried strawberry units will be discarded; it then uses a safe worker drop/pickup sequence and validates the queued action against the live position.

Validation completed 30 replay games with all games valid and no runtime or delivery-guard errors. V50 won 6/6 against V43, 4/6 against V47, 2/6 against V48 with four ties, and 4/6 against the wide opponent. Mean margins were +2689, +676, +254, and -532 respectively. The V48 control against wide in the same batch averaged -831, so the targeted change improved that comparison while preserving the existing production and input logic.

This package is prepared as an experimental candidate. It has not been submitted to Kaggle from this workspace because the authenticated browser upload path is currently blocked by the host approval limit.
