import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Lightbulb } from "lucide-react"

interface IfOptimizationsProps {
  optimizations: string[]
}

export default function IfOptimizations({ optimizations }: IfOptimizationsProps) {
  return (
    <div>
      <h3 className="text-lg font-medium mb-2 text-purple-400">If Statement Optimizations</h3>

      {optimizations.length > 0 ? (
        <div className="space-y-3">
          <p className="text-gray-300">You have {optimizations.length} if statements that could be optimized:</p>

          {optimizations.map((optimization, index) => (
            <Alert key={index} className="bg-purple-900/30 border-purple-800">
              <Lightbulb className="h-4 w-4 text-yellow-400" />
              <AlertTitle className="text-purple-300">Optimization Suggestion</AlertTitle>
              <AlertDescription className="font-mono text-sm bg-gray-800 p-2 mt-2 rounded">
                {optimization}
              </AlertDescription>
            </Alert>
          ))}
        </div>
      ) : (
        <div className="text-center text-gray-400 py-8">No if statement optimizations found</div>
      )}
    </div>
  )
}
