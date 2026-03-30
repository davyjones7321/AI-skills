import assert from "node:assert/strict"
import {
  getFilterDescription,
  getVisiblePageNumbers,
  parsePositiveInt,
  startEndText,
} from "../../lib/skills-page-utils"

assert.equal(parsePositiveInt("3", 1), 3)
assert.equal(parsePositiveInt("0", 1), 1)
assert.equal(parsePositiveInt("-1", 1), 1)
assert.equal(parsePositiveInt("2.5", 1), 1)
assert.equal(parsePositiveInt("abc", 1), 1)
assert.equal(parsePositiveInt(null, 1), 1)

assert.equal(startEndText(0, 1, 12), "Showing 0 of 0 skills")
assert.equal(startEndText(25, 1, 12), "Showing 1-12 of 25 skills")
assert.equal(startEndText(25, 3, 12), "Showing 25-25 of 25 skills")

assert.equal(
  getFilterDescription({ q: "sql", type: "code", tag: "database", category: "Utilities", sort: "most_downloaded" }),
  'search "sql", type code, tag database, category Utilities, sorted by most downloaded'
)
assert.equal(
  getFilterDescription({ q: "", type: "all", tag: "all", category: "all", sort: "newest" }),
  "sorted by newest"
)

assert.deepEqual(getVisiblePageNumbers(1, 1), [])
assert.deepEqual(getVisiblePageNumbers(1, 5), [1, 2, 3])
assert.deepEqual(getVisiblePageNumbers(3, 8), [1, 2, 3, 4, 5])
assert.deepEqual(getVisiblePageNumbers(8, 8), [6, 7, 8])

console.log("skills-page-utils tests passed")
