"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import CodeEditor from "@/components/code-editor"
import VariablesTable from "@/components/variables-table"
import ErrorsList from "@/components/errors-list"
import IfOptimizations from "@/components/if-optimizations"
import StatsSummary from "@/components/stats-summary"
import TypeDistribution from "@/components/type-distribution"
import { analyzeCode } from "@/lib/analyze-code"
import type { AnalysisResult } from "@/lib/types"
import { Loader2 } from "lucide-react"

export default function Home() {
  const [code, setCode] = useState<string>(`list[int] nums = [1,2,3,4]
for n in nums:
  n = ((n*4)/2)^2
  do:
    n = n + x
  while (n % 2)
  
int x = 1
int a = 2

if x:
  read()
  print("1234")
elif a:
  if b:
    x = 2`)

  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    try {
      const analysisResult = await analyzeCode(code)
      setResult(analysisResult)
    } catch (error) {
      console.error("Error analyzing code:", error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-4xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
          Code Analyzer
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-purple-400">Code Input</h2>
            <CodeEditor code={code} onChange={setCode} />
            <div className="mt-4 flex justify-end">
              <Button onClick={handleAnalyze} className="bg-purple-600 hover:bg-purple-700" disabled={isAnalyzing}>
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  "Analyze Code"
                )}
              </Button>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
            {result ? (
              <Tabs defaultValue="variables">
                <TabsList className="grid grid-cols-4 mb-4">
                  <TabsTrigger value="variables">Variables</TabsTrigger>
                  <TabsTrigger value="errors">Errors</TabsTrigger>
                  <TabsTrigger value="stats">Statistics</TabsTrigger>
                  <TabsTrigger value="optimizations">Optimizations</TabsTrigger>
                </TabsList>

                <TabsContent value="variables">
                  <VariablesTable variables={result.symbols} />
                  <div className="mt-6">
                    <TypeDistribution typeCounts={result.typeCounts} />
                  </div>
                </TabsContent>

                <TabsContent value="errors">
                  <ErrorsList
                    redeclared={result.redeclared}
                    undeclared={result.undeclared}
                    unused={result.unused}
                    uninitializedButUsed={result.uninitializedButUsed}
                  />
                </TabsContent>

                <TabsContent value="stats">
                  <StatsSummary
                    declarations={result.declarations}
                    assignments={result.assignments}
                    readWrite={result.readWrite}
                    conditionals={result.conditionals}
                    cyclic={result.cyclic}
                    nestings={result.nestings}
                  />
                </TabsContent>

                <TabsContent value="optimizations">
                  <IfOptimizations optimizations={result.ifOptimizations} />
                </TabsContent>
              </Tabs>
            ) : (
              <div className="flex flex-col items-center justify-center h-full">
                <p className="text-gray-400 text-center">
                  Enter your code and click "Analyze Code" to see the results.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
