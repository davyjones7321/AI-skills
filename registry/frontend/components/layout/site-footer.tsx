import Link from "next/link"
import { ExternalLink } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

type FooterLink = {
  href: string
  label: string
  external?: boolean
}

function FooterColumn({ title, links }: { title: string; links: FooterLink[] }) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{title}</h3>
      <ul className="space-y-2 text-sm text-zinc-600 dark:text-zinc-400">
        {links.map((link) => (
          <li key={link.label}>
            {link.external ? (
              <a href={link.href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 hover:text-zinc-900 dark:hover:text-zinc-100">
                {link.label}
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            ) : (
              <Link href={link.href} className="hover:text-zinc-900 dark:hover:text-zinc-100">
                {link.label}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

const productLinks: FooterLink[] = [
  { href: "/skills", label: "Browse Skills" },
  { href: "/publish", label: "Publish a Skill" },
  { href: "/#how-it-works", label: "How It Works" },
]

const resourceLinks: FooterLink[] = [
  { href: "https://github.com/davyjones7321/AI-skills/blob/main/docs/SPEC.md", label: "Specification", external: true },
  { href: "https://github.com/davyjones7321/AI-skills/blob/main/docs/SECURITY.md", label: "Security Model", external: true },
  { href: "https://github.com/davyjones7321/AI-skills/blob/main/docs/COMPARISON.md", label: "Comparison Guide", external: true },
  { href: "https://github.com/davyjones7321/AI-skills/blob/main/CONTRIBUTING.md", label: "Contributing", external: true },
]

const communityLinks: FooterLink[] = [
  { href: "https://github.com/davyjones7321/AI-skills", label: "GitHub", external: true },
  { href: "https://github.com/davyjones7321/AI-skills/blob/main/CODE_OF_CONDUCT.md", label: "Code of Conduct", external: true },
  { href: "https://github.com/davyjones7321/AI-skills/issues", label: "Report an Issue", external: true },
]

export function SiteFooter() {
  return (
    <footer className="border-t bg-zinc-50/60 dark:bg-zinc-900/20">
      <div className="container mx-auto px-4 py-10 md:px-6">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <FooterColumn title="Product" links={productLinks} />
          <FooterColumn title="Resources" links={resourceLinks} />
          <FooterColumn title="Community" links={communityLinks} />
        </div>
        <Separator className="my-6" />
        <div className="flex flex-col items-start justify-between gap-3 text-sm text-zinc-600 dark:text-zinc-400 sm:flex-row sm:items-center">
          <p>© 2026 ai-skills. MIT License.</p>
          <Badge variant="outline">spec v0.1</Badge>
        </div>
      </div>
    </footer>
  )
}
