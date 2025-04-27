import { type NextRequest, NextResponse } from "next/server"
import { exec } from "child_process"
import { promisify } from "util"
import fs from "fs/promises"
import path from "path"
import os from "os"
import type { AnalysisResult } from "@/lib/types"

const execPromise = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const { code } = await request.json()

    if (!code) {
      return NextResponse.json({ error: "No code provided" }, { status: 400 })
    }

    // Create temporary files for the code
    const tempDir = os.tmpdir()
    const tempFilePath = path.join(tempDir, `input_${Date.now()}.lpi`)

    try {
      // Write the code to the temporary file
      await fs.writeFile(tempFilePath, code)

      // Get the absolute path to fase2.py
      const analyzerPath = path.join(process.cwd(), "fase2.py")

      // Execute the Python analyzer script
      const { stdout, stderr } = await execPromise(`python ${analyzerPath} ${tempFilePath} --json`)

      if (stderr && !stderr.includes("Traceback")) {
        console.warn("Analyzer warnings:", stderr)
      }

      // Parse JSON output
      const result = JSON.parse(stdout)

      return NextResponse.json(result)
    } catch (error) {
      console.error("Error executing analyzer:", error)
      return NextResponse.json({ error: "Error executing analyzer" }, { status: 500 })
    } finally {
      // Clean up temporary file
      try {
        await fs.unlink(tempFilePath)
      } catch (e) {
        console.warn("Could not delete temporary file:", e)
      }
    }
  } catch (error) {
    console.error("Error analyzing code:", error)
    return NextResponse.json({ error: "Error analyzing code" }, { status: 500 })
  }
}

// Function to parse the output from fase2.py
function parseAnalyzerOutput(output: string): AnalysisResult {
  // Initialize the result object
  const result: AnalysisResult = {
    symbols: [],
    redeclared: [],
    undeclared: [],
    unused: [],
    uninitializedButUsed: [],
    typeCounts: {},
    declarations: 0,
    assignments: 0,
    readWrite: 0,
    conditionals: 0,
    cyclic: 0,
    nestings: 0,
    ifOptimizations: [],
  }

  // Parse the symbol table
  const symbolTableMatch = output.match(/tabela de simbolos:\n\n([\s\S]*?)===/)
  if (symbolTableMatch) {
    const symbolTableText = symbolTableMatch[1]
    const symbolLines = symbolTableText.trim().split("\n")

    symbolLines.forEach((line) => {
      const match = line.match(/Nome: (.*?), Tipo: (.*?), Escopo: (.*?), Inicializado: (.*?), Usado: (.*)/)
      if (match) {
        const [_, name, type, scope, initializedStr, usedStr] = match
        const isInitialized = initializedStr === "True"
        const isUsed = usedStr === "True"

        result.symbols.push({
          name,
          type,
          scope,
          isInitialized,
          isUsed,
          isRedeclared: false, // Will be updated later
          line: 0, // Will be updated if found in errors
          column: 0, // Will be updated if found in errors
        })
      }
    })
  }

  // Parse redeclared variables
  const redeclaredMatch = output.match(/Variáveis redeclaradas:\n([\s\S]*?)Variáveis não declaradas:/)
  if (redeclaredMatch) {
    const redeclaredText = redeclaredMatch[1]
    const redeclaredLines = redeclaredText.trim().split("\n")

    redeclaredLines.forEach((line) => {
      if (line.trim() && !line.includes("Variáveis redeclaradas:")) {
        const match = line.match(/\s+(.*?) $$linha (\d+), coluna (\d+)$$/)
        if (match) {
          const [_, name, lineNum, colNum] = match

          // Find the symbol and mark as redeclared
          const symbol = result.symbols.find((s) => s.name === name)
          if (symbol) {
            symbol.isRedeclared = true
            symbol.line = Number.parseInt(lineNum)
            symbol.column = Number.parseInt(colNum)
            result.redeclared.push({ ...symbol })
          }
        }
      }
    })
  }

  // Parse undeclared variables
  const undeclaredMatch = output.match(/Variáveis não declaradas:\n([\s\S]*?)Variáveis não usadas:/)
  if (undeclaredMatch) {
    const undeclaredText = undeclaredMatch[1]
    const undeclaredLines = undeclaredText.trim().split("\n")

    undeclaredLines.forEach((line) => {
      if (line.trim() && !line.includes("Variáveis não declaradas:")) {
        const match = line.match(/\s+(.*?) $$linha (\d+), coluna (\d+)$$/)
        if (match) {
          const [_, name, lineNum, colNum] = match
          result.undeclared.push([name, Number.parseInt(lineNum), Number.parseInt(colNum)])
        }
      }
    })
  }

  // Parse unused variables
  const unusedMatch = output.match(/Variáveis não usadas:\n([\s\S]*?)Variáveis usadas sem inicialização:/)
  if (unusedMatch) {
    const unusedText = unusedMatch[1]
    const unusedLines = unusedText.trim().split("\n")

    unusedLines.forEach((line) => {
      if (line.trim() && !line.includes("Variáveis não usadas:")) {
        const match = line.match(/\s+(.*?) $$linha (\d+), coluna (\d+)$$/)
        if (match) {
          const [_, name, lineNum, colNum] = match

          // Find the symbol
          const symbol = result.symbols.find((s) => s.name === name)
          if (symbol) {
            symbol.line = Number.parseInt(lineNum)
            symbol.column = Number.parseInt(colNum)
            result.unused.push({ ...symbol })
          }
        }
      }
    })
  }

  // Parse uninitialized but used variables
  const uninitializedMatch = output.match(/Variáveis usadas sem inicialização:\n([\s\S]*?)Contagem por tipo:/)
  if (uninitializedMatch) {
    const uninitializedText = uninitializedMatch[1]
    const uninitializedLines = uninitializedText.trim().split("\n")

    uninitializedLines.forEach((line) => {
      if (line.trim() && !line.includes("Variáveis usadas sem inicialização:")) {
        const match = line.match(/\s+(.*?) $$linha (\d+), coluna (\d+)$$/)
        if (match) {
          const [_, name, lineNum, colNum] = match

          // Find the symbol
          const symbol = result.symbols.find((s) => s.name === name)
          if (symbol) {
            symbol.line = Number.parseInt(lineNum)
            symbol.column = Number.parseInt(colNum)
            result.uninitializedButUsed.push({ ...symbol })
          }
        }
      }
    })
  }

  // Parse type counts
  const typeCountsMatch = output.match(/Contagem por tipo:\n([\s\S]*?)----------------------------------/)
  if (typeCountsMatch) {
    const typeCountsText = typeCountsMatch[1]
    const typeCountsLines = typeCountsText.trim().split("\n")

    typeCountsLines.forEach((line) => {
      if (line.trim()) {
        const match = line.match(/\s+(.*?): (\d+)/)
        if (match) {
          const [_, type, count] = match
          result.typeCounts[type] = Number.parseInt(count)
        }
      }
    })
  }

  // Parse instruction counts
  const declarationsMatch = output.match(/Declarations: (\d+)/)
  if (declarationsMatch) {
    result.declarations = Number.parseInt(declarationsMatch[1])
  }

  const assignmentsMatch = output.match(/Assignments: (\d+)/)
  if (assignmentsMatch) {
    result.assignments = Number.parseInt(assignmentsMatch[1])
  }

  const readWriteMatch = output.match(/Read\/Write: (\d+)/)
  if (readWriteMatch) {
    result.readWrite = Number.parseInt(readWriteMatch[1])
  }

  const conditionalsMatch = output.match(/Conditionals: (\d+)/)
  if (conditionalsMatch) {
    result.conditionals = Number.parseInt(conditionalsMatch[1])
  }

  const cyclicMatch = output.match(/Cyclic: (\d+)/)
  if (cyclicMatch) {
    result.cyclic = Number.parseInt(cyclicMatch[1])
  }

  const aninhamentosMatch = output.match(/Aninhamentos: (\d+)/)
  if (aninhamentosMatch) {
    result.nestings = Number.parseInt(aninhamentosMatch[1])
  }

  // For if optimizations, we would need to add this to your fase2.py output
  // For now, we'll leave it empty

  return result
}
