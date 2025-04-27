import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart3, FileCode, GitCompare, LayoutList, Pencil, RefreshCw, SplitSquareVertical } from "lucide-react"

interface StatsSummaryProps {
  declarations: number
  assignments: number
  readWrite: number
  conditionals: number
  cyclic: number
  nestings: number
}

export default function StatsSummary({
  declarations,
  assignments,
  readWrite,
  conditionals,
  cyclic,
  nestings,
}: StatsSummaryProps) {
  const total = declarations + assignments + readWrite + conditionals + cyclic

  return (
    <div>
      <h3 className="text-lg font-medium mb-2 text-purple-400">Code Statistics</h3>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <Card className="bg-gray-900 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-300">
              <FileCode className="h-4 w-4 mr-2 text-purple-400" />
              Declarations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{declarations}</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-300">
              <Pencil className="h-4 w-4 mr-2 text-purple-400" />
              Assignments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assignments}</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-300">
              <LayoutList className="h-4 w-4 mr-2 text-purple-400" />
              Read/Write
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{readWrite}</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-300">
              <GitCompare className="h-4 w-4 mr-2 text-purple-400" />
              Conditionals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{conditionals}</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-300">
              <RefreshCw className="h-4 w-4 mr-2 text-purple-400" />
              Cycles
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{cyclic}</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-300">
              <SplitSquareVertical className="h-4 w-4 mr-2 text-purple-400" />
              Nestings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{nestings}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-purple-300 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2 text-purple-400" />
            Instruction Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Declarations</span>
                <span className="text-sm text-gray-400">{Math.round((declarations / total) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-500 rounded-full"
                  style={{ width: `${(declarations / total) * 100}%` }}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Assignments</span>
                <span className="text-sm text-gray-400">{Math.round((assignments / total) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-pink-500 rounded-full" style={{ width: `${(assignments / total) * 100}%` }} />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Read/Write</span>
                <span className="text-sm text-gray-400">{Math.round((readWrite / total) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(readWrite / total) * 100}%` }} />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Conditionals</span>
                <span className="text-sm text-gray-400">{Math.round((conditionals / total) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-yellow-500 rounded-full"
                  style={{ width: `${(conditionals / total) * 100}%` }}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Cycles</span>
                <span className="text-sm text-gray-400">{Math.round((cyclic / total) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: `${(cyclic / total) * 100}%` }} />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
