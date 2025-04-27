import type { AnalysisResult } from "./types"

export async function analyzeCode(code: string): Promise<AnalysisResult> {
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || "Failed to analyze code")
    }

    const result = await response.json()
    return result
  } catch (error) {
    console.error("Error analyzing code:", error)
    throw error
  }
}
