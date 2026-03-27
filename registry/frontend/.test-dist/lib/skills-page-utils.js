"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SORT_OPTIONS = exports.EXEC_TYPES = exports.PAGE_SIZE = void 0;
exports.parsePositiveInt = parsePositiveInt;
exports.startEndText = startEndText;
exports.getFilterDescription = getFilterDescription;
exports.getVisiblePageNumbers = getVisiblePageNumbers;
exports.PAGE_SIZE = 12;
exports.EXEC_TYPES = ["all", "prompt", "tool_call", "code", "chain"];
exports.SORT_OPTIONS = ["newest", "most_downloaded", "lowest_latency"];
function parsePositiveInt(value, fallback) {
    if (!value)
        return fallback;
    const parsed = Number(value);
    return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}
function startEndText(totalCount, page, limit) {
    if (totalCount === 0)
        return "Showing 0 of 0 skills";
    const start = (page - 1) * limit + 1;
    const end = Math.min(page * limit, totalCount);
    return `Showing ${start}-${end} of ${totalCount} skills`;
}
function getFilterDescription({ q, type, tag, sort, }) {
    const parts = [];
    if (q)
        parts.push(`search "${q}"`);
    if (type !== "all")
        parts.push(`type ${type}`);
    if (tag !== "all")
        parts.push(`tag ${tag}`);
    parts.push(`sorted by ${sort.replace(/_/g, " ")}`);
    return parts.join(", ");
}
function getVisiblePageNumbers(page, totalPages) {
    if (totalPages <= 1)
        return [];
    const start = Math.max(1, page - 2);
    const end = Math.min(totalPages, page + 2);
    const nums = [];
    for (let i = start; i <= end; i += 1)
        nums.push(i);
    return nums;
}
