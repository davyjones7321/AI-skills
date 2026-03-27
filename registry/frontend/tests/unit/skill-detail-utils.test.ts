import assert from "node:assert/strict"
import {
  executionBadgeClass,
  formatPublishedDate,
  parseBenchmarks,
  parseChainSteps,
  parseInputs,
  parseOutputs,
} from "../../lib/skill-detail-utils"

const inputs = parseInputs([{ required: true }, { name: "query", type: "string", description: "User query" }])
assert.deepEqual(inputs, [
  { name: "input_1", type: "unknown", required: true, description: "" },
  { name: "query", type: "string", required: false, description: "User query" },
])

const outputs = parseOutputs([{}, { name: "summary", type: "string" }])
assert.deepEqual(outputs, [
  { name: "output_1", type: "unknown", description: "" },
  { name: "summary", type: "string", description: "" },
])

assert.deepEqual(parseChainSteps({ type: "prompt", steps: [{ id: "noop" }] }), [])

const chainSteps = parseChainSteps({
  type: "chain",
  steps: [{ id: "fetch" }, { skill: "summarize" }, {}, "invalid"],
})
assert.deepEqual(chainSteps, [
  { name: "fetch", description: "" },
  { name: "summarize", description: "" },
  { name: "Step 3", description: "" },
  { name: "Step 4", description: "" },
])

const entries = parseBenchmarks({
  entries: [
    { model: "gpt-4.1", score: 92, latency_ms: 110, avg_cost_per_call_usd: 0.004 },
    { name: "fallback-name" },
  ],
})
assert.deepEqual(entries, [
  { model: "gpt-4.1", score: 92, latency_ms: 110, cost_per_call: 0.004, last_evaluated: "" },
  { model: "fallback-name", score: undefined, latency_ms: undefined, cost_per_call: undefined, last_evaluated: "" },
])

const summary = parseBenchmarks({
  score: 88,
  avg_latency_ms: 95,
  avg_cost_per_call_usd: 0.002,
  last_evaluated: "2026-03-20",
})
assert.deepEqual(summary, [
  { model: "Overall", score: 88, latency_ms: 95, cost_per_call: 0.002, last_evaluated: "2026-03-20" },
])

assert.equal(formatPublishedDate("not-a-date"), "Unknown date")
assert.equal(executionBadgeClass("prompt"), "bg-blue-100 text-blue-800 border-blue-200")
assert.equal(executionBadgeClass("tool_call"), "bg-purple-100 text-purple-800 border-purple-200")
assert.equal(executionBadgeClass("code"), "bg-emerald-100 text-emerald-800 border-emerald-200")
assert.equal(executionBadgeClass("chain"), "bg-orange-100 text-orange-800 border-orange-200")
assert.equal(executionBadgeClass("custom"), "bg-zinc-100 text-zinc-800 border-zinc-200")

console.log("skill-detail-utils tests passed")
