import assert from "node:assert/strict"
import {
  buildSkillYaml,
  createInitialBuildSkillFormState,
  getUploadPreview,
  isKebabCase,
  isSemver,
  splitTags,
  validateBuildSkillForm,
} from "../../lib/publish-utils"

const baseForm = createInitialBuildSkillFormState()

assert.equal(isKebabCase("my-skill-name"), true)
assert.equal(isKebabCase("MySkill"), false)
assert.equal(isSemver("1.0.0"), true)
assert.equal(isSemver("1.0"), false)
assert.deepEqual(splitTags("nlp, summarization, utility"), ["nlp", "summarization", "utility"])

const invalidErrors = validateBuildSkillForm(baseForm)
assert.equal(invalidErrors.id, "Use kebab-case, like my-skill-name.")
assert.equal(invalidErrors.version, undefined)
assert.equal(invalidErrors.name, "Name is required.")
assert.equal(invalidErrors.description, "Description is required.")
assert.equal(invalidErrors.category, "Choose a category.")
assert.equal(invalidErrors.promptTemplate, "Prompt skills need a prompt template.")

const validForm = {
  ...baseForm,
  id: "my-skill-name",
  name: "My Skill",
  description: "Summarizes input text.",
  category: "Content & Writing" as const,
  tags: "summarization, nlp",
  promptTemplate: "Summarize {input_text}",
  inputs: [{ name: "input_text", type: "string", required: true }],
  outputs: [{ name: "summary", type: "string" }],
}

assert.deepEqual(validateBuildSkillForm(validForm), {})

const yaml = buildSkillYaml(validForm, "octocat")
assert.match(yaml, /author: "octocat"/)
assert.match(yaml, /category: "Content & Writing"/)
assert.match(yaml, /prompt_template: "Summarize \{input_text\}"/)

const preview = getUploadPreview(`skill:
  id: sample-skill
  version: 1.2.3
  name: "Sample Skill"
  execution:
    type: prompt
`)

assert.deepEqual(preview, {
  id: "sample-skill",
  version: "1.2.3",
  name: "Sample Skill",
  execType: "prompt",
})

console.log("publish-utils tests passed")
