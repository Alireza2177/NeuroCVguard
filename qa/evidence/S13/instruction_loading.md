# S13 loaded instructions and scope

Opened AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json,
prompts/S13_synthetic_demo.md (via S13*), spec chapters 01, 13, 14, 15 and 20,
all seven S13 acceptance cases, the full rule catalog, templates/HANDOFF.md and
state/handoffs/S12.md. The actual S13 prompt basename is recorded by the command
evidence/file inventory. No human-accepted handoff exists. The user explicitly
requested S13 after completed S12 and 588 passing tests; continuation does not
change human acceptance flags. Git was clean at e8eef64 (merged S12).

Planned files: synthetic.py, demo.py, CLI integration, a fixed synthetic report
label through an exact fixed limitation, five examples, generator/demo/example tests,
synthetic guide and README/CLI/assistance updates. No contract/schema change is
planned. Work order: A generators and invariant tests; B tutorials/demo and
integration checks; C execute all examples, record real reports/configs/versions,
capture a genuine rendered screenshot, then full regressions/static checks and
handoff. Baseline captures 751 preexisting files. Stop before S14.

Read the computer-use SKILL.md while assessing screenshot capabilities; no native
Windows automation skill was applied. The browser tool's local-file request was
blocked by its security policy, and no alternate surface or workaround was used.
The outstanding screenshot is recorded separately; it is not a claimed success.

The initial implementation attempted a synthetic_demo provenance field, which the
existing closed schema correctly rejected. The implementation was corrected to
preserve only an exact fixed synthetic notice in the existing limitations array.
No normative conflict or schema extension is needed for that compatible approach.
