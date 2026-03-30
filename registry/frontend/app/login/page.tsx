import Link from "next/link"
import { Github } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const params = await searchParams
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  const oauthUrl = new URL("/auth/github", apiBaseUrl)

  if (params?.next) {
    oauthUrl.searchParams.set("next", params.next)
  }

  return (
    <main className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-3 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border bg-zinc-50">
            <Github className="h-7 w-7" />
          </div>
          <CardTitle className="text-2xl">Sign in to ai-skills</CardTitle>
          <CardDescription>Use GitHub to publish and manage your skills.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button asChild className="w-full">
            <a href={oauthUrl.toString()}>
              <Github className="h-4 w-4" />
              Sign in with GitHub
            </a>
          </Button>
          <p className="text-center text-sm text-zinc-600 dark:text-zinc-300">
            We only request read access to your public profile.
          </p>
          <p className="text-center text-sm text-zinc-500">
            Need to go back? <Link href="/" className="underline underline-offset-4">Return home</Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
