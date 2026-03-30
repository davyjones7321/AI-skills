import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Download, Zap, Box, Code, Link2 } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SkillBenchmarks } from "@/lib/types"

export interface SkillCardProps {
    id: string
    author: string
    name: string
    description: string
    exec_type: string
    category?: string | null
    downloads?: number
    reviewed?: boolean
    tags?: string[]
    benchmarks?: SkillBenchmarks | null
}

const typeIcons = {
    prompt: Zap,
    tool_call: Link2,
    chain: Box,
    code: Code,
}

function executionBadgeClass(execType: string): string {
    if (execType === "prompt") return "bg-blue-100 text-blue-800 border-blue-200"
    if (execType === "tool_call") return "bg-purple-100 text-purple-800 border-purple-200"
    if (execType === "code") return "bg-emerald-100 text-emerald-800 border-emerald-200"
    if (execType === "chain") return "bg-orange-100 text-orange-800 border-orange-200"
    return "bg-zinc-100 text-zinc-800 border-zinc-200"
}

export function SkillCard({
    id,
    author,
    name,
    description,
    exec_type,
    category,
    downloads,
    reviewed,
    tags = [],
}: SkillCardProps) {
    const Icon = typeIcons[exec_type as keyof typeof typeIcons] || Zap
    const visibleTags = tags.slice(0, 3)
    const hiddenTagCount = Math.max(tags.length - visibleTags.length, 0)

    return (
        <Link href={`/skills/${author}/${id}`}>
            <Card className="h-full transition-all hover:border-zinc-400 dark:hover:border-zinc-500 cursor-pointer">
                <CardHeader>
                    <div className="flex items-start justify-between">
                        <div className="space-y-1">
                            <CardTitle className="text-xl font-bold tracking-tight">{name}</CardTitle>
                            <CardDescription className="font-mono text-xs text-zinc-500">
                                {author}/{id}
                            </CardDescription>
                        </div>
                        <div className={cn(
                            "flex items-center justify-center h-8 w-8 rounded-full bg-zinc-100 dark:bg-zinc-800",
                            "text-zinc-500"
                        )}>
                            <Icon className="h-4 w-4" />
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-2">
                        {description}
                    </p>
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                        {category ? (
                            <Badge variant="secondary" className="text-[10px]">
                                {category}
                            </Badge>
                        ) : null}
                        {visibleTags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-[10px]">
                                #{tag}
                            </Badge>
                        ))}
                        {hiddenTagCount > 0 ? (
                            <Badge variant="outline" className="text-[10px]">
                                +{hiddenTagCount} more
                            </Badge>
                        ) : null}
                    </div>
                </CardContent>
                <CardFooter className="flex items-center justify-between border-t bg-zinc-50/50 dark:bg-zinc-900/50 px-6 py-3">
                    <div className="flex items-center gap-2">
                        <Badge variant="outline" className={cn("font-normal text-xs uppercase tracking-wider", executionBadgeClass(exec_type))}>
                            {exec_type}
                        </Badge>
                        {reviewed ? <Badge variant="secondary" className="text-[10px]">Reviewed</Badge> : null}
                    </div>
                    {typeof downloads === "number" ? (
                        <div className="flex items-center gap-1 text-xs text-zinc-500">
                            <Download className="h-3 w-3" />
                            <span>{downloads.toLocaleString()}</span>
                        </div>
                    ) : (
                        <span />
                    )}
                </CardFooter>
            </Card>
        </Link>
    )
}
