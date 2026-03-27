"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const strict_1 = __importDefault(require("node:assert/strict"));
const skill_detail_utils_1 = require("../../lib/skill-detail-utils");
const inputs = (0, skill_detail_utils_1.parseInputs)([{ required: true }, { name: "query", type: "string", description: "User query" }]);
strict_1.default.deepEqual(inputs, [
    { name: "input_1", type: "unknown", required: true, description: "" },
    { name: "query", type: "string", required: false, description: "User query" },
]);
const outputs = (0, skill_detail_utils_1.parseOutputs)([{}, { name: "summary", type: "string" }]);
strict_1.default.deepEqual(outputs, [
    { name: "output_1", type: "unknown", description: "" },
    { name: "summary", type: "string", description: "" },
]);
strict_1.default.deepEqual((0, skill_detail_utils_1.parseChainSteps)({ type: "prompt", steps: [{ id: "noop" }] }), []);
const chainSteps = (0, skill_detail_utils_1.parseChainSteps)({
    type: "chain",
    steps: [{ id: "fetch" }, { skill: "summarize" }, {}, "invalid"],
});
strict_1.default.deepEqual(chainSteps, [
    { name: "fetch", description: "" },
    { name: "summarize", description: "" },
    { name: "Step 3", description: "" },
    { name: "Step 4", description: "" },
]);
const entries = (0, skill_detail_utils_1.parseBenchmarks)({
    entries: [
        { model: "gpt-4.1", score: 92, latency_ms: 110, avg_cost_per_call_usd: 0.004 },
        { name: "fallback-name" },
    ],
});
strict_1.default.deepEqual(entries, [
    { model: "gpt-4.1", score: 92, latency_ms: 110, cost_per_call: 0.004, last_evaluated: "" },
    { model: "fallback-name", score: undefined, latency_ms: undefined, cost_per_call: undefined, last_evaluated: "" },
]);
const summary = (0, skill_detail_utils_1.parseBenchmarks)({
    score: 88,
    avg_latency_ms: 95,
    avg_cost_per_call_usd: 0.002,
    last_evaluated: "2026-03-20",
});
strict_1.default.deepEqual(summary, [
    { model: "Overall", score: 88, latency_ms: 95, cost_per_call: 0.002, last_evaluated: "2026-03-20" },
]);
strict_1.default.equal((0, skill_detail_utils_1.formatPublishedDate)("not-a-date"), "Unknown date");
strict_1.default.equal((0, skill_detail_utils_1.executionBadgeClass)("prompt"), "bg-blue-100 text-blue-800 border-blue-200");
strict_1.default.equal((0, skill_detail_utils_1.executionBadgeClass)("tool_call"), "bg-purple-100 text-purple-800 border-purple-200");
strict_1.default.equal((0, skill_detail_utils_1.executionBadgeClass)("code"), "bg-emerald-100 text-emerald-800 border-emerald-200");
strict_1.default.equal((0, skill_detail_utils_1.executionBadgeClass)("chain"), "bg-orange-100 text-orange-800 border-orange-200");
strict_1.default.equal((0, skill_detail_utils_1.executionBadgeClass)("custom"), "bg-zinc-100 text-zinc-800 border-zinc-200");
console.log("skill-detail-utils tests passed");
