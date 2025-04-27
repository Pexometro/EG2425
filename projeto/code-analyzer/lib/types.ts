export interface Symbol {
  name: string
  type: string
  scope: string
  isInitialized: boolean
  isUsed: boolean
  isRedeclared: boolean
  line: number
  column: number
}

export interface AnalysisResult {
  symbols: Symbol[]
  redeclared: Symbol[]
  undeclared: [string, number, number][]
  unused: Symbol[]
  uninitializedButUsed: Symbol[]
  typeCounts: Record<string, number>
  declarations: number
  assignments: number
  readWrite: number
  conditionals: number
  cyclic: number
  nestings: number
  ifOptimizations: string[]
}
