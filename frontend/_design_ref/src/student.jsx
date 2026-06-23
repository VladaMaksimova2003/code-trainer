/* global React */
const { useState, useMemo, useEffect, useRef } = React;

/* =========================================================
   STUDENT SIDEBAR (shared across student pages)
   ========================================================= */
function studentSidebarItems() {
  return [
    { divider: 'Обучение' },
    { to:'/',                 label:'Список задач',    matches:(p)=>p==='/' },
    { to:'/learn/pascal',     label:'Учебные треки',   matches:(p)=>p.startsWith('/learn') },
    { to:'/student/profile',  label:'Профиль',         matches:(p)=>p.startsWith('/student/profile') },
    { to:'/student/groups',   label:'Мои группы',      matches:(p)=>p.startsWith('/student/groups') },
    { divider: 'Аккаунт' },
    { to:'/settings/profile', label:'Настройки',       matches:(p)=>p.startsWith('/settings') },
  ];
}

/* =========================================================
   TASKS PAGE  ( / )
   ========================================================= */
function TasksPage() {
  const { navigate } = useRouter();
  const toast = useToast();
  const data = window.MOCK;

  // filters — new design: search + langFrom ⇄ langTo + "Фильтр" panel
  const [search, setSearch] = useState('');
  const [type, setType] = useState('all');
  const [status, setStatus] = useState('all');
  const [diff, setDiff] = useState('all');
  const [langFrom, setLangFrom] = useState('all');
  const [langTo, setLangTo] = useState('all');
  const [patternSel, setPatternSel] = useState(''); // single value, '' = any
  const [matchMode, setMatchMode] = useState('all'); // 'all' / 'any'
  const [filterOpen, setFilterOpen] = useState(false);

  // pagination
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // assignment-sets — interactive: add by code
  const [sets, setSets] = useState(data.assignmentSets);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteCode, setInviteCode] = useState('');

  const filtered = useMemo(() => {
    const activeFilters = []; // for "matchMode" semantics
    return data.tasks.filter(t => {
      if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false;
      // langFrom is the primary lang filter; langTo is for Translation tasks only
      if (langFrom !== 'all' && t.lang !== langFrom) return false;
      // Other filters: AND when matchMode='all', OR when matchMode='any' (excluding 'all' values)
      const checks = [
        { key:'type',    on: type !== 'all',    pass: t.type === type },
        { key:'status',  on: status !== 'all',  pass: t.status === status },
        { key:'diff',    on: diff !== 'all',    pass: t.diff === diff },
        { key:'pattern', on: patternSel !== '', pass: t.pattern === patternSel },
      ];
      const active = checks.filter(c => c.on);
      if (active.length === 0) return true;
      if (matchMode === 'any') return active.some(c => c.pass);
      return active.every(c => c.pass);
    });
  }, [data.tasks, search, type, status, diff, langFrom, patternSel, matchMode]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const paged = filtered.slice((page-1)*pageSize, page*pageSize);
  useEffect(() => { if (page > pageCount) setPage(1); }, [pageCount, page]);

  const stats = useMemo(() => {
    const solved = data.tasks.filter(t => t.status === 'solved').length;
    return { solved, total: data.tasks.length };
  }, [data.tasks]);

  const continueLearning = () => {
    const next = data.tasks.find(t => t.status !== 'solved');
    if (next) { toast.push({ kind:'lime', title:'Рекомендация загружена', body:next.title }); navigate(`/tasks/${next.id}`); }
  };

  const togglePattern = (p) => {
    setPatternSel(prev => prev === p ? '' : p);
    setPage(1);
  };

  const resetFilters = () => {
    setType('all'); setStatus('all'); setDiff('all');
    setLangFrom('all'); setLangTo('all');
    setPatternSel(''); setMatchMode('all');
    setSearch(''); setPage(1);
  };

  const swapLangs = () => { const a = langFrom, b = langTo; setLangFrom(b); setLangTo(a); setPage(1); };

  const filterCount = (type!=='all'?1:0)+(status!=='all'?1:0)+(diff!=='all'?1:0)+(patternSel?1:0);

  const joinSet = () => {
    const code = inviteCode.trim().toUpperCase();
    if (!code) return;
    const newSet = { id:'custom-'+Math.random().toString(36).slice(2,5), name:`Сборник ${code}`, total:6, solved:0, color:'purple' };
    setSets(s => [...s, newSet]);
    setInviteOpen(false); setInviteCode('');
    toast.push({ kind:'lime', title:'Сборник добавлен', body:newSet.name });
  };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: studentSidebarItems(), role:'STUDENT' }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Тренажёр', crumbCurrent:'Список задач' },
        React.createElement('button', { className:'icon-btn', title:'Уведомления' }, '🔔'),
      ),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, {
          title:'Список задач',
          subtitle:`Решено ${stats.solved} из ${stats.total} · средняя сложность растёт`,
          right: [
            React.createElement('button', { key:1, className:'btn btn-secondary btn-sm', onClick:()=>navigate('/student/profile') }, 'Профиль ученика'),
          ]
        }),

        // Compact "continue learning" → straight to the current task
        React.createElement('button', { className:'track-entry', onClick:()=>navigate('/tasks/2') },
          React.createElement('div', { className:'te-glyph' }, 'Py'),
          React.createElement('div', { style:{flex:'1 1 auto', minWidth:0} },
            React.createElement('div', { className:'row', style:{gap:8, marginBottom:3, flexWrap:'wrap'} },
              React.createElement('b', { style:{fontSize:15} }, 'Учебный трек'),
              React.createElement(Badge, { kind:'purple' }, 'Python'),
              React.createElement('span', { className:'mut3 mono', style:{fontSize:12} }, '24/270 · 9%'),
            ),
            React.createElement('div', { className:'mut3', style:{fontSize:13, display:'flex', alignItems:'center', gap:7, minWidth:0} },
              React.createElement('span', { style:{color:'var(--text-2)'} }, 'Продолжаете:'),
              React.createElement('span', { style:{color:'var(--text)', fontWeight:500, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'} }, '3. Условия · Тернарный оператор'),
            ),
          ),
          React.createElement('span', { className:'btn btn-primary btn-sm', style:{flex:'none', pointerEvents:'none'} }, 'Продолжить обучение'),
        ),

        // New filter toolbar: search + langFrom ⇄ langTo + Фильтр button + popover panel
        React.createElement('div', { className:'card card-pad filter-toolbar', style:{padding:14, marginBottom:18} },
          React.createElement('div', { className:'row', style:{gap:10, flexWrap:'wrap'} },
            React.createElement('input', {
              className:'input',
              style:{flex:'1 1 240px', minWidth:200},
              placeholder:'Поиск задач…', value:search,
              onChange: e => { setSearch(e.target.value); setPage(1); }
            }),
            React.createElement('select', {
              className:'select', style:{width:140, flex:'none'},
              value:langFrom, onChange:e => { setLangFrom(e.target.value); setPage(1); },
              title:'Язык задачи'
            },
              React.createElement('option', { value:'all' }, 'Любой язык'),
              ...data.languages.map(l => React.createElement('option', { key:l, value:l }, l))
            ),
            React.createElement('button', { className:'swap-btn', onClick:swapLangs, title:'Поменять языки местами' }, '⇄'),
            React.createElement('select', {
              className:'select', style:{width:140, flex:'none'},
              value:langTo, onChange:e => { setLangTo(e.target.value); setPage(1); },
              title:'Целевой язык (для Translation)'
            },
              React.createElement('option', { value:'all' }, 'Любой язык'),
              ...data.languages.map(l => React.createElement('option', { key:l, value:l }, l))
            ),
            React.createElement('button', {
              className: filterOpen ? 'btn btn-secondary' : 'btn btn-secondary',
              style: filterOpen ? { background:'var(--purple)', color:'#fff', boxShadow:'var(--glow-purple)' } : null,
              onClick: () => setFilterOpen(o => !o)
            },
              'Фильтр',
              filterCount > 0 && React.createElement('span', {
                className:'badge', style:{
                  height:20, padding:'0 7px', minWidth:20, justifyContent:'center',
                  background: filterOpen?'rgba(255,255,255,.2)':'var(--purple)',
                  color:'#fff', border:0, fontSize:11, marginLeft:2
                }
              }, filterCount)
            ),
          ),
          filterOpen && React.createElement(React.Fragment, null,
            React.createElement('div', { className:'filter-backdrop', onClick:()=>setFilterOpen(false) }),
            React.createElement('div', { className:'filter-popover' },
            React.createElement(FilterRow, { label:'Совпадение' },
              React.createElement('select', { className:'select', style:{maxWidth:340}, value:matchMode, onChange:e => setMatchMode(e.target.value) },
                React.createElement('option', { value:'all' }, 'Все условия (AND)'),
                React.createElement('option', { value:'any' }, 'Любое из условий (OR)'),
              )
            ),
            React.createElement(FilterRow, { label:'Статус' },
              React.createElement('select', { className:'select', style:{maxWidth:340}, value:status, onChange:e => { setStatus(e.target.value); setPage(1); } },
                React.createElement('option', { value:'all' }, 'Любой'),
                React.createElement('option', { value:'solved' }, 'Решено'),
                React.createElement('option', { value:'attempted' }, 'В процессе'),
                React.createElement('option', { value:'todo' }, 'Не начато'),
              )
            ),
            React.createElement(FilterRow, { label:'Сложность' },
              React.createElement('div', { className:'wrap' },
                ...data.difficulties.map(d => React.createElement(Chip, {
                  key:d, active: diff === d,
                  onClick: () => { setDiff(diff === d ? 'all' : d); setPage(1); }
                }, d))
              )
            ),
            React.createElement(FilterRow, { label:'Типы' },
              React.createElement('div', { className:'wrap' },
                React.createElement(Chip, { active: type==='all', onClick: ()=>{ setType('all'); setPage(1); } }, 'Все'),
                ...data.taskTypes.slice(0,5).map(t => React.createElement(Chip, {
                  key:t.id, active:type===t.id, onClick:()=>{ setType(t.id); setPage(1); }
                }, t.label))
              )
            ),
            React.createElement(FilterRow, { label:'Конструкции' },
              React.createElement('select', { className:'select', style:{maxWidth:340}, value:patternSel, onChange:e => { setPatternSel(e.target.value); setPage(1); } },
                React.createElement('option', { value:'' }, 'Выберите конструкцию'),
                ...data.patterns.map(p => React.createElement('option', { key:p, value:p }, p))
              )
            ),
            React.createElement('div', { className:'row', style:{justifyContent:'flex-end', gap:10, marginTop:14, paddingTop:14, borderTop:'1px solid var(--border)'} },
              React.createElement('button', { className:'btn btn-ghost', onClick:resetFilters }, 'Сбросить'),
              React.createElement('button', { className:'btn btn-primary', onClick:()=>setFilterOpen(false) }, 'Применить')
            )
            )
          )
        ),

        // Grid: tasks + assignment sets
        React.createElement('div', { style:{display:'grid', gridTemplateColumns:'1fr 290px', gap:18, alignItems:'start'} },
          // task table
          React.createElement('div', { className:'card card-pad' },
            paged.length === 0
              ? React.createElement(EmptyState, {
                  icon:'⌕', title:'Ничего не найдено',
                  text:'Попробуйте сбросить фильтры или поискать что-то другое.',
                  action: React.createElement('button', { className:'btn btn-primary btn-sm', onClick:resetFilters }, 'Сбросить фильтры')
                })
              : React.createElement(React.Fragment, null,
                  React.createElement('table', { className:'table' },
                    React.createElement('thead', null, React.createElement('tr', null,
                      React.createElement('th', { style:{width:38} }),
                      React.createElement('th', null, 'Задача'),
                      React.createElement('th', null, 'Тип'),
                      React.createElement('th', null, 'Язык'),
                      React.createElement('th', null, 'Сложность'),
                      React.createElement('th', null, 'Статус'),
                    )),
                    React.createElement('tbody', null,
                      paged.map(t => React.createElement('tr', { key:t.id, onClick:()=>navigate(`/tasks/${t.id}`) },
                        React.createElement('td', null, React.createElement(TaskStatusDot, { status:t.status })),
                        React.createElement('td', { className:'t-name' }, t.title),
                        React.createElement('td', { className:'muted' }, data.taskTypes.find(x=>x.id===t.type)?.label || t.type),
                        React.createElement('td', { className:'muted' }, t.lang),
                        React.createElement('td', null, React.createElement(DiffBadge, { diff:t.diff })),
                        React.createElement('td', null, React.createElement(StatusBadge, { status:t.status })),
                      ))
                    )
                  ),
                  React.createElement('div', { className:'between', style:{marginTop:16} },
                    React.createElement('span', { className:'mut3', style:{fontSize:13} }, `${(page-1)*pageSize+1}–${Math.min(page*pageSize, filtered.length)} из ${filtered.length}`),
                    React.createElement(Pagination, { page, pageCount, onChange:setPage })
                  ),
                )
          ),
          // assignment sets
          React.createElement('aside', { className:'card card-pad' },
            React.createElement('div', { className:'between', style:{marginBottom:14} },
              React.createElement('b', { style:{fontSize:15} }, 'Сборники'),
              React.createElement(Badge, { kind:'purple' }, sets.length)
            ),
            React.createElement('div', { className:'grid', style:{gap:10} },
              sets.map(s => React.createElement(AssignmentSetCard, { key:s.id, set:s, onOpen:()=>{
                setSearch(''); setPage(1); toast.push({kind:'info', title:'Открыт сборник', body:s.name});
              } })),
              React.createElement('button', {
                onClick:()=>setInviteOpen(true),
                style:{border:'1px dashed var(--border-2)', background:'transparent', borderRadius:12, padding:13, cursor:'pointer', color:'var(--text-2)', fontSize:13}
              }, '+ Ввести инвайт-код')
            )
          )
        )
      )
    ),
    React.createElement(Modal, {
      open:inviteOpen, onClose:()=>setInviteOpen(false), title:'Вступить в сборник',
      footer: React.createElement(React.Fragment, null,
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setInviteOpen(false) }, 'Отмена'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:joinSet }, 'Вступить'),
      )
    },
      React.createElement('p', { className:'muted', style:{fontSize:14, margin:'0 0 14px'} }, 'Введите инвайт-код от преподавателя, чтобы получить доступ к назначенным задачам.'),
      React.createElement('input', { className:'input mono', placeholder:'GRP-XXXX', value:inviteCode, onChange:e=>setInviteCode(e.target.value.toUpperCase()), autoFocus:true })
    ),
  );
}

function Chip({ active, pp, sm, onClick, children }) {
  return React.createElement('span', {
    className: `chip ${active?'on':''} ${active&&pp?'pp':''} ${sm?'sm':''}`,
    onClick, role:'button', tabIndex:0
  }, children);
}
function FilterRow({ label, children }) {
  return React.createElement('div', { className:'filter-row' },
    React.createElement('label', null, label),
    React.createElement('div', null, children)
  );
}
function Divider() { return React.createElement('span', { style:{width:1, height:24, background:'var(--border)', margin:'0 4px'} }); }
function TaskStatusDot({ status }) {
  if (status === 'solved') return React.createElement('span', { className:'badge badge-lime btn-icon', style:{width:24,height:24,padding:0,justifyContent:'center',borderRadius:'50%'} }, '✓');
  if (status === 'attempted') return React.createElement('span', { style:{display:'inline-block',width:24,height:24,borderRadius:'50%',border:'2px solid var(--purple)'} });
  return React.createElement('span', { style:{display:'inline-block',width:24,height:24,borderRadius:'50%',border:'2px dashed var(--border-2)'} });
}
function Pagination({ page, pageCount, onChange }) {
  const pages = [];
  const max = Math.min(pageCount, 5);
  for (let i = 1; i <= max; i++) pages.push(i);
  return React.createElement('div', { className:'pagination' },
    React.createElement('button', { onClick:()=>onChange(Math.max(1,page-1)), disabled:page===1 }, '‹'),
    pages.map(p => React.createElement('button', { key:p, className: p===page?'on':'', onClick:()=>onChange(p) }, p)),
    pageCount > 5 && React.createElement('span', { className:'mut3', style:{padding:'0 8px'} }, '…'),
    React.createElement('button', { onClick:()=>onChange(Math.min(pageCount,page+1)), disabled:page===pageCount }, '›'),
  );
}
function AssignmentSetCard({ set, onOpen }) {
  const pct = Math.round((set.solved / set.total) * 100);
  const pp = set.color === 'purple';
  return React.createElement('div', {
    onClick:onOpen, style:{border:'1px solid var(--border)', borderRadius:12, padding:13, cursor:'pointer', transition:'.12s'},
    onMouseEnter:e=>e.currentTarget.style.borderColor='var(--lime)',
    onMouseLeave:e=>e.currentTarget.style.borderColor='var(--border)',
  },
    React.createElement('div', { className:'between' },
      React.createElement('b', { style:{fontSize:13.5} }, set.name),
      React.createElement(Badge, { kind: pp?'purple':'lime' }, `${set.solved}/${set.total}`),
    ),
    React.createElement('div', { className:'progress '+(pp?'pp':''), style:{marginTop:10} }, React.createElement('i', { style:{width:`${pct}%`} }))
  );
}

/* =========================================================
   TASK PAGE  ( /tasks/:id )
   ========================================================= */
function TaskPage({ id }) {
  const { navigate } = useRouter();
  const toast = useToast();
  const data = window.MOCK;
  const task = data.tasks.find(t => t.id === +id) || data.tasks[0];

  const [lang, setLang] = useState(task.lang === '—' ? 'Python' : task.lang);
  const [editorMode, setEditorMode] = useState(() => {
    if (task.type === 'blocks') return 'flow';
    if (task.type === 'code_assembly' || task.type === 'block_reorder' || task.type === 'task_build_from_blocks') return 'blocks';
    return 'code';
  });
  const [code, setCode] = useState(data.codeSample[task.lang === '—' ? 'Python' : task.lang] || data.codeSample.Python);
  const [tab, setTab] = useState('task');
  const [bottomTab, setBottomTab] = useState('tests');
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(initialResults());

  function initialResults() {
    // 11/12 passed, test 4 fails
    return Array.from({length:12}, (_,i) => ({ idx:i+1, pass: i !== 3 }));
  }

  // drafts in localStorage
  useEffect(() => {
    const key = `tp_draft_${task.id}_${lang}`;
    const saved = localStorage.getItem(key);
    if (saved) setCode(saved);
    else setCode(data.codeSample[lang] || data.codeSample.Python);
  }, [task.id, lang]);
  useEffect(() => {
    const key = `tp_draft_${task.id}_${lang}`;
    const t = setTimeout(() => localStorage.setItem(key, code), 500);
    return () => clearTimeout(t);
  }, [code, task.id, lang]);

  const run = () => {
    setRunning(true);
    setBottomTab('tests');
    setTimeout(() => {
      const passN = 10 + Math.floor(Math.random()*3);
      const arr = Array.from({length:12}, (_,i) => ({ idx:i+1, pass: i < passN }));
      // shuffle a single fail position
      if (passN < 12) {
        const failIdx = passN + Math.floor(Math.random() * (12 - passN));
        arr.forEach((x,i) => { x.pass = i !== failIdx; });
        // ensure at least passN pass (close enough for demo)
      }
      setResults(arr);
      setRunning(false);
      const allPass = arr.every(x => x.pass);
      if (allPass) toast.push({ kind:'lime', title:'Решение принято!', body:'Все тесты пройдены.' });
      else toast.push({ kind:'err', title:'Не все тесты пройдены', body:`${arr.filter(x=>x.pass).length}/${arr.length}` });
    }, 900);
  };

  const reset = () => {
    setCode(data.codeSample[lang] || data.codeSample.Python);
    localStorage.removeItem(`tp_draft_${task.id}_${lang}`);
    toast.push({ kind:'info', title:'Код сброшен' });
  };

  const idx = data.tasks.findIndex(t => t.id === task.id);
  const goPrev = () => { if (idx > 0) navigate(`/tasks/${data.tasks[idx-1].id}`); };
  const goNext = () => { if (idx < data.tasks.length-1) navigate(`/tasks/${data.tasks[idx+1].id}`); };

  const passed = results.filter(r => r.pass).length;
  const failedTest = results.find(r => !r.pass);

  return React.createElement('div', { style:{minHeight:'100vh', display:'flex', flexDirection:'column'} },
    React.createElement('div', { className:'topbar', style:{padding:'12px 20px'} },
      React.createElement('div', { className:'row' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>navigate('/') }, '← Каталог'),
        React.createElement('div', { className:'crumb' }, task.catalog || 'Задачи', ' / ', React.createElement('b', null, task.title)),
        React.createElement(DiffBadge, { diff:task.diff }),
        task.lang !== '—' && React.createElement(Badge, { kind:'purple' }, task.lang),
      ),
      React.createElement('div', { className:'row' },
        React.createElement('span', { className:'muted', style:{fontSize:13} }, `Задача ${idx+1} из ${data.tasks.length}`),
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:goPrev, disabled:idx===0 }, '← Предыдущая'),
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:goNext, disabled:idx===data.tasks.length-1 }, 'Следующая →'),
        React.createElement(UserMenu, null)
      )
    ),
    React.createElement('div', { className:'task-split', style:{flex:1} },
      // LEFT panel
      React.createElement('div', { className:'task-left' },
        React.createElement('div', { className:'tabbar', style:{marginBottom:14} },
          React.createElement('button', { className: tab==='task'?'on':'', onClick:()=>setTab('task') }, 'Условие'),
          React.createElement('button', { className: tab==='examples'?'on':'', onClick:()=>setTab('examples') }, 'Примеры'),
          React.createElement('button', { className: tab==='flow'?'on':'', onClick:()=>setTab('flow') }, 'Подсказки'),
          React.createElement('button', { className: tab==='reference'?'on':'', onClick:()=>setTab('reference') }, 'Эталон'),
        ),
        tab === 'task' && React.createElement(React.Fragment, null,
          React.createElement('h2', { style:{fontSize:20, fontWeight:800, margin:'0 0 12px'} }, task.title),
          React.createElement('p', { className:'muted', style:{fontSize:14, margin:'0 0 16px'} }, task.desc),
          task.complexity !== '—' && React.createElement('p', { style:{fontSize:13.5, margin:'0 0 16px'} }, 'Сложность — ', React.createElement('b', null, task.complexity)),
          React.createElement('div', { className:'eyebrow' }, 'Ограничения'),
          React.createElement('ul', { className:'muted', style:{fontSize:13.5, margin:0, paddingLeft:18, lineHeight:1.9} },
            React.createElement('li', null, '1 ≤ n ≤ 10⁵'),
            React.createElement('li', null, 'массив отсортирован по возрастанию'),
            React.createElement('li', null, '−10⁹ ≤ arr[i] ≤ 10⁹'),
          ),
          React.createElement('div', { className:'eyebrow' }, 'Паттерн'),
          React.createElement('div', { className:'wrap' }, React.createElement(Badge, { kind:'purple' }, task.pattern)),
        ),
        tab === 'examples' && React.createElement('div', null,
          React.createElement('div', { className:'eyebrow', style:{marginTop:0} }, 'Пример 1'),
          React.createElement('div', { className:'editor' },
            React.createElement('div', { className:'body' },
              React.createElement('div', { className:'ln' }, React.createElement('span',{className:'n'},'›'), React.createElement('span',{className:'cm'},'Вход:  '), React.createElement('span',{className:'nm2'},'arr=[1,3,5,7,9], x=5')),
              React.createElement('div', { className:'ln' }, React.createElement('span',{className:'n'},'›'), React.createElement('span',{className:'cm'},'Выход:'), React.createElement('span',{className:'fn'},' 2'))
            )
          ),
          React.createElement('div', { className:'eyebrow' }, 'Пример 2'),
          React.createElement('div', { className:'editor' },
            React.createElement('div', { className:'body' },
              React.createElement('div', { className:'ln' }, React.createElement('span',{className:'n'},'›'), React.createElement('span',{className:'cm'},'Вход:  '), React.createElement('span',{className:'nm2'},'arr=[2,4,6,8], x=7')),
              React.createElement('div', { className:'ln' }, React.createElement('span',{className:'n'},'›'), React.createElement('span',{className:'cm'},'Выход:'), React.createElement('span',{className:'fn'},' -1'))
            )
          ),
        ),
        tab === 'flow' && React.createElement('div', null,
          React.createElement('div', { className:'note' },
            React.createElement('b', null, 'Подсказка: '), 'Думайте о массиве как о диапазоне, который вы сужаете вдвое на каждой итерации.'
          ),
          React.createElement('div', { className:'note', style:{marginTop:10, background:'transparent', borderStyle:'dashed'} },
            'Учитывайте граничный случай: пустой массив должен вернуть −1.'
          )
        ),
        tab === 'reference' && React.createElement('div', null,
          React.createElement('div', { className:'eyebrow', style:{marginTop:0} }, 'Эталонное решение'),
          React.createElement('p', { className:'muted', style:{fontSize:13, margin:'0 0 12px'} },
            'Полностью рабочая реализация. Используйте её как ориентир, но решайте задачу самостоятельно — это лучший способ научиться.'
          ),
          React.createElement('div', { className:'ref-snippet' },
            React.createElement('div', { className:'ref-snippet-h' },
              React.createElement('span', null, `solution.${ext(lang)} · ${lang}`),
              React.createElement('span', null, 'read-only')
            ),
            React.createElement('pre', null, data.codeSample[lang] || data.codeSample.Python)
          ),
          React.createElement('div', { className:'note warn', style:{marginTop:12, fontSize:12.5} },
            React.createElement('b', null, 'Совет: '), 'Закройте эту вкладку и попробуйте сначала — если застряли, посмотрите подсказку и только потом эталон.'
          )
        )
      ),
      // RIGHT panel — editor or blocks
      React.createElement('div', { className:'task-right' },
        React.createElement('div', { className:'row', style:{gap:6, padding:'12px 16px', borderBottom:'1px solid var(--border)', background:'#0c111a'} },
          React.createElement(Chip, { sm:true, active:editorMode==='code', onClick:()=>setEditorMode('code') }, 'Код (Monaco)'),
          React.createElement(Chip, { sm:true, active:editorMode==='blocks', onClick:()=>setEditorMode('blocks') }, 'Блоки'),
          React.createElement(Chip, { sm:true, active:editorMode==='flow', onClick:()=>setEditorMode('flow') }, 'Блок-схема'),
          React.createElement('select', {
            className:'select',
            style:{marginLeft:'auto', width:130, height:30, padding:'4px 12px', fontSize:12.5},
            value:lang, onChange:e=>setLang(e.target.value)
          },
            data.languages.slice(0,3).map(l => React.createElement('option', { key:l, value:l }, l))
          )
        ),
        editorMode === 'code' && React.createElement(CodeEditor, { code, setCode, lang }),
        editorMode === 'blocks' && React.createElement(BlockAssemblyEditor, null),
        editorMode === 'flow' && React.createElement(FlowEditor, null),

        React.createElement('div', { className:'between', style:{padding:'12px 16px', borderTop:'1px solid var(--border)', background:'#0c111a'} },
          React.createElement('span', { className:'muted', style:{fontSize:13} }, 'Автосохранение · только что'),
          React.createElement('div', { className:'row' },
            React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:reset }, 'Сбросить'),
            React.createElement('button', { className:'btn btn-primary', onClick:run, disabled:running },
              running ? React.createElement(React.Fragment, null, React.createElement('span', { className:'spinner', style:{width:14,height:14,borderWidth:2} }), ' Запуск…')
                      : '▸ Запуск'
            )
          )
        ),
        // Bottom: TestPanel
        React.createElement('div', { style:{borderTop:'1px solid var(--border)', background:'var(--surface)'} },
          React.createElement('div', { className:'tabbar', style:{margin:'0 16px'} },
            React.createElement('button', { className: bottomTab==='tests'?'on':'', onClick:()=>setBottomTab('tests') }, 'Тесты'),
            React.createElement('button', { className: bottomTab==='output'?'on':'', onClick:()=>setBottomTab('output') }, 'Вывод'),
            React.createElement('button', { className: bottomTab==='errors'?'on':'', onClick:()=>setBottomTab('errors') }, 'Ошибки'),
          ),
          React.createElement('div', { style:{padding:'4px 16px 16px'} },
            bottomTab === 'tests' && React.createElement(React.Fragment, null,
              React.createElement('div', { className:'between', style:{marginBottom:10} },
                React.createElement('b', { style:{fontSize:13.5} }, 'Тесты'),
                React.createElement(Badge, { kind: passed===results.length?'lime':'warn' }, React.createElement(Dot), `${passed} / ${results.length} пройдено`),
              ),
              React.createElement('div', { className:'wrap', style:{gap:6} },
                results.map(r => React.createElement('span', {
                  key:r.idx,
                  className:`badge ${r.pass?'badge-lime':'badge-danger'}`,
                  style:{width:26,height:26,padding:0,justifyContent:'center',borderRadius:8}
                }, r.idx))
              ),
              failedTest && React.createElement('div', { className:'toast err', style:{marginTop:12, maxWidth:'none'} },
                React.createElement('span', { style:{color:'var(--danger)', fontWeight:800} }, '!'),
                React.createElement('div', null,
                  React.createElement('div', { className:'tt', style:{fontSize:13} }, `Тест №${failedTest.idx} не пройден`),
                  React.createElement('div', { className:'tx', style:{fontSize:12.5} }, 'arr=[2,4,6,8], x=8 → ожидалось 3, получено −1')
                )
              )
            ),
            bottomTab === 'output' && React.createElement('div', { className:'mono', style:{padding:'10px 0', color:'var(--text-2)', fontSize:13} },
              '> python solution.py', React.createElement('br'),
              '✓ test 1 passed (0.003s)', React.createElement('br'),
              '✓ test 2 passed (0.002s)', React.createElement('br'),
              React.createElement('span', { className:'fn' }, 'Process exited with code 0')
            ),
            bottomTab === 'errors' && (failedTest
              ? React.createElement('pre', { className:'mono', style:{margin:0, padding:'10px 0', color:'#ff8198', fontSize:12.5} },
                `AssertionError on test #${failedTest.idx}\n  expected: 3\n  received: -1\n  input: arr=[2,4,6,8], x=8`)
              : React.createElement('p', { className:'muted', style:{fontSize:13, margin:'10px 0'} }, 'Ошибок нет.')
            )
          )
        )
      )
    )
  );
}

function CodeEditor({ code, setCode, lang }) {
  const taRef = useRef(null);
  return React.createElement('div', { className:'editor', style:{borderRadius:0, border:0, flex:1, minHeight:280} },
    React.createElement('div', { className:'eh' },
      React.createElement('span', { className:'t' }, `solution.${ext(lang)}`),
      React.createElement('span', { className:'mut3', style:{fontSize:11, marginLeft:'auto', fontFamily:'var(--mono)'} }, `UTF-8 · ${lang}`),
    ),
    React.createElement('textarea', {
      ref: taRef,
      value: code,
      onChange: e => setCode(e.target.value),
      spellCheck: false,
      style: { minHeight:280 }
    })
  );
}
function ext(lang) { return lang==='Python'?'py':lang==='JavaScript'?'js':lang==='C++'?'cpp':'txt'; }

function BlockAssemblyEditor() {
  // Build bank of code tokens (real solution tokens + distractors), shuffled.
  // The solution area is a list of LINES, each line holds an ordered sequence of token ids.
  // Indentation is per-line (number of 4-space steps). Whitespace between tokens is rendered.
  const initialBank = useMemo(() => {
    const real = [
      { id:'t1', text:'def' },
      { id:'t2', text:'factorial' },
      { id:'t3', text:'(n):' },
      { id:'t4', text:'if' },
      { id:'t5', text:'n <= 1' },
      { id:'t6', text:':' },
      { id:'t7', text:'return' },
      { id:'t8', text:'1' },
      { id:'t9', text:'return' },
      { id:'t10', text:'n' },
      { id:'t11', text:'*' },
      { id:'t12', text:'factorial(n - 1)' },
      { id:'d1', text:'break', distractor:true },
      { id:'d2', text:'n + 1', distractor:true },
      { id:'d3', text:'while', distractor:true },
    ];
    // shuffle copy
    const a = [...real];
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; }
    return a;
  }, []);

  const [tokens] = useState(initialBank);
  const tokenMap = useMemo(() => Object.fromEntries(tokens.map(t => [t.id, t])), [tokens]);
  const [bank, setBank]   = useState(() => tokens.map(t => t.id));
  const [lines, setLines] = useState([{ id:'L1', indent:0, tokens:[] }]);
  const [hoverLine, setHoverLine] = useState(null);

  // ---- DnD ----
  const onDragStart = (e, payload) => {
    e.dataTransfer.setData('text/plain', JSON.stringify(payload));
    e.dataTransfer.effectAllowed = 'move';
    setTimeout(() => e.target.classList.add('dragging'), 0);
  };
  const onDragEnd = (e) => e.target.classList.remove('dragging');
  const allow = (e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; };

  const getPayload = (e) => { try { return JSON.parse(e.dataTransfer.getData('text/plain')); } catch { return null; } };

  // Remove a token from wherever it currently is (line or bank).
  const detach = (tokenId, draft) => {
    draft.bank = draft.bank.filter(id => id !== tokenId);
    draft.lines = draft.lines.map(l => l.tokens.includes(tokenId) ? {...l, tokens: l.tokens.filter(id => id !== tokenId)} : l);
  };

  const dropOnLine = (lineId, beforeIndex) => (e) => {
    e.preventDefault(); e.stopPropagation();
    setHoverLine(null);
    const p = getPayload(e); if (!p) return;
    setBank(b => { setLines(ls => {
      const draft = { bank:[...b], lines: ls.map(l => ({...l, tokens:[...l.tokens]})) };
      detach(p.id, draft);
      const li = draft.lines.findIndex(l => l.id === lineId); if (li < 0) return ls;
      const insertAt = beforeIndex == null ? draft.lines[li].tokens.length : beforeIndex;
      draft.lines[li].tokens.splice(insertAt, 0, p.id);
      setBank(draft.bank);
      return draft.lines;
    }); return b; });
  };

  const dropOnBank = (e) => {
    e.preventDefault();
    const p = getPayload(e); if (!p) return;
    setBank(b => { setLines(ls => {
      const draft = { bank:[...b], lines: ls.map(l => ({...l, tokens:[...l.tokens]})) };
      detach(p.id, draft);
      if (!draft.bank.includes(p.id)) draft.bank.push(p.id);
      setBank(draft.bank);
      return draft.lines;
    }); return b; });
  };

  const removeToken = (tokenId) => {
    setLines(ls => ls.map(l => ({...l, tokens: l.tokens.filter(id => id !== tokenId)})));
    setBank(b => b.includes(tokenId) ? b : [...b, tokenId]);
  };

  // ---- Lines ----
  const addLine = () => setLines(ls => [...ls, { id:'L'+Date.now(), indent:0, tokens:[] }]);
  const removeLine = (lineId) => setLines(ls => {
    if (ls.length === 1) return ls.map(l => ({...l, tokens:[], indent:0}));
    const line = ls.find(l => l.id === lineId); if (line) line.tokens.forEach(removeToken);
    return ls.filter(l => l.id !== lineId);
  });
  const indent = (lineId, dir) => setLines(ls => ls.map(l => l.id===lineId ? {...l, indent: Math.max(0, Math.min(6, l.indent + dir))} : l));
  const clearAll = () => { setLines([{ id:'L1', indent:0, tokens:[] }]); setBank(tokens.map(t => t.id)); };

  return React.createElement('div', { className:'asm-shell' },
    React.createElement('div', { className:'asm-toolbar' },
      React.createElement('span', { className:'mut3 small', style:{textTransform:'uppercase', letterSpacing:'.06em', fontWeight:700, fontFamily:'var(--mono)'} }, 'Сборка'),
      React.createElement('button', { className:'btn btn-ghost btn-xs', onClick:addLine }, '+ Строка'),
      React.createElement('button', { className:'btn btn-ghost btn-xs', onClick:clearAll }, 'Очистить'),
      React.createElement('span', { className:'hint' }, 'Перетаскивайте блоки. Несколько блоков в одной строке — через пробел.')
    ),
    React.createElement('div', { className:'asm-solution', onDragOver:allow },
      lines.map((line, lineIdx) => React.createElement('div', {
        key: line.id,
        className: 'asm-line ' + (hoverLine===line.id?'over':''),
        onDragOver: (e) => { e.preventDefault(); setHoverLine(line.id); },
        onDragLeave: () => setHoverLine(null),
        onDrop: dropOnLine(line.id, null)
      },
        React.createElement('span', { className:'lnum' }, lineIdx+1),
        // indent visual
        line.indent > 0 && React.createElement('span', { className:'fixed' }, '    '.repeat(line.indent)),
        // tokens
        line.tokens.length === 0
          ? React.createElement('span', { className:'empty' }, '(пусто — перетащите сюда)')
          : line.tokens.map((tid, ti) => {
              const tk = tokenMap[tid];
              return React.createElement(React.Fragment, { key:tid },
                React.createElement('span', {
                  className:'asm-block placed',
                  draggable:true,
                  onDragStart:(e)=>onDragStart(e, { id:tid }),
                  onDragEnd,
                  onClick:()=>removeToken(tid),
                  title:'Клик — вернуть в банк'
                }, tk.text),
                ti < line.tokens.length - 1 && React.createElement('span', { className:'fixed' }, ' ')
              );
            }),
        React.createElement('div', { className:'asm-line-actions' },
          React.createElement('button', { className:'ind-ctrl', onClick:()=>indent(line.id, -1), title:'← Отступ' }, '←'),
          React.createElement('button', { className:'ind-ctrl', onClick:()=>indent(line.id, +1), title:'Отступ →' }, '→'),
          React.createElement('button', { className:'ind-ctrl', onClick:()=>removeLine(line.id), title:'Удалить строку', style:{color:'#ff8198'} }, '✕')
        )
      ))
    ),
    React.createElement('div', { className:'asm-bank', onDragOver:allow, onDrop:dropOnBank },
      bank.length === 0
        ? React.createElement('span', { className:'mut3 small', style:{margin:'auto'} }, 'Банк пуст — все блоки расставлены')
        : bank.map(id => {
            const tk = tokenMap[id];
            return React.createElement('span', {
              key:id, className:'asm-block', draggable:true,
              onDragStart:(e)=>onDragStart(e, { id }), onDragEnd,
              title: tk.distractor ? 'дистрактор' : 'блок'
            }, tk.text);
          })
    )
  );
}

/* ===== Flowchart editor (React Flow-style) ===== */
const FLOW_NODE_TYPES = {
  start:    { label:'Начало',  w:130, h:48 },
  input:    { label:'Ввод',    w:170, h:50 },
  process:  { label:'Действие',w:170, h:56 },
  decision: { label:'Условие', w:170, h:110 },
  loop:     { label:'Цикл',    w:170, h:54 },
  output:   { label:'Вывод',   w:170, h:50 },
  end:      { label:'Конец',   w:130, h:48 },
};

function FlowEditor() {
  const [nodes, setNodes] = useState([
    { id:1, type:'start', x:240, y:40,  label:'Начало' },
    { id:2, type:'input', x:240, y:130, label:'Ввести n' },
  ]);
  const [edges, setEdges] = useState([
    { id:'e1', from:1, fromPort:'bottom', to:2, toPort:'top' },
  ]);
  const [nextId, setNextId] = useState(3);
  const [selected, setSelected] = useState(null); // { kind:'node'|'edge', id }
  const [connecting, setConnecting] = useState(null); // { fromNode, fromPort }
  const [editing, setEditing] = useState(null); // node id while editing label
  const [editText, setEditText] = useState('');
  const canvasRef = useRef(null);
  const dragRef = useRef(null); // { id, dx, dy } during node drag
  const [, force] = useState(0); // for redraw after drag

  // ---- Palette drop ----
  const onPaletteDragStart = (e, type) => { e.dataTransfer.setData('flow/type', type); e.dataTransfer.effectAllowed='copy'; };
  const onCanvasDragOver = (e) => { if (e.dataTransfer.types.includes('flow/type')) { e.preventDefault(); e.dataTransfer.dropEffect='copy'; e.currentTarget.classList.add('dragover'); } };
  const onCanvasDragLeave = (e) => e.currentTarget.classList.remove('dragover');
  const onCanvasDrop = (e) => {
    e.preventDefault(); e.currentTarget.classList.remove('dragover');
    const type = e.dataTransfer.getData('flow/type'); if (!type || !FLOW_NODE_TYPES[type]) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const def = FLOW_NODE_TYPES[type];
    const x = e.clientX - rect.left - def.w/2;
    const y = e.clientY - rect.top  - def.h/2;
    const id = nextId; setNextId(n => n+1);
    setNodes(ns => [...ns, { id, type, x:Math.max(8,x), y:Math.max(8,y), label: def.label }]);
  };

  // ---- Node move (mouse) ----
  useEffect(() => {
    const onMove = (e) => {
      const d = dragRef.current; if (!d) return;
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left - d.dx;
      const y = e.clientY - rect.top  - d.dy;
      setNodes(ns => ns.map(n => n.id===d.id ? {...n, x:Math.max(0,x), y:Math.max(0,y)} : n));
    };
    const onUp = () => { dragRef.current = null; };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    return () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); };
  }, []);

  const onNodeMouseDown = (e, n) => {
    if (e.target.classList.contains('flow-port')) return; // don't drag when clicking port
    const rect = canvasRef.current.getBoundingClientRect();
    dragRef.current = { id:n.id, dx: e.clientX - rect.left - n.x, dy: e.clientY - rect.top - n.y };
    setSelected({ kind:'node', id:n.id });
    e.preventDefault();
  };

  // ---- Connections ----
  const onPortClick = (e, nodeId, port) => {
    e.stopPropagation();
    if (!connecting) {
      setConnecting({ fromNode:nodeId, fromPort:port });
      return;
    }
    if (connecting.fromNode === nodeId) { setConnecting(null); return; }
    const id = 'e' + Date.now();
    setEdges(es => [...es, { id, from:connecting.fromNode, fromPort:connecting.fromPort, to:nodeId, toPort:port }]);
    setConnecting(null);
  };

  // ---- Selection / Delete ----
  useEffect(() => {
    const onKey = (e) => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
      if ((e.key === 'Delete' || e.key === 'Backspace') && selected) {
        if (selected.kind === 'node') {
          setNodes(ns => ns.filter(n => n.id !== selected.id));
          setEdges(es => es.filter(ed => ed.from !== selected.id && ed.to !== selected.id));
        } else {
          setEdges(es => es.filter(ed => ed.id !== selected.id));
        }
        setSelected(null);
      }
      if (e.key === 'Escape') { setConnecting(null); setEditing(null); }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [selected]);

  // ---- Label editing ----
  const startEdit = (n) => { setEditing(n.id); setEditText(n.label); };
  const commitEdit = () => {
    setNodes(ns => ns.map(n => n.id===editing ? {...n, label: editText} : n));
    setEditing(null);
  };

  // ---- Edge geometry ----
  const portPos = (n, port) => {
    const def = FLOW_NODE_TYPES[n.type];
    if (port === 'top')    return { x: n.x + def.w/2, y: n.y, dx:0, dy:-1 };
    if (port === 'bottom') return { x: n.x + def.w/2, y: n.y + def.h, dx:0, dy:1 };
    if (port === 'left')   return { x: n.x, y: n.y + def.h/2, dx:-1, dy:0 };
    if (port === 'right')  return { x: n.x + def.w, y: n.y + def.h/2, dx:1, dy:0 };
    return { x: n.x, y: n.y, dx:0, dy:0 };
  };
  const edgePath = (a, b) => {
    const d = Math.max(40, Math.hypot(b.x-a.x, b.y-a.y) * 0.4);
    const c1 = { x: a.x + a.dx * d, y: a.y + a.dy * d };
    const c2 = { x: b.x + b.dx * d, y: b.y + b.dy * d };
    return `M ${a.x} ${a.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${b.x} ${b.y}`;
  };

  const clearAll = () => { setNodes([]); setEdges([]); setSelected(null); setConnecting(null); };

  return React.createElement('div', { className:'flow-shell' },
    // Sidebar palette
    React.createElement('div', { className:'flow-side' },
      React.createElement('div', { className:'sec' }, 'Перетащите'),
      ...Object.entries(FLOW_NODE_TYPES).map(([type, def]) => React.createElement('div', {
        key:type, className:`flow-drag ${type}`,
        draggable:true, onDragStart:(e)=>onPaletteDragStart(e, type)
      },
        React.createElement('span', { className:'ico' }),
        def.label
      )),
      React.createElement('div', { className:'sec', style:{marginTop:14} }, 'Подсказка'),
      React.createElement('p', { className:'mut3 small', style:{margin:'0 4px', lineHeight:1.45} },
        '• Перетащите узлы из этой панели', React.createElement('br'),
        '• Клик по точке на узле — начало стрелки', React.createElement('br'),
        '• Клик по точке другого узла — конец', React.createElement('br'),
        '• Двойной клик — переименовать', React.createElement('br'),
        '• Delete — удалить'
      )
    ),
    // Canvas
    React.createElement('div', { className:'flow-canvas-wrap' },
      React.createElement('div', {
        ref:canvasRef, className:'flow-canvas',
        onDragOver:onCanvasDragOver, onDragLeave:onCanvasDragLeave, onDrop:onCanvasDrop,
        onClick:()=>{ setSelected(null); setConnecting(null); }
      },
        // SVG edges
        React.createElement('svg', { className:'flow-svg', xmlns:'http://www.w3.org/2000/svg' },
          React.createElement('defs', null,
            React.createElement('marker', { id:'arrow', viewBox:'0 0 10 10', refX:'9', refY:'5', markerWidth:'8', markerHeight:'8', orient:'auto-start-reverse' },
              React.createElement('path', { d:'M 0 0 L 10 5 L 0 10 z', className:'arrowhead' })
            ),
            React.createElement('marker', { id:'arrow-lime', viewBox:'0 0 10 10', refX:'9', refY:'5', markerWidth:'8', markerHeight:'8', orient:'auto-start-reverse' },
              React.createElement('path', { d:'M 0 0 L 10 5 L 0 10 z', style:{fill:'var(--lime)'} })
            )
          ),
          edges.map(ed => {
            const fn = nodes.find(n => n.id === ed.from); const tn = nodes.find(n => n.id === ed.to);
            if (!fn || !tn) return null;
            const a = portPos(fn, ed.fromPort); const b = portPos(tn, ed.toPort);
            const isSel = selected && selected.kind === 'edge' && selected.id === ed.id;
            return React.createElement('path', {
              key:ed.id, d:edgePath(a, b),
              markerEnd: `url(#${isSel?'arrow-lime':'arrow'})`,
              style: isSel ? { stroke:'var(--lime)', strokeWidth:2 } : null,
              onClick:(e)=>{ e.stopPropagation(); setSelected({ kind:'edge', id:ed.id }); }
            });
          })
        ),
        // Nodes
        nodes.map(n => {
          const def = FLOW_NODE_TYPES[n.type];
          const isSel = selected && selected.kind === 'node' && selected.id === n.id;
          const hasShape = ['decision','input','output','loop'].includes(n.type);
          return React.createElement('div', {
            key:n.id,
            className:`flow-node ${n.type} ${isSel?'selected':''}`,
            style:{ left:n.x, top:n.y, width:def.w, height:def.h },
            onMouseDown:(e)=>onNodeMouseDown(e, n),
            onDoubleClick:(e)=>{ e.stopPropagation(); startEdit(n); },
            onClick:(e)=>{ e.stopPropagation(); setSelected({ kind:'node', id:n.id }); }
          },
            hasShape && React.createElement('div', { className:'shape' }),
            editing === n.id
              ? null
              : React.createElement('div', { className:'lbl' }, n.label),
            // ports
            ['top','right','bottom','left'].map(port => React.createElement('span', {
              key:port,
              className: `flow-port ${port} ${connecting && connecting.fromNode===n.id && connecting.fromPort===port ? 'active' : ''}`,
              onMouseDown:(e)=>e.stopPropagation(),
              onClick:(e)=>onPortClick(e, n.id, port)
            }))
          );
        }),
        // Editing overlay
        editing && (() => {
          const n = nodes.find(x => x.id === editing); if (!n) return null;
          const def = FLOW_NODE_TYPES[n.type];
          return React.createElement('div', {
            className:'flow-edit-overlay',
            style:{ left: n.x + def.w/2 - 120, top: n.y + def.h + 8 }
          },
            React.createElement('input', {
              value:editText, autoFocus:true,
              onChange:e=>setEditText(e.target.value),
              onKeyDown:e=>{ if (e.key==='Enter') commitEdit(); if (e.key==='Escape') setEditing(null); }
            }),
            React.createElement('button', { className:'btn btn-primary btn-xs', onMouseDown:(e)=>e.preventDefault(), onClick:commitEdit }, '✓')
          );
        })(),
        // Toolbar
        React.createElement('div', { className:'flow-toolbar' },
          React.createElement('button', { onClick:(e)=>{ e.stopPropagation(); setConnecting(null); } }, 'Отмена связи'),
          React.createElement('button', { onClick:(e)=>{ e.stopPropagation(); clearAll(); } }, 'Очистить'),
        ),
        // Status line
        connecting && React.createElement('div', { style:{position:'absolute', left:12, bottom:12, padding:'6px 12px', background:'var(--surface)', border:'1px solid var(--lime)', borderRadius:8, fontSize:12, color:'var(--lime)', zIndex:6, fontFamily:'var(--mono)'} },
          '→ выберите конечную точку (Esc — отмена)')
      )
    )
  );
}

/* =========================================================
   STUDENT PROFILE  ( /student/profile )
   ========================================================= */
function StudentProfilePage() {
  const { user } = useAuth();
  const { query, navigate } = useRouter();
  const initialTab = query.tab && ['progress','solutions','groups'].includes(query.tab) ? query.tab : 'progress';
  const [tab, setTab] = useState(initialTab);
  useEffect(() => { setTab(initialTab); }, [initialTab]);
  const data = window.MOCK;

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: studentSidebarItems(), role:'STUDENT' }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Тренажёр', crumbCurrent:'Профиль' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, { title:'Мой профиль', subtitle:'Прогресс, история решений и группы.' }),
        React.createElement('div', { style:{display:'grid', gridTemplateColumns:'260px 1fr', gap:20, alignItems:'start'} },
          // Sidebar card
          React.createElement('aside', { className:'card card-pad glow-card', style:{textAlign:'center'} },
            React.createElement('div', { className:'avatar lg', style:{margin:'0 auto 12px'} }, (user?.initials || 'В')),
            React.createElement('b', { style:{fontSize:17} }, user?.name || 'Влада Максимова'),
            React.createElement('p', { className:'mut3', style:{fontSize:13, margin:'4px 0 14px'} }, '@vlada · Студент'),
            React.createElement(Badge, { kind:'lime', style:{marginBottom:18} }, 'Уровень 6 · Junior'),
            React.createElement('div', { className:'grid', style:{gap:0, textAlign:'left', marginTop:8} },
              statRow('Решено задач', '128'),
              statRow('Серия дней', React.createElement('b', { style:{color:'var(--lime)'} }, '7 🔥')),
              statRow('Точность', '82%'),
              statRow('Групп', '2'),
            ),
            React.createElement('button', { className:'btn btn-ghost btn-sm btn-full', style:{marginTop:14}, onClick:()=>navigate('/settings/profile') }, 'Редактировать профиль')
          ),
          // Right
          React.createElement('div', null,
            // activity
            React.createElement('div', { className:'card card-pad', style:{marginBottom:18} },
              React.createElement('div', { className:'between', style:{marginBottom:16} },
                React.createElement('b', { style:{fontSize:15} }, 'Активность за 26 недель'),
                React.createElement(Badge, { kind:'purple' }, '+18% к прошлому месяцу')
              ),
              React.createElement(ContribGraph, { weeks: 26 })
            ),
            // tabs
            React.createElement('div', { className:'tabbar' },
              React.createElement('button', { className: tab==='progress'?'on':'', onClick:()=>setTab('progress') }, 'Прогресс'),
              React.createElement('button', { className: tab==='solutions'?'on':'', onClick:()=>setTab('solutions') }, 'Мои решения'),
              React.createElement('button', { className: tab==='groups'?'on':'', onClick:()=>setTab('groups') }, 'Группы'),
            ),
            tab === 'progress' && React.createElement(StudentProgressPanel),
            tab === 'solutions' && React.createElement(StudentSolutionsPanel),
            tab === 'groups' && React.createElement(StudentGroupsPanel),
          )
        )
      )
    )
  );
}

function statRow(label, value) {
  return React.createElement('div', { className:'between', style:{padding:'11px 0', borderTop:'1px solid var(--border)'} },
    React.createElement('span', { className:'muted', style:{fontSize:13} }, label),
    typeof value === 'string' ? React.createElement('b', null, value) : value
  );
}

function StudentProgressPanel() {
  return React.createElement('div', { className:'cards2' },
    React.createElement('div', { className:'card card-pad' },
      React.createElement('b', { style:{fontSize:14} }, 'Навыки'),
      React.createElement('div', { style:{marginTop:14} },
        ['Алгоритмы 78%','Структуры данных 54%','Строки 91%','Графы 32%'].map((s,i) => {
          const [name, pct] = s.split(' ');
          const v = +pct.replace('%','');
          const pp = i % 2 === 1;
          return React.createElement('div', { key:i, style:{marginBottom: i<3?16:0} },
            React.createElement('div', { className:'between', style:{fontSize:13, marginBottom:6} },
              React.createElement('span', { className:'muted' }, s.split(' ').slice(0,-1).join(' ')),
              React.createElement('span', { className:'mono', style:{color: pp?'#b89bff':'var(--lime)'} }, pct)
            ),
            React.createElement('div', { className: 'progress '+(pp?'pp':'') }, React.createElement('i', { style:{width:pct} }))
          );
        })
      )
    ),
    React.createElement('div', { className:'card card-pad' },
      React.createElement('b', { style:{fontSize:14} }, 'Рекомендации'),
      React.createElement('div', { className:'grid', style:{gap:10, marginTop:14} },
        recRow('purple', '→', 'Подтяните ', React.createElement('b',null,'динамическое программирование')),
        recRow('purple', '→', '5 задач по графам ждут решения'),
        recRow('lime',   '✓', 'Бинарный поиск освоен — отлично!'),
        recRow('purple', '→', 'Серия 7 дней — продолжайте!'),
      )
    )
  );
}
function recRow(kind, sym, ...children) {
  return React.createElement('div', { className:'row', style:{gap:10} },
    React.createElement('span', { className:`badge badge-${kind}`, style:{width:26,height:26,padding:0,justifyContent:'center',borderRadius:8} }, sym),
    React.createElement('span', { style:{fontSize:13.5} }, ...children)
  );
}

function StudentSolutionsPanel() {
  const data = window.MOCK;
  const { navigate } = useRouter();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sort, setSort] = useState('new');

  const filtered = useMemo(() => {
    let r = data.submissions.filter(s => !search || s.title.toLowerCase().includes(search.toLowerCase()));
    if (statusFilter !== 'all') r = r.filter(s => s.status === statusFilter);
    if (sort === 'old') r = [...r].reverse();
    return r;
  }, [data.submissions, search, statusFilter, sort]);

  return React.createElement('div', null,
    React.createElement('div', { className:'between', style:{marginBottom:16, flexWrap:'wrap', gap:10} },
      React.createElement('input', { className:'input', style:{width:280, height:38}, placeholder:'Поиск по решениям…', value:search, onChange:e=>setSearch(e.target.value) }),
      React.createElement('div', { className:'wrap' },
        React.createElement('select', { className:'select', style:{width:150, height:38, padding:'8px 12px', fontSize:13}, value:statusFilter, onChange:e=>setStatusFilter(e.target.value) },
          React.createElement('option', { value:'all' }, 'Все статусы'),
          React.createElement('option', { value:'accepted' }, 'Принято'),
          React.createElement('option', { value:'failed' }, 'Ошибка тестов'),
          React.createElement('option', { value:'reviewing' }, 'На проверке'),
        ),
        React.createElement('select', { className:'select', style:{width:170, height:38, padding:'8px 12px', fontSize:13}, value:sort, onChange:e=>setSort(e.target.value) },
          React.createElement('option', { value:'new' }, 'Сначала новые'),
          React.createElement('option', { value:'old' }, 'Сначала старые'),
        ),
      )
    ),
    React.createElement('div', { className:'card card-pad' },
      filtered.length === 0
        ? React.createElement(EmptyState, { icon:'∅', title:'Нет решений', text:'Решите свою первую задачу — попытки появятся здесь.', action: React.createElement('button',{className:'btn btn-primary',onClick:()=>navigate('/')}, 'К списку задач') })
        : React.createElement('table', { className:'table' },
            React.createElement('thead', null, React.createElement('tr', null,
              React.createElement('th', null, 'Задача'),
              React.createElement('th', null, 'Язык'),
              React.createElement('th', null, 'Попытка'),
              React.createElement('th', null, 'Статус'),
              React.createElement('th', null, 'Дата')
            )),
            React.createElement('tbody', null,
              filtered.map(s => React.createElement('tr', { key:s.id, onClick:()=>navigate(`/tasks/${s.taskId}`) },
                React.createElement('td', { className:'t-name' }, s.title),
                React.createElement('td', { className:'muted' }, s.lang),
                React.createElement('td', { className:'mono mut3' }, '#'+s.attempt),
                React.createElement('td', null, React.createElement(StatusBadge, { status:s.status })),
                React.createElement('td', { className:'muted' }, s.date),
              ))
            )
          )
    )
  );
}

function StudentGroupsPanel() {
  const { navigate } = useRouter();
  const toast = useToast();
  const [inviteOpen, setInviteOpen] = useState(false);
  const [code, setCode] = useState('');

  return React.createElement('div', null,
    React.createElement('div', { className:'between', style:{marginBottom:16} },
      React.createElement('b', { style:{fontSize:15} }, 'Мои группы'),
      React.createElement('div', { className:'row' },
        React.createElement('input', { className:'input mono', style:{width:160, height:38}, placeholder:'GRP-XXXX', value:code, onChange:e=>setCode(e.target.value.toUpperCase()) }),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>{
          const g = window.MOCK.groups.find(x => x.invite === code.trim());
          if (g) { toast.push({kind:'lime', title:'Вы вступили', body:g.name}); navigate(`/student/groups/${g.id}`); }
          else toast.push({kind:'err', title:'Код не найден', body:'Проверьте написание.'});
        }}, 'Вступить по коду')
      )
    ),
    React.createElement('div', { className:'cards2' },
      window.MOCK.groups.map((g,i) => React.createElement('div', { key:g.id, className:'course-card '+(i%2?'pp':''), onClick:()=>navigate(`/student/groups/${g.id}`) },
        React.createElement('div', { className:'between' },
          React.createElement('b', { style:{fontSize:15} }, g.name),
          React.createElement(Badge, { kind: i%2?'purple':'lime' }, 'Активна')
        ),
        React.createElement('p', { className:'muted', style:{fontSize:13, margin:'8px 0 14px'} }, `Преподаватель: ${g.teacher} · ${g.students} студентов`),
        React.createElement('div', { className: 'progress '+(i%2?'pp':'') }, React.createElement('i', { style:{width: g.avgProgress+'%'} })),
        React.createElement('p', { className:'mut3', style:{fontSize:12, margin:'8px 0 0'} }, `Решено ${g.avgProgress}% задач курса`)
      ))
    ),
    React.createElement('div', { className:'note', style:{marginTop:18} },
      React.createElement('b', null, 'Хотите стать преподавателем? '),
      'Подайте заявку — администратор рассмотрит её в течение 1–2 дней. ',
      React.createElement('button', { className:'btn btn-secondary btn-xs', style:{marginLeft:8}, onClick:()=>toast.push({kind:'info', title:'Заявка отправлена', body:'Ожидайте ответа админа.'}) }, 'Подать заявку')
    )
  );
}

/* =========================================================
   STUDENT GROUP DETAIL  ( /student/groups/:groupId )
   ========================================================= */
function StudentGroupDetailPage({ groupId }) {
  const { navigate } = useRouter();
  const data = window.MOCK;
  const group = data.groups.find(g => g.id === groupId) || data.groups[0];
  const cats = group.catalogs.map(cid => data.catalogs.find(c => c.id === cid)).filter(Boolean);
  const [activeCat, setActiveCat] = useState(cats[0]?.id);
  const cat = cats.find(c => c.id === activeCat) || cats[0];
  const tasks = (cat?.taskIds || []).map(id => data.tasks.find(t => t.id === id)).filter(Boolean);
  const solved = tasks.filter(t => t.status === 'solved').length;

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: studentSidebarItems(), role:'STUDENT' }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Группы', crumbCurrent:group.name }),
      React.createElement('div', { className:'content' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:14}, onClick:()=>navigate('/student/profile', { query:{tab:'groups'} }) }, '← Все группы'),
        React.createElement(PageHeader, {
          title: group.name,
          subtitle: `Преподаватель: ${group.teacher} · ${group.students} студентов`,
          right: [ React.createElement(Badge, { key:1, kind:'lime' }, `Решено ${solved} / ${tasks.length}`) ]
        }),
        // teacher card
        React.createElement('div', {
          className:'card card-pad',
          style:{marginBottom:18, cursor:'pointer', transition:'.12s'},
          onClick:()=>{
            // find the teacher's id from adminUsers by matching name; fallback to demo id 113
            const t = window.MOCK.adminUsers.find(u => u.role==='TEACHER' && u.name === group.teacher);
            navigate(`/teachers/${t?.id || 113}`);
          },
          onMouseEnter:e=>e.currentTarget.style.borderColor='rgba(139,83,254,.4)',
          onMouseLeave:e=>e.currentTarget.style.borderColor='var(--border)'
        },
          React.createElement('div', { className:'between' },
            React.createElement('div', { className:'row' },
              React.createElement('div', { className:'avatar pp lg', style:{width:48,height:48,fontSize:18,borderRadius:14} }, group.teacher[0]),
              React.createElement('div', null,
                React.createElement('b', null, group.teacher),
                React.createElement('p', { className:'mut3', style:{margin:'2px 0 0', fontSize:12.5} }, 'Преподаватель группы · открыть профиль →')
              )
            ),
            React.createElement('span', { className:'mono mut3', style:{fontSize:12} }, 'Инвайт-код: ', React.createElement('span', {style:{color:'var(--lime)'}}, group.invite))
          )
        ),
        React.createElement('div', { style:{display:'grid', gridTemplateColumns:'230px 1fr', gap:18, alignItems:'start'} },
          React.createElement('aside', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:14} }, 'Каталоги'),
            React.createElement('div', { className:'grid', style:{gap:6, marginTop:12} },
              cats.map(c => React.createElement('button', {
                key:c.id, className:'chip '+(activeCat===c.id?'on':''),
                style:{width:'100%', justifyContent:'flex-start', height:34}, onClick:()=>setActiveCat(c.id)
              }, c.name))
            )
          ),
          React.createElement('div', { className:'card card-pad' },
            React.createElement('table', { className:'table' },
              React.createElement('thead', null, React.createElement('tr', null,
                React.createElement('th', null, 'Задача'),
                React.createElement('th', null, 'Сложность'),
                React.createElement('th', null, 'Статус'),
                React.createElement('th', null),
              )),
              React.createElement('tbody', null, tasks.map(t => React.createElement('tr', { key:t.id, className:'no-hover' },
                React.createElement('td', { className:'t-name' }, t.title),
                React.createElement('td', null, React.createElement(DiffBadge, { diff:t.diff })),
                React.createElement('td', null, React.createElement(StatusBadge, { status:t.status })),
                React.createElement('td', { style:{textAlign:'right'} },
                  React.createElement('button', {
                    className: 'btn btn-sm '+(t.status==='solved'?'btn-ghost':t.status==='attempted'?'btn-primary':'btn-ghost'),
                    onClick:()=>navigate(`/tasks/${t.id}`)
                  }, t.status==='solved' ? 'Открыть' : t.status==='attempted' ? 'Продолжить' : 'Начать')
                )
              )))
            )
          )
        )
      )
    )
  );
}

Object.assign(window, {
  TasksPage, TaskPage, StudentProfilePage, StudentGroupDetailPage,
  studentSidebarItems, Chip, Pagination, TaskStatusDot, Divider
});
