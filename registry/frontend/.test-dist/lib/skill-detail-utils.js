"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseInputs = parseInputs;
exports.parseOutputs = parseOutputs;
exports.parseChainSteps = parseChainSteps;
exports.parseBenchmarks = parseBenchmarks;
exports.formatPublishedDate = formatPublishedDate;
exports.executionBadgeClass = executionBadgeClass;
function readString(value, fallback = "") {
    return typeof value === "string" ? value : fallback;
}
function readBoolean(value, fallback = false) {
    return typeof value === "boolean" ? value : fallback;
}
function readNumber(value) {
    return typeof value === "number" ? value : undefined;
}
function parseInputs(rows) {
    return rows.map((row, index) => ({
        name: readString(row.name, `input_${index + 1}`),
        type: readString(row.type, "unknown"),
        required: readBoolean(row.required, false),
        description: readString(row.description, ""),
    }));
}
function parseOutputs(rows) {
    return rows.map((row, index) => ({
        name: readString(row.name, `output_${index + 1}`),
        type: readString(row.type, "unknown"),
        description: readString(row.description, ""),
    }));
}
function parseChainSteps(execution) {
    if (readString(execution.type) !== "chain") {
        return [];
    }
    const rawSteps = execution.steps;
    if (!Array.isArray(rawSteps)) {
        return [];
    }
    return rawSteps.map((step, index) => {
        const row = typeof step === "object" && step !== null ? step : {};
        const name = readString(row.name) ||
            readString(row.id) ||
            readString(row.skill) ||
            readString(row.uses) ||
            `Step ${index + 1}`;
        const description = readString(row.description, "");
        return { name, description };
    });
}
function parseBenchmarks(benchmarks) {
    if (!benchmarks || Object.keys(benchmarks).length === 0) {
        return [];
    }
    const candidateKeys = ["entries", "results", "models", "benchmarks"];
    for (const key of candidateKeys) {
        const value = benchmarks[key];
        if (Array.isArray(value)) {
            return value.map((item, index) => {
                const row = typeof item === "object" && item !== null ? item : {};
                return {
                    model: readString(row.model, readString(row.name, `Model ${index + 1}`)),
                    score: readNumber(row.score),
                    latency_ms: readNumber(row.latency_ms),
                    cost_per_call: readNumber(row.cost_per_call ?? row.avg_cost_per_call_usd),
                    last_evaluated: readString(row.last_evaluated, ""),
                };
            });
        }
    }
    return [
        {
            model: "Overall",
            score: readNumber(benchmarks.score),
            latency_ms: readNumber(benchmarks.avg_latency_ms),
            cost_per_call: readNumber(benchmarks.avg_cost_per_call_usd),
            last_evaluated: readString(benchmarks.last_evaluated, ""),
        },
    ];
}
function formatPublishedDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return "Unknown date";
    }
    return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}
function executionBadgeClass(execType) {
    if (execType === "prompt")
        return "bg-blue-100 text-blue-800 border-blue-200";
    if (execType === "tool_call")
        return "bg-purple-100 text-purple-800 border-purple-200";
    if (execType === "code")
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
    if (execType === "chain")
        return "bg-orange-100 text-orange-800 border-orange-200";
    return "bg-zinc-100 text-zinc-800 border-zinc-200";
}
