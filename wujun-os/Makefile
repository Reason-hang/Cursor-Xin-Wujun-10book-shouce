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

# P3a 加速：探针草稿 → 编辑 manifest claim → commit → lint → 既有 test/pack
p3a-probes:
	@test -n "$(BATCH)" || (echo "用法: make p3a-probes BATCH=B-P3a-GJ-003"; exit 1)
	$(PY) scripts/p3a_batch.py probes --batch $(BATCH) -o drafts/$(BATCH)_probes.json

p3a-commit:
	@test -n "$(MANIFEST)" || (echo "用法: make p3a-commit MANIFEST=drafts/B-P3a-xxx.json"; exit 1)
	$(PY) scripts/p3a_batch.py commit --manifest $(MANIFEST)

p3a-lint:
	@if [ -n "$(BATCH)" ]; then $(PY) scripts/p3a_batch.py lint --batch $(BATCH); else $(PY) scripts/p3a_batch.py lint; fi

p3a-close:
	@test -n "$(BATCH)" || (echo "用法: make p3a-close BATCH=B-P3a-xxx [MANIFEST=drafts/....json]"; exit 1)
	@if [ -n "$(MANIFEST)" ]; then $(MAKE) p3a-commit MANIFEST=$(MANIFEST); fi
	$(MAKE) p3a-lint BATCH=$(BATCH)
	$(MAKE) p3a-verify-anchors
	$(MAKE) pack
	$(MAKE) test

p3b-plan:
	$(PY) scripts/p3b_plan_batches.py

p3b-plan-sg1:
	$(PY) scripts/p3b_plan_sg1_batches.py

p3b-verify-anchors:
	$(PY) scripts/anchor_tool.py verify --ledger ledger/锚点表_P3b.md --books-dir src_frozen

p3b-probes:
	@test -n "$(BATCH)" || (echo "用法: make p3b-probes BATCH=B-P3b-GG-001"; exit 1)
	$(PY) scripts/p3b_batch.py probes --batch $(BATCH) -o drafts/$(BATCH)_probes.json

p3b-commit:
	@test -n "$(MANIFEST)" || (echo "用法: make p3b-commit MANIFEST=drafts/B-P3b-xxx.json"; exit 1)
	$(PY) scripts/p3b_batch.py commit --manifest $(MANIFEST)

p3b-lint:
	@test -n "$(BATCH)" || (echo "用法: make p3b-lint BATCH=B-P3b-GG-001"; exit 1)
	$(PY) scripts/p3b_batch.py lint --batch $(BATCH)

p3b-close:
	@test -n "$(BATCH)" || (echo "用法: make p3b-close BATCH=B-P3b-xxx"; exit 1)
	@if [ -n "$(MANIFEST)" ]; then $(MAKE) p3b-commit MANIFEST=$(MANIFEST); fi
	$(MAKE) p3b-lint BATCH=$(BATCH)
	$(MAKE) p3b-verify-anchors
	$(MAKE) pack
	$(MAKE) test

p3c-apply:
	$(PY) scripts/p3c_apply_triage.py

p3-meta-shell:
	$(PY) scripts/p3_meta_shell.py

p3-gap-plan:
	$(PY) scripts/p3_gap_plan.py

p3b-gap-plan:
	$(PY) scripts/p3b_gap_plan.py

p3-disposition-audit:
	$(PY) scripts/p3_disposition_audit.py
	$(PY) scripts/status.py

p4-freeze-p3:
	$(PY) scripts/p4_freeze_p3.py

p4-concept-keys:
	$(PY) scripts/p4_build_concept_keys.py
	$(PY) scripts/p4_lint_concept_keys.py

p4-lint-concept-keys:
	$(PY) scripts/p4_lint_concept_keys.py

p4-similar-pairs:
	$(PY) scripts/p4_similar_pairs.py

p4-annotate-relations:
	$(PY) scripts/p4_annotate_relations.py
	$(PY) scripts/p4_lint_relations.py

p4-assign-pillars:
	$(PY) scripts/p4_assign_pillars.py
	$(PY) scripts/p4_lint_pillars.py

p4-aggregate-l3:
	$(PY) scripts/p4_aggregate_l3.py
	$(PY) scripts/p4_lint_l3.py

p4-finalize-l2:
	$(PY) scripts/p4_finalize_l2.py
	$(PY) scripts/p4_lint_l2_final.py

p4-d10-gates:
	$(PY) scripts/p4_d10_three_gates.py
	$(PY) scripts/p4_lint_d10_gates.py

p4-count-audit:
	$(PY) scripts/p4_count_audit.py
	$(PY) scripts/p4_lint_count.py

p4-blind-kappa:
	$(PY) scripts/s16_kappa.py
	$(PY) scripts/p4_lint_blind_kappa.py

p4-apply-blind-manual:
	$(PY) scripts/p4_apply_blind_manual.py
	$(PY) scripts/s16_kappa.py

p4-spot-check-20:
	$(PY) scripts/p4_spot_check_20.py

p4-prefill-spot-check:
	$(PY) scripts/p4_prefill_spot_check.py

p4-freeze-k:
	$(PY) scripts/p4_prefill_spot_check.py
	$(PY) scripts/p4_freeze_k.py
	$(PY) scripts/p4_lint_freeze_k.py

p4-dict-change-report:
	$(PY) scripts/p4_dict_change_report.py

p5-export-chapter:
	@test -n "$(CH)" || (echo "用法: make p5-export-chapter CH=D06"; exit 1)
	$(PY) scripts/p5_export_chapter.py $(CH)

p5-assemble:
	$(PY) scripts/p5_assemble.py

p5-lint-scenes:
	$(PY) scripts/p5_lint_scenes.py

p6-preflight:
	$(PY) scripts/p6_preflight.py

p6-build-d3:
	$(PY) scripts/p6_build_d3.py

p6-report:
	$(PY) scripts/p6_report.py

p6-build-d6:
	$(PY) scripts/p6_build_d6.py

p6-dup-lint:
	$(PY) scripts/p6_dup_lint.py

p6-unit-coverage:
	$(PY) scripts/p6_unit_coverage.py

p6-must-check-rollup:
	$(PY) scripts/p6_must_check_rollup.py

p6-k-by-book:
	$(PY) scripts/p6_k_coverage_by_book.py

p6-g10-status:
	$(PY) scripts/p6_g10_kw_status.py

p6-g10-refresh:
	$(MAKE) p1-kwscan
	$(PY) scripts/p6_g10_kw_status.py

p6-anchor-suggest:
	$(PY) scripts/p6_anchor_reprobe_suggest.py

p6-bidir-matrix:
	$(PY) scripts/p6_bidir_matrix.py

p6-recall-sample:
	$(PY) scripts/p6_recall_sample.py

p6-recall-assist:
	$(PY) scripts/p6_recall_assist.py

p6-recall-lint:
	$(PY) scripts/p6_recall_lint.py

p6-recall-ingest:
	$(PY) scripts/p6_recall_ingest.py
	$(MAKE) p6-recall-assist

p6-recall-batch-init:
	$(PY) scripts/p6_recall_batch_init.py

p6-math-audit:
	$(PY) scripts/p6_math_mapping_audit.py

p6-app-lint:
	$(PY) scripts/p6_app_scenarios_lint.py

p6-ac6-dashboard:
	$(PY) scripts/p6_ac6_dashboard.py

p6-s15-g-audit:
	$(PY) scripts/p6_s15_g_audit.py
	$(PY) scripts/p6_sg3_highlight_status.py

p6-sg3-highlight-recall:
	$(PY) scripts/p6_sg3_highlight_recall.py

p6-build: p6-build-d3 p6-s15-g-audit p6-ac6-dashboard p6-report p6-build-d6 p6-dup-lint p6-unit-coverage p6-must-check-rollup p6-k-by-book p6-g10-status p6-anchor-suggest p6-bidir-matrix p6-recall-sample p6-recall-assist p6-math-audit p6-app-lint p6-anchor-queue-preview p5-assemble deliver-audit

p7-s18-check:
	$(PY) scripts/s18_render_check.py

deliver-audit:
	$(PY) scripts/deliverables_audit.py

p7-preflight:
	$(MAKE) deliver-audit
	$(MAKE) p7-s18-check
	$(MAKE) p7-human-signoff
	$(MAKE) deliver-audit

p7-human-signoff:
	$(PY) scripts/p7_human_signoff_lint.py

p6-human-review-status:
	$(PY) scripts/p6_human_review_status.py

p6-human-review-ingest:
	$(PY) scripts/p6_human_review_ingest.py

p6-human-review-apply:
	$(PY) scripts/p6_human_review_apply.py
	$(MAKE) p6-ac6-dashboard
	$(MAKE) p6-report

p6-human-review-full:
	$(MAKE) p6-human-review-ingest
	$(MAKE) p6-human-review-apply
	$(MAKE) p7-ready-lint

p6-anchor-queue-preview:
	$(PY) scripts/p6_anchor_queue_apply.py

p6-anchor-queue-apply:
	$(PY) scripts/p6_anchor_queue_apply.py --apply

d10-apply:
	$(PY) scripts/d10_apply_decision.py

p4-spot-confirm:
	$(PY) scripts/p4_spot_check_confirm.py

g10-opt-apply:
	$(PY) scripts/g10_opt_apply.py

sg1-opt-apply:
	$(PY) scripts/sg1_opt_apply.py

approvals-ingest:
	$(PY) scripts/approvals_ingest.py

approvals-apply:
	$(MAKE) d10-apply
	$(MAKE) g10-opt-apply
	$(MAKE) sg1-opt-apply
	$(MAKE) p4-spot-confirm
	$(PY) scripts/p6_build_d6.py

approvals-full:
	$(MAKE) approvals-ingest
	$(MAKE) approvals-apply
	$(MAKE) p6-build
	$(MAKE) p7-preflight
	$(MAKE) pack

p7-ready-lint:
	$(PY) scripts/p7_ready_lint.py

p7-acceptance-audit:
	$(PY) scripts/p7_stage_acceptance_audit.py

p7-closeout:
	$(PY) scripts/p7_closeout.py

p5-lint:
	$(PY) scripts/s17_manual_lint.py
