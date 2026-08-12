# Observed runtime auto-switch behaviour

During this session the chat's active model changed automatically as providers
were exhausted:

1. Started: `openrouter/deepseek/deepseek-v4-flash` → EXHAUSTED (paid, credits out).
2. Auto-switched to: `z-ai/glm-5.2` via NVIDIA NIM (free).
3. Later switched to: `tencent/hy3:free` via Nous Portal (free).

Each change came with a system message telling the user which provider/model was
now active. The task continued without user intervention.

## Lesson for the router
On a non-200 or quota error, the router should pick the next-best *validated free*
model of the same quality tier — NOT necessarily a different model of the same
provider, and NEVER a paid one. The user set the rule: exhausted free → ask,
do not silently escalate to a paid key.
