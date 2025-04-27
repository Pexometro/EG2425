import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Database } from "lucide-react"

interface TypeDistributionProps {
  typeCounts: Record<string, number>
}

export default function TypeDistribution({ typeCounts }: TypeDistributionProps) {
  const data = Object.entries(typeCounts).map(([name, value], index) => ({
    name,
    value,
  }))

  const COLORS = ["#9333ea", "#ec4899", "#8b5cf6", "#d946ef", "#a855f7", "#f472b6"]

  return (
    <Card className="bg-gray-900 border-gray-700">
      <CardHeader>
        <CardTitle className="text-purple-300 flex items-center">
          <Database className="h-5 w-5 mr-2 text-purple-400" />
          Type Distribution
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px]">
          {data.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, name: string) => [`${value} variables`, name]}
                  contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: "0.375rem" }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">No type data available</div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
