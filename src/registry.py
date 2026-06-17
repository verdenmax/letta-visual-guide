"""Single source of truth: ordered map of output filename -> bilingual content.

Each value is a dict ``{"zh": html, "en": html}``. build.py / check_html.py import
this so the lesson set stays in sync with shell.PAGES.
"""
import part1
import part2
import part3
import part4
import part5

# Filename -> {"zh": ..., "en": ...}. Keep keys in sync with shell.PAGES.
CONTENT = {
    "01-what-is-letta.html": part1.LESSON_01,
    "02-project-map.html": part1.LESSON_02,
    "03-message-lifecycle.html": part1.LESSON_03,
    "04-agent-and-tools.html": part2.LESSON_04,
    "05-context-window.html": part2.LESSON_05,
    "06-stateful-vs-stateless.html": part2.LESSON_06,
    "07-memory-tiers.html": part3.LESSON_07,
    "08-memory-blocks.html": part3.LESSON_08,
    "09-self-editing-memory.html": part3.LESSON_09,
    "10-archival-memory.html": part3.LESSON_10,
    "11-recall-memory.html": part3.LESSON_11,
    "12-context-compaction.html": part3.LESSON_12,
    "13-agent-state-and-loop.html": part4.LESSON_13,
    "14-v3-step-loop.html": part4.LESSON_14,
    "15-heartbeat-to-no-heartbeat.html": part4.LESSON_15,
    "16-tool-rules.html": part4.LESSON_16,
    "17-tool-as-function.html": part5.LESSON_17,
    "18-schema-without-executing.html": part5.LESSON_18,
}
