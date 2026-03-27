const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://ai-skills-production-f4f0.up.railway.app";

async function check(name, path, validate) {
  const url = new URL(path, API_BASE_URL).toString();
  const response = await fetch(url);
  const text = await response.text();

  let payload = null;
  try {
    payload = JSON.parse(text);
  } catch {
    payload = text;
  }

  const result = {
    name,
    path,
    ok: false,
    details: "",
  };

  try {
    validate(response, payload);
    result.ok = true;
    result.details = `status ${response.status}`;
  } catch (error) {
    result.details = `status ${response.status}: ${error instanceof Error ? error.message : String(error)}`;
  }

  return result;
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const checks = [
  check("health", "/health", (_response, body) => {
    assert(body?.status === "ok", "expected status=ok");
  }),
  check("skills list", "/skills/?page=1&limit=5", (_response, body) => {
    assert(Array.isArray(body?.skills), "expected skills array");
    assert(body.skills.length > 0, "expected at least one skill");
    assert(typeof body?.total_count === "number", "expected total_count");
  }),
  check("search", "/skills/search?q=sentiment", (_response, body) => {
    assert(Array.isArray(body?.skills), "expected skills array");
    assert(body.skills.some((skill) => skill.id === "classify-sentiment"), "expected sentiment skill");
  }),
  check("detail", "/skills/ai-skills-team/summarize-document", (_response, body) => {
    assert(body?.id === "summarize-document", "expected summarize-document detail");
    assert(Array.isArray(body?.compatible_with), "expected compatible_with array");
  }),
  check("invalid filter handling", "/skills/search?type=invalid", (response, body) => {
    assert(response.status === 400, "expected HTTP 400");
    assert(typeof body?.detail === "string" && body.detail.includes("Invalid type"), "expected validation message");
  }),
  check("tags", "/skills/tags", (response, body) => {
    assert(response.status === 200, "expected HTTP 200");
    assert(Array.isArray(body?.tags), "expected tags array");
    assert(body.tags.length > 0, "expected at least one tag");
  }),
];

const results = await Promise.all(checks);
const failures = results.filter((result) => !result.ok);

for (const result of results) {
  const prefix = result.ok ? "PASS" : "FAIL";
  console.log(`${prefix} ${result.name}: ${result.details}`);
}

if (failures.length > 0) {
  process.exitCode = 1;
}
