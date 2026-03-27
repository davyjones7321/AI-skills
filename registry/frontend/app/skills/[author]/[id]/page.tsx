import { SkillDetailView, SkillNotFoundState } from "@/components/registry/skill-detail-view"
import { getSkill } from "@/lib/api"
import type { SkillDetail } from "@/lib/types"

export default async function SkillPage({
    params,
}: {
    params: Promise<{ author: string; id: string }>
}) {
    const { author, id } = await params
    let skill: SkillDetail | null = null

    try {
        skill = await getSkill(author, id)
    } catch (error) {
        console.error("getSkill failed:", error)
        return <SkillNotFoundState />
    }

    if (!skill) {
        return <SkillNotFoundState />
    }

    return <SkillDetailView skill={skill} />
}
