import { MarkerType } from "react-flow-renderer"

const DEFAULT_EDGE_MARKER = {
  type: MarkerType.ArrowClosed,
  color: "#cbd5e1",
  width: 20,
  height: 20,
}

const DEFAULT_EDGE_STYLE = {
  stroke: "#94a3b8",
  strokeWidth: 1.75,
}

function createNode(id, type, label, x, y) {
  return {
    id,
    type: "typedBlock",
    position: { x, y },
    data: { label, type },
  }
}

function createEdge(id, source, target, label) {
  return {
    id,
    source,
    target,
    label,
    animated: true,
    style: DEFAULT_EDGE_STYLE,
    markerEnd: DEFAULT_EDGE_MARKER,
  }
}

/** Стартовые примеры графиков под id заданий (ответ / предпросмотр). Рёбрам задан маркер направления для React Flow. */
export function getStarterGraph(taskId) {
  if (taskId === 4) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 240, 40),
        createNode("2", "input", "Ввод N", 240, 150),
        createNode("3", "decision", "N mod 2 == 0 ?", 240, 280),
        createNode("4", "output", "Вывести «чётное»", 80, 430),
        createNode("5", "output", "Вывести «нечётное»", 400, 430),
        createNode("6", "end", "Конец", 240, 570),
      ],
      edges: [
        createEdge("e1-2", "1", "2"),
        createEdge("e2-3", "2", "3"),
        createEdge("e3-4", "3", "4", "да"),
        createEdge("e3-5", "3", "5", "нет"),
        createEdge("e4-6", "4", "6"),
        createEdge("e5-6", "5", "6"),
      ],
    }
  }

  if (taskId === 5) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 260, 40),
        createNode("2", "input", "Ввод N", 260, 150),
        createNode("3", "process", "i ← 1", 260, 260),
        createNode("4", "loop", "i ≤ 10", 260, 380),
        createNode("5", "output", "Вывести N·i", 60, 520),
        createNode("6", "process", "i ← i + 1", 60, 650),
        createNode("7", "end", "Конец", 460, 520),
      ],
      edges: [
        createEdge("e1-2", "1", "2"),
        createEdge("e2-3", "2", "3"),
        createEdge("e3-4", "3", "4"),
        createEdge("e4-5", "4", "5", "да"),
        createEdge("e5-6", "5", "6"),
        createEdge("e6-4", "6", "4"),
        createEdge("e4-7", "4", "7", "нет"),
      ],
    }
  }

  if (taskId === 6) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 330, 30),
        createNode("2", "input", "Ввод S", 330, 130),
        createNode("3", "process", "S → нижний регистр", 330, 230),
        createNode("4", "process", "left ← 0; right ← len(S) − 1", 330, 340),
        createNode("5", "decision", "left < right ?", 330, 470),
        createNode("6", "decision", "S[left] == S[right] ?", 110, 620),
        createNode("7", "process", "палиндром ← ложь", 520, 620),
        createNode("8", "process", "left++; right--", 110, 760),
        createNode("9", "decision", "палиндром ?", 520, 830),
        createNode("10", "output", "Вывести «палиндром»", 320, 980),
        createNode("11", "output", "Вывести «не палиндром»", 680, 980),
        createNode("12", "end", "Конец", 500, 1110),
      ],
      edges: [
        createEdge("e1-2", "1", "2"),
        createEdge("e2-3", "2", "3"),
        createEdge("e3-4", "3", "4"),
        createEdge("e4-5", "4", "5"),
        createEdge("e5-6", "5", "6", "да"),
        createEdge("e6-8", "6", "8", "да"),
        createEdge("e8-5", "8", "5"),
        createEdge("e6-7", "6", "7", "нет"),
        createEdge("e7-9", "7", "9"),
        createEdge("e5-9", "5", "9", "нет"),
        createEdge("e9-10", "9", "10", "да"),
        createEdge("e9-11", "9", "11", "нет"),
        createEdge("e10-12", "10", "12"),
        createEdge("e11-12", "11", "12"),
      ],
    }
  }

  if (taskId === 7) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 360, 20),
        createNode("2", "input", "Ввод N", 360, 120),
        createNode("3", "input", "Ввод массива A", 360, 230),
        createNode("4", "process", "i ← 0", 360, 340),
        createNode("5", "decision", "i < N − 1 ?", 360, 460),
        createNode("6", "process", "j ← 0", 100, 590),
        createNode("7", "decision", "j < N − i − 1 ?", 100, 720),
        createNode("8", "decision", "A[j] > A[j + 1] ?", 100, 860),
        createNode("9", "process", "обмен A[j], A[j+1]", 100, 1000),
        createNode("10", "process", "j ← j + 1", 100, 1120),
        createNode("11", "output", "Вывести A", 450, 860),
        createNode("12", "process", "i ← i + 1", 450, 1000),
        createNode("13", "end", "Конец", 620, 590),
      ],
      edges: [
        createEdge("e1-2", "1", "2"),
        createEdge("e2-3", "2", "3"),
        createEdge("e3-4", "3", "4"),
        createEdge("e4-5", "4", "5"),
        createEdge("e5-6", "5", "6", "да"),
        createEdge("e6-7", "6", "7"),
        createEdge("e7-8", "7", "8", "да"),
        createEdge("e8-9", "8", "9", "да"),
        createEdge("e9-10", "9", "10"),
        createEdge("e8-10", "8", "10", "нет"),
        createEdge("e10-7", "10", "7"),
        createEdge("e7-11", "7", "11", "нет"),
        createEdge("e11-12", "11", "12"),
        createEdge("e12-5", "12", "5"),
        createEdge("e5-13", "5", "13", "нет"),
      ],
    }
  }

  if (taskId === 25) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 240, 40),
        createNode("2", "input", "readln(n)", 240, 130),
        createNode("3", "process", "s := 0", 240, 220),
        createNode("4", "loop", "i := 1 to n", 240, 310),
        createNode("5", "process", "s := s + i", 240, 400),
        createNode("6", "output", "writeln(s)", 240, 490),
        createNode("7", "end", "Конец", 240, 580),
      ],
      edges: [
        createEdge("e1", "1", "2"),
        createEdge("e2", "2", "3"),
        createEdge("e3", "3", "4"),
        createEdge("e4", "4", "5", "тело"),
        createEdge("e5", "5", "4"),
        createEdge("e6", "4", "6", "выход"),
        createEdge("e7", "6", "7"),
      ],
    }
  }

  if (taskId === 13) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 240, 40),
        createNode("2", "input", "readln(n)", 240, 140),
        createNode("3", "decision", "n > 0 ?", 240, 260),
        createNode("4", "output", "writeln('pos')", 80, 400),
        createNode("5", "output", "writeln('nonpos')", 400, 400),
        createNode("6", "end", "Конец", 240, 530),
      ],
      edges: [
        createEdge("e1", "1", "2"),
        createEdge("e2", "2", "3"),
        createEdge("e3", "3", "4", "да"),
        createEdge("e4", "3", "5", "нет"),
        createEdge("e5", "4", "6"),
        createEdge("e6", "5", "6"),
      ],
    }
  }

  if (taskId === 0) {
    return {
      nodes: [
        createNode("1", "start", "Начало", 260, 40),
        createNode("2", "input", "Ввод", 240, 140),
        createNode("3", "process", "Действие", 240, 250),
        createNode("4", "output", "Вывод", 240, 360),
        createNode("5", "end", "Конец", 260, 470),
      ],
      edges: [
        createEdge("e1", "1", "2"),
        createEdge("e2", "2", "3"),
        createEdge("e3", "3", "4"),
        createEdge("e4", "4", "5"),
      ],
    }
  }

  return {
    nodes: [
      createNode("1", "start", "Начало", 260, 30),
      createNode("2", "input", "Ввести n", 240, 110),
      createNode("3", "process", "total = 0", 240, 200),
      createNode("4", "decision", "n > 0?", 240, 290),
    ],
    edges: [
      createEdge("e1-2", "1", "2"),
      createEdge("e2-3", "2", "3"),
      createEdge("e3-4", "3", "4"),
    ],
  }
}
