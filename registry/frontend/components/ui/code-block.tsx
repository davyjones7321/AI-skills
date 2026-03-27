"use client"

import { useState } from "react"
import { Check, Copy } from "lucide-react"
import { Button } from "@/components/ui/button"

type CodeBlockProps = {
  code: string
  language?: string
}

export function CodeBlock({ code, language }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const copyCode = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="relative rounded-lg border bg-muted/50">
      {language ? (
        <span className="absolute left-3 top-2 text-[10px] uppercase tracking-wide text-muted-foreground">
          {language}
        </span>
      ) : null}
      <Button
        type="button"
        size="sm"
        variant="ghost"
        className="absolute right-2 top-1 h-7 px-2 text-xs"
        onClick={copyCode}
      >
        {copied ? <Check className="mr-1 h-3.5 w-3.5" /> : <Copy className="mr-1 h-3.5 w-3.5" />}
        {copied ? "Copied" : "Copy"}
      </Button>
      <pre className="overflow-x-auto px-4 pb-4 pt-9 font-mono text-xs leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  )
}
