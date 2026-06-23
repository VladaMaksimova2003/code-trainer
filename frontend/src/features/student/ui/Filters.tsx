interface FiltersProps {
  search: unknown
  onSearchChange: (...args: unknown[]) => unknown
  langFrom: unknown
  langTo: unknown
  languageOptions: unknown
  onLangFromChange: (...args: unknown[]) => unknown
  onLangToChange: (...args: unknown[]) => unknown
  onSwapLangs: (...args: unknown[]) => unknown
  filterOpen: unknown
  onFilterOpenChange: (...args: unknown[]) => unknown
  filterCount: unknown
  matchMode: unknown
  onMatchModeChange: (...args: unknown[]) => unknown
  status: unknown
  onStatusChange: (...args: unknown[]) => unknown
  diff: unknown
  onDiffChange: (...args: unknown[]) => unknown
  type: unknown
  onTypeChange: (...args: unknown[]) => unknown
  patternSel: unknown
  onPatternSelChange: (...args: unknown[]) => unknown
  difficulties: unknown
  taskTypeOptions: unknown
  patternOptions: unknown
  onReset: (...args: unknown[]) => unknown
  hideStatusFilter?: boolean
}

import Chip from "@/shared/ui/Chip"

function FilterRow({ label, children }) {
  return (
    <div className="filter-row">
      <label>{label}</label>
      <div>{children}</div>
    </div>
  )
}

const DIFF_LABELS = { easy: "Лёгкая", medium: "Средняя", hard: "Сложная" }

export default function Filters({

  search,
  onSearchChange,
  langFrom,
  langTo,
  languageOptions,
  onLangFromChange,
  onLangToChange,
  onSwapLangs,
  filterOpen,
  onFilterOpenChange,
  filterCount,
  matchMode,
  onMatchModeChange,
  status,
  onStatusChange,
  diff,
  onDiffChange,
  type,
  onTypeChange,
  patternSel,
  onPatternSelChange,
  difficulties,
  taskTypeOptions,
  patternOptions,
  onReset,
  hideStatusFilter = false,

}: FiltersProps) {
  return (
    <div className="card card-pad filter-toolbar" style={{ padding: 14, marginBottom: 18 }}>
      <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
        <input
          className="input"
          style={{ flex: "1 1 240px", minWidth: 200 }}
          placeholder="Поиск задач…"
          value={search}
          onChange={(e: unknown) => onSearchChange(e.target.value)}
        />
        <select
          className="select"
          style={{ width: 140, flex: "none" }}
          value={langFrom}
          onChange={(e: unknown) => onLangFromChange(e.target.value)}
          title="Язык задачи"
        >
          <option value="all">Любой язык</option>
          {languageOptions.map((l: unknown) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
        <button type="button" className="swap-btn" onClick={onSwapLangs} title="Поменять языки">
          ⇄
        </button>
        <select
          className="select"
          style={{ width: 140, flex: "none" }}
          value={langTo}
          onChange={(e: unknown) => onLangToChange(e.target.value)}
          title="Целевой язык"
        >
          <option value="all">Любой язык</option>
          {languageOptions.map((l: unknown) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="btn btn-secondary"
          style={
            filterOpen
              ? { background: "var(--purple)", color: "#fff", boxShadow: "var(--glow-purple)" }
              : undefined
          }
          onClick={() => onFilterOpenChange(!filterOpen)}
        >
          Фильтр
          {filterCount > 0 ? (
            <span
              className="badge"
              style={{
                height: 20,
                padding: "0 7px",
                minWidth: 20,
                justifyContent: "center",
                background: filterOpen ? "rgba(255,255,255,.2)" : "var(--purple)",
                color: "#fff",
                border: 0,
                fontSize: 11,
                marginLeft: 2,
              }}
            >
              {filterCount}
            </span>
          ) : null}
        </button>
      </div>

      {filterOpen ? (
        <>
          <div className="filter-backdrop" onClick={() => onFilterOpenChange(false)} />
          <div className="filter-popover">
            <FilterRow label="Совпадение">
              <select
                className="select"
                style={{ maxWidth: 340 }}
                value={matchMode}
                onChange={(e: unknown) => onMatchModeChange(e.target.value)}
              >
                <option value="all">Все условия (AND)</option>
                <option value="any">Любое из условий (OR)</option>
              </select>
            </FilterRow>
            {!hideStatusFilter ? (
            <FilterRow label="Статус">
              <select
                className="select"
                style={{ maxWidth: 340 }}
                value={status}
                onChange={(e: unknown) => onStatusChange(e.target.value)}
              >
                <option value="all">Любой</option>
                <option value="solved">Решено</option>
                <option value="attempted">Попытка</option>
                <option value="todo">Не начато</option>
              </select>
            </FilterRow>
            ) : null}
            <FilterRow label="Сложность">
              <div className="wrap">
                {difficulties.map((d: unknown) => (
                  <Chip
                    key={d}
                    active={diff === d}
                    onClick={() => onDiffChange(diff === d ? "all" : d)}
                  >
                    {DIFF_LABELS[d] || d}
                  </Chip>
                ))}
              </div>
            </FilterRow>
            <FilterRow label="Типы">
              <div className="wrap">
                <Chip active={type === "all"} onClick={() => onTypeChange("all")}>
                  Все
                </Chip>
                {taskTypeOptions.slice(0, 5).map((t: unknown) => (
                  <Chip key={t.id} active={type === t.id} onClick={() => onTypeChange(t.id)}>
                    {t.label}
                  </Chip>
                ))}
              </div>
            </FilterRow>
            <FilterRow label="Конструкции">
              <select
                className="select"
                style={{ maxWidth: 340 }}
                value={patternSel}
                onChange={(e: unknown) => onPatternSelChange(e.target.value)}
              >
                <option value="">Выберите конструкцию</option>
                {patternOptions.map((p: unknown) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </FilterRow>
            <div
              className="row"
              style={{
                justifyContent: "flex-end",
                gap: 10,
                marginTop: 14,
                paddingTop: 14,
                borderTop: "1px solid var(--border)",
              }}
            >
              <button type="button" className="btn btn-ghost" onClick={onReset}>
                Сбросить
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => onFilterOpenChange(false)}
              >
                Применить
              </button>
            </div>
          </div>
        </>
      ) : null}
    </div>
  )
}
