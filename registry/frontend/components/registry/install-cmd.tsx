"use client"

import * as React from "react"
import { Check, Copy, Terminal } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export function InstallCmd({ cmd }: { cmd: string }) {
  const [hasCopied, setHasCopied] = React.useState(false)

  React.useEffect(() => {
    setTimeout(() => {
      setHasCopied(false)
    }, 2000)
  }, [hasCopied])

  const copyToClipboard = () => {
    navigator.clipboard.writeText(cmd)
    setHasCopied(true)
  }

  return (
    <Card className="relative flex items-center justify-between bg-zinc-950 py-3 pl-4 pr-2 text-zinc-50 font-mono text-sm border-zinc-800">
      <div className="flex items-center gap-2 overflow-x-auto">
        <Terminal className="h-4 w-4 text-zinc-500" />
        <span className="whitespace-nowrap">{cmd}</span>
      </div>
      <Button
        size="icon"
        variant="ghost"
        className="h-8 w-8 text-zinc-500 hover:text-zinc-50 hover:bg-zinc-800"
        onClick={copyToClipboard}
      >
        {hasCopied ? (
          <Check className="h-4 w-4" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
        <span className="sr-only">Copy</span>
      </Button>
    </Card>
  )
}
