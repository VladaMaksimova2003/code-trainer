/** Language-aware checks for expected curriculum concepts in student code. */

export function isProgramEntryUsed(code: string, language: string): boolean {
  const text = String(code || "")
  if (!text.trim()) return false

  const lang = String(language || "").toLowerCase()
  switch (lang) {
    case "python":
      return true
    case "pascal":
      return /\b(program|begin)\b/i.test(text)
    case "cpp":
      return /\bmain\s*\(/i.test(text)
    case "csharp":
    case "cs":
    case "c#":
      return /\bstatic\s+void\s+Main\s*\(/i.test(text)
    case "java":
      return /\bpublic\s+static\s+void\s+main\s*\(/i.test(text)
    case "javascript":
    case "js":
      return /\b(function|class|const|let|var|import)\b/.test(text) || text.trim().length > 0
    default:
      return /\b(program|main|__name__|begin)\b/i.test(text) || text.trim().length > 0
  }
}

export function isConceptUsedForLanguage(
  conceptId: string,
  code: string,
  language: string,
  technicalConceptIds?: string[],
): boolean {
  if (conceptId === "program_entry" || conceptId === "tc_program_structure") {
    return isProgramEntryUsed(code, language)
  }

  const techIds = (
    technicalConceptIds?.length
      ? technicalConceptIds
      : conceptId.startsWith("tc_")
        ? []
        : [conceptId]
  ).map(String)

  if (techIds.length === 0) {
    return defaultConceptCheck(conceptId, code, language)
  }

  return techIds.some((id) => defaultConceptCheck(id, code, language))
}

function defaultConceptCheck(conceptId: string, code: string, language: string): boolean {
  const lang = String(language || "").toLowerCase()
  const checks: Record<string, (c: string, l: string) => boolean> = {
    block_scope: (c) => /\bbegin\b/i.test(c) || /\{\s*$/.test(c) || /\{/.test(c),
    main_entry: (_c, l) => isProgramEntryUsed(_c, l),
    program_root: (_c, l) => isProgramEntryUsed(_c, l) || /\b(program|begin)\b/i.test(_c),
    pascal_comment: (c) => /\{|\(\*/.test(c),
    variable_declaration: (c, l) => variableDeclarationUsed(c, l),
    typed_declaration: (c, l) => variableDeclarationUsed(c, l),
    constant_declaration: (c) => /\bconst\b|\bfinal\b|[A-Z][A-Z0-9_]{2,}\s*=/.test(c),
    assignment: (c) => /:=|=(?!=)|\+=/.test(c),
    arithmetic: (c) => /\b(div|mod|\/\/)\b/.test(c) || /[+\-*\/%]/.test(c),
    arithmetic_ops: (c) => /\b(div|mod|\/\/)\b/.test(c) || /[+\-*\/%]/.test(c),
    console_input: (c) =>
      /\b(readln|read\s*\(|input\s*\(|ReadLine\s*\(|Scanner\b|std::cin|\bcin\b|scanf\s*\()/i.test(
        c,
      ) || /\binput\s*\(\s*\)\s*\.\s*split\s*\(/i.test(c),
    stdin_read: (c) =>
      /\b(readln|read\s*\(|input\s*\(|ReadLine\s*\(|Scanner\b|std::cin|\bcin\b|scanf\s*\()/i.test(
        c,
      ) || /\binput\s*\(\s*\)\s*\.\s*split\s*\(/i.test(c),
    console_output: (c) =>
      /\b(writeln|write|print\(|cout|Console\.|System\.out\.)/i.test(c),
    stdout_write: (c) =>
      /\b(writeln|write|print\(|cout|Console\.|System\.out\.)/i.test(c),
    import_dependency: (c) => /\b(uses|import|from|#include|using)\b/i.test(c),
    module_namespace: (c) => /\b(unit|namespace|module)\b/i.test(c),
    symbol_visibility: (c) => /\b(interface|implementation|public|private|protected)\b/i.test(c),
    simple_branch: (c) => /\bif\b/.test(c),
    multi_branch: (c) => /\belse\b/i.test(c) || /\belif\b/i.test(c),
    switch_selection: (c) => /\b(case|switch|match)\b/i.test(c),
    conditional_expression: (c) => /\bif\b/.test(c) || /\?.*:/.test(c),
    counted_loop: (c) => /\bfor\b/i.test(c),
    pre_condition_loop: (c) => /\bwhile\b/i.test(c),
    post_condition_loop: (c) => /\b(repeat|do\s*\{)/i.test(c),
    loop_control: (c) => /\b(break|continue|exit)\b/i.test(c),
    nested_iteration: (c) => /for[\s\S]*for/i.test(c) || /while[\s\S]*while/i.test(c),
    collection_iteration: (c) =>
      (/\bfor\b.*\bin\b/i.test(c) && !/\bin\s+range\s*\(/i.test(c)) ||
      /\bfor\s*\([^)]*:/.test(c) ||
      /\.forEach\(/.test(c),
    function_definition: (c) => /\b(function|procedure|def)\b/i.test(c),
    procedure_definition: (c) => /\bprocedure\b/i.test(c),
    return_flow: (c) => /\b(return|Result\s*:=)\b/i.test(c),
    parameter_passing: (c) => /\b(procedure|function|def)\s+\w+\s*\(/i.test(c),
    function_invocation: (c) => /\w+\s*\(/.test(c),
    recursion: (c) => /\bfunction\b[\s\S]*\bFact\b|\bdef\b[\s\S]*\bself\b/i.test(c),
    indexed_sequence: (c) => /\barray\b|\[\d/.test(c),
    dynamic_array: (c) => /\bSetLength\b|\blist\(|\[\]/.test(c),
    string_sequence: (c) => /\b(string|str)\b/i.test(c) || /\.strip\(/.test(c),
    key_value_map: (c) => /\b(record|dict|Map|struct)\b/i.test(c),
    file_read: (c) => /\b(open\(|Reset|AssignFile|Readln)\b/i.test(c),
    file_write: (c) => /\b(Rewrite|WriteLn|write\()\b/i.test(c),
    search_find: (c) =>
      (/\bif\b/.test(c) && /\bfor\b/i.test(c) && /(==|!=|<=|>=|<|>|=|:=)/.test(c)) ||
      /\b(in|find|index|contains)\b/i.test(c),
    filter_select: (c) => /\bif\b/i.test(c) && /\bfor\b/i.test(c),
    fold_aggregate: (c) => /\bsum\b|\+/.test(c) && /\bfor\b/i.test(c),
    sort_order: (c) => /\bsort\b|<|>/.test(c),
    stack_queue: (c) => /\bstack\b|\bqueue\b|\btop\b/i.test(c),
    linked_node: (c) => /\bnext\b|\^Node|\->next/.test(c),
    tree_hierarchy: (c) => /\bleft\b|\bright\b|\bchildren\b/.test(c),
    graph_edges: (c) => /\badj\b|\bedge\b|\bgraph\b/i.test(c),
    class_type: (c) => /\bclass\b/i.test(c),
    object_instance: (c) => /\b(Create|new |\.Free\b)/i.test(c),
    field_access: (c) => /\.\w+/.test(c),
    method_dispatch: (c) => /\.\w+\s*\(/.test(c),
    inheritance_hierarchy: (c) => /\b(class\s*\(|extends|: public|override)\b/i.test(c),
    parent_class: (c) => /\bvirtual\b|\bclass\b/i.test(c),
    child_class: (c) => /\boverride\b|\bclass\s*\(/i.test(c),
    loop: (c) => /\bfor\b/i.test(c) || /\bwhile\b/i.test(c),
    nested_loop: (c) => /for[\s\S]*for/i.test(c) || /while[\s\S]*while/i.test(c),
  }

  const check = checks[conceptId]
  return check ? check(String(code || ""), lang) : false
}

function variableDeclarationUsed(code: string, language: string): boolean {
  const text = String(code || "")
  const lang = String(language || "").toLowerCase()
  if (lang === "python") {
    return (
      /\b\w+\s*=/.test(text) ||
      /\w+\s*:\s*\w+/.test(text) ||
      /\bint\s*\(/.test(text) ||
      /\bfloat\s*\(/.test(text) ||
      /\bstr\s*\(/.test(text)
    )
  }
  return (
    /\b(var|const|type|def|class|int |float |double |string|boolean)\b/i.test(text) ||
    /:\s*(integer|real|boolean|char|string)/i.test(text)
  )
}
