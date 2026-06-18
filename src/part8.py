"""Part 8 - Advanced topics (lessons 28-31).

Lesson 28 opens Part 8: multi-agent and sleeptime. In letta v0.16.8 only two
multi-agent mechanisms are actually live:

    send_message_to_agent_* tools (agent A re-enters the server over REST and
        runs agent B's own loop) -> direct agent-to-agent calls
    sleeptime (a foreground agent finishes, then a background sleeptime agent is
        woken every N turns to rewrite memory) -> a shared Block row is the only
        coordination primitive

The classic group managers (round_robin / supervisor / dynamic) survive only as
schema / enum / class skeletons; their executor load_multi_agent is never called.
Each lesson dict mirrors the house style of Parts 1-7 (cards / notes / cute /
codefile / vflow / cols / cellgroup / table.t), with cross-refs back to earlier
lessons. zh is authored first; en starts as a stub for the next agent.
"""

LESSON_28 = {
    "zh": r"""
<!--ZHMORE-->
""",
    "en": r"""<p>stub</p>""",
}
