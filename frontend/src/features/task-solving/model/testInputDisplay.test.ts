import { describe, expect, it } from "vitest"
import {
  formatStdinForDisplay,
  inferStdinLayout,
  testInputDisplayContextFromTask,
} from "@/features/task-solving/model/testInputDisplay"

const SUM_CPP_CTX = {
  goal: "Вводится количество дней и выручка за каждый день.",
  cppCode: `#include <iostream>
int main(){
  int n; std::cin >> n;
  int total = 0;
  for(int i = 0; i < n; i++){
    int sale; std::cin >> sale;
    total += sale;
  }
  std::cout << total;
}`,
}

const SEARCH_CTX = {
  patternId: "task_002",
  goal: "В первой строке вводятся количество товаров и искомый код. Затем вводятся коды товаров по одному.",
  pascalCode: "readln(n, target);",
  cppCode: `#include <iostream>
int main() {
  int n, target;
  std::cin >> n >> target;
  for (int i = 1; i <= n; i++) {
    int code;
    std::cin >> code;
  }
}`,
}

describe("formatStdinForDisplay", () => {
  it("shows count on first line and loop-read scalars on one line", () => {
    expect(formatStdinForDisplay("5\n2\n9\n1\n7\n4\n", SUM_CPP_CTX)).toBe("5\n2 9 1 7 4")
  })

  it("keeps two scalars on one line when read together", () => {
    expect(formatStdinForDisplay("5 12\n8\n3\n12\n5\n9\n", SEARCH_CTX)).toBe(
      "5 12\n8 3 12 5 9",
    )
  })

  it("shows three scalars on one line", () => {
    const ctx = {
      goal: "Даны три целых числа.",
      cppCode: "int a,b,c; std::cin >> a >> b >> c;",
    }
    expect(inferStdinLayout(ctx)).toBe("first_line_3")
    expect(formatStdinForDisplay("3 7 2\n", ctx)).toBe("3 7 2")
  })

  it("builds context from task payload", () => {
    const ctx = testInputDisplayContextFromTask(
      {
        description: SUM_CPP_CTX.goal,
        code_examples: { cpp: SUM_CPP_CTX.cppCode },
      },
      "csharp",
    )
    expect(formatStdinForDisplay("1\n10\n", ctx)).toBe("1\n10")
  })

  it("keeps list reads in brackets", () => {
    const ctx = {
      goal: "Дан список чисел в одной строке.",
      referenceCode: "a = list(map(int, input().split()))\nprint(sum(a))",
    }
    expect(formatStdinForDisplay("2 9 1 7 4\n", ctx)).toBe("[2, 9, 1, 7, 4]")
  })
})
