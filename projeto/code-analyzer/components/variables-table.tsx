import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { Symbol } from "@/lib/types"

interface VariablesTableProps {
  variables: Symbol[]
}

export default function VariablesTable({ variables }: VariablesTableProps) {
  return (
    <div>
      <h3 className="text-lg font-medium mb-2 text-purple-400">Variables</h3>
      <div className="rounded-md border border-gray-700 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-gray-900">
              <TableHead className="text-purple-300">ID</TableHead>
              <TableHead className="text-purple-300">Scope</TableHead>
              <TableHead className="text-purple-300">Type</TableHead>
              <TableHead className="text-purple-300">Initialized</TableHead>
              <TableHead className="text-purple-300">Used</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {variables.length > 0 ? (
              variables.map((variable, index) => (
                <TableRow key={index} className="border-t border-gray-700">
                  <TableCell>{variable.name}</TableCell>
                  <TableCell>{variable.scope}</TableCell>
                  <TableCell>{variable.type}</TableCell>
                  <TableCell>
                    {variable.isInitialized ? (
                      <span className="text-green-500">Yes</span>
                    ) : (
                      <span className="text-red-500">No</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {variable.isUsed ? (
                      <span className="text-green-500">Yes</span>
                    ) : (
                      <span className="text-red-500">No</span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-gray-400">
                  No variables found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
