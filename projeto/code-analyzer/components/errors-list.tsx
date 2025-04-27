import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import type { Symbol } from "@/lib/types"
import { AlertCircle, AlertTriangle } from "lucide-react"

interface ErrorsListProps {
  redeclared: Symbol[]
  undeclared: [string, number, number][]
  unused: Symbol[]
  uninitializedButUsed: Symbol[]
}

export default function ErrorsList({ redeclared, undeclared, unused, uninitializedButUsed }: ErrorsListProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium mb-2 text-purple-400">Errors & Warnings</h3>

      {redeclared.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-red-400">Redeclared Variables</h4>
          {redeclared.map((variable, index) => (
            <Alert key={index} variant="destructive" className="bg-red-900/30 border-red-800">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle className="text-red-400">Error</AlertTitle>
              <AlertDescription>
                Variable <code className="bg-red-900/50 px-1 rounded">{variable.name}</code> already declared in scope{" "}
                {variable.scope} (line {variable.line}, column {variable.column})
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {undeclared.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-red-400">Undeclared Variables</h4>
          {undeclared.map((variable, index) => (
            <Alert key={index} variant="destructive" className="bg-red-900/30 border-red-800">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle className="text-red-400">Error</AlertTitle>
              <AlertDescription>
                Variable <code className="bg-red-900/50 px-1 rounded">{variable[0]}</code> not declared (line{" "}
                {variable[1]}, column {variable[2]})
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {unused.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-amber-400">Unused Variables</h4>
          {unused.map((variable, index) => (
            <Alert key={index} variant="default" className="bg-amber-900/30 border-amber-800">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <AlertTitle className="text-amber-400">Warning</AlertTitle>
              <AlertDescription>
                Variable <code className="bg-amber-900/50 px-1 rounded">{variable.name}</code> declared but never used
                (line {variable.line}, column {variable.column})
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {uninitializedButUsed.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-amber-400">Uninitialized Variables</h4>
          {uninitializedButUsed.map((variable, index) => (
            <Alert key={index} variant="default" className="bg-amber-900/30 border-amber-800">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <AlertTitle className="text-amber-400">Warning</AlertTitle>
              <AlertDescription>
                Variable <code className="bg-amber-900/50 px-1 rounded">{variable.name}</code> used but not initialized
                (line {variable.line}, column {variable.column})
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {redeclared.length === 0 &&
        undeclared.length === 0 &&
        unused.length === 0 &&
        uninitializedButUsed.length === 0 && (
          <div className="text-center text-gray-400 py-8">No errors or warnings found</div>
        )}
    </div>
  )
}
