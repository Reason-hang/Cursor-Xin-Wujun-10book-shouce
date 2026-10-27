ZIP ?= _打包吴军10本电子书.zip
PY ?= python3

.PHONY: restore-check freeze probe test status verify-pack verify-anchors pack gates validate-spec p0 split p0-gates handover

restore-check: verify-pack freeze probe test status

freeze:
	$(PY) scripts/s00_freeze.py --zip "$(ZIP)" --out src_frozen --log logs/g0_inputs.md

probe:
	$(PY) scripts/s01_probe.py --src src_frozen --out logs/p0_probe.md

test:
	$(PY) scripts/selftest.py

status:
	$(PY) scripts/status.py

handover:
	$(PY) scripts/make_handover.py

verify-pack:
	$(PY) scripts/verify_pack.py

verify-anchors:
	$(PY) scripts/anchor_tool.py verify --ledger "ledger/溯源与处置台账.md" --books-dir src_frozen

pack:
	$(PY) scripts/pack.py

gates:
	$(PY) scripts/gates.py

validate-spec:
	$(PY) scripts/validate_pillars.py

split:
	$(PY) scripts/s01_split.py --src src_frozen

p0-gates:
	$(PY) scripts/p0_pipeline.py

p0: split p0-gates

p1-select:
	$(PY) scripts/p1_select.py --src src_frozen

p1-verify-anchors:
	$(PY) scripts/anchor_tool.py verify --ledger ledger/锚点表_试点.md --books-dir src_frozen

p1-blind2:
	$(PY) scripts/p1_blind2_anchors.py
	$(PY) scripts/anchor_tool.py verify --ledger ledger/锚点表_试点_blind2.md --books-dir src_frozen

p1-overlap:
	$(PY) scripts/s14_overlap.py --a ledger/锚点表_试点.md --b ledger/锚点表_试点_blind2.md

p1-kwscan:
	$(PY) scripts/s13_kwscan.py

p1-recall:
	$(PY) scripts/p1_highlight_recall.py

p1-stats:
	$(PY) scripts/p1_stats.py

p1-throughput:
	$(PY) scripts/p1_throughput.py

st-p1:
	$(PY) scripts/st_p1_pressure.py

drift: st-p1

p2-s09:
	$(PY) scripts/s09_make_cards.py

p2-s10:
	$(PY) scripts/s10_batcher.py

p2-triage:
	$(PY) scripts/p2_triage.py
	$(PY) scripts/p2_series_groups.py

p2-triage-verify:
	$(PY) scripts/p2_triage.py --verify-only

p2-x-readback:
	$(PY) scripts/p2_x_readback.py

p3a-plan:
	$(PY) scripts/p3a_plan_batches.py

p3a-verify-anchors:
	$(PY) scripts/anchor_tool.py verify --ledger ledger/锚点表_P3a.md --books-dir src_frozen
