"use client"

import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

type DropdownMenuContextValue = {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
}

const DropdownMenuContext = React.createContext<DropdownMenuContextValue | undefined>(undefined)

function useDropdownMenuContext(): DropdownMenuContextValue {
  const context = React.useContext(DropdownMenuContext)
  if (!context) {
    throw new Error("DropdownMenu components must be used within DropdownMenu")
  }
  return context
}

export function DropdownMenu({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false)
  const containerRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false)
      }
    }

    document.addEventListener("mousedown", handlePointerDown)
    document.addEventListener("keydown", handleEscape)
    return () => {
      document.removeEventListener("mousedown", handlePointerDown)
      document.removeEventListener("keydown", handleEscape)
    }
  }, [])

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div ref={containerRef} className="relative inline-flex">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  )
}

export function DropdownMenuTrigger({
  asChild = false,
  className,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean
}) {
  const { open, setOpen } = useDropdownMenuContext()
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      aria-expanded={open}
      aria-haspopup="menu"
      className={className}
      onClick={(event: React.MouseEvent<HTMLButtonElement>) => {
        props.onClick?.(event)
        if (!event.defaultPrevented) {
          setOpen((current) => !current)
        }
      }}
      {...props}
    >
      {children}
    </Comp>
  )
}

export function DropdownMenuContent({
  align = "end",
  className,
  children,
}: {
  align?: "start" | "end"
  className?: string
  children: React.ReactNode
}) {
  const { open } = useDropdownMenuContext()
  if (!open) {
    return null
  }

  return (
    <div
      role="menu"
      className={cn(
        "absolute top-full z-50 mt-2 min-w-40 rounded-md border bg-background p-1 shadow-md",
        align === "end" ? "right-0" : "left-0",
        className
      )}
    >
      {children}
    </div>
  )
}

export function DropdownMenuItem({
  className,
  onSelect,
  children,
}: {
  className?: string
  onSelect?: () => void
  children: React.ReactNode
}) {
  const { setOpen } = useDropdownMenuContext()

  return (
    <button
      type="button"
      role="menuitem"
      className={cn(
        "flex w-full items-center rounded-sm px-3 py-2 text-sm text-left transition-colors hover:bg-accent hover:text-accent-foreground",
        className
      )}
      onClick={() => {
        setOpen(false)
        onSelect?.()
      }}
    >
      {children}
    </button>
  )
}
