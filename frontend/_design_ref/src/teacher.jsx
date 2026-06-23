/* global React */
const { useState: useStateT, useMemo: useMemoT, useEffect: useEffectT } = React;

function teacherSidebarItems() {
  return [
    { divider: 'Преподаватель' },
    { to:'/teacher/profile', label:'Кабинет',     matches:(p)=>p.startsWith('/teacher/profile') },
    { to:'/teacher/tasks',   label:'Задачи',       matches:(p)=>p === '/teacher/tasks' || p.startsWith('/teacher/tasks/') },
    { to:'/teacher/catalogs',label:'Каталоги',     matches:(p)=>p.startsWith('/teacher/catalogs') },
    { divider: 'Аккаунт' },
    { to:'/settings/profile',label:'Настройки',    matches:(p)=>p.startsWith('/settings') },
    { to:'/',                label:'← К задачам (студентом)' },
  ];
}

/* =========================================================
   TEACHER PROFILE HUB
   ========================================================= */
const TEACHER_TABS = ['tasks','solutions','analytics','catalogs','groups','settings'];

function TeacherProfilePage() {
  const { user } = useAuth();
  const { query, navigate } = useRouter();
  const initial = TEACHER_TABS.includes(query.tab) ? query.tab : 'analytics';
  const [tab, setTab] = useStateT(initial);
  useEffectT(() => setTab(initial), [initial]);

  const switchTab = (t) => { setTab(t); navigate('/teacher/profile', { query:{ tab:t }, replace:true }); };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: teacherSidebarItems(), role:'TEACHER', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Преподаватель', crumbCurrent:'Кабинет' },
        React.createElement(RoleBadge, { role:'TEACHER' }),
      ),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, {
          title:'Кабинет преподавателя',
          subtitle:`${user?.name || 'Алексей Петров'} · ${user?.dept || 'Алгоритмы и структуры данных'}`,
          right:[ React.createElement('button', { key:1, className:'btn btn-primary btn-sm', onClick:()=>navigate('/teacher/create-task') }, '+ Создать задачу') ]
        }),
        React.createElement('div', { className:'tabbar' },
          tabBtn(tab,'tasks','Мои задачи',switchTab),
          tabBtn(tab,'solutions','Решения',switchTab),
          tabBtn(tab,'analytics','Аналитика',switchTab),
          tabBtn(tab,'catalogs','Каталоги',switchTab),
          tabBtn(tab,'groups','Группы',switchTab),
          tabBtn(tab,'settings','Настройки',switchTab),
        ),
        tab === 'tasks'     && React.createElement(TeacherTasksPanel),
        tab === 'solutions' && React.createElement(TeacherSolutionsPanel),
        tab === 'analytics' && React.createElement(TeacherAnalyticsPanel),
        tab === 'catalogs'  && React.createElement(TeacherCatalogsPanel),
        tab === 'groups'    && React.createElement(TeacherGroupsPanel),
        tab === 'settings'  && React.createElement(TeacherEmbeddedSettings),
      )
    )
  );
}

function tabBtn(active, key, label, onClick) {
  return React.createElement('button', { className:`${active===key?'on pp':''}`, onClick:()=>onClick(key) }, label);
}

function TeacherTasksPanel() {
  const { navigate } = useRouter();
  const toast = useToast();
  const data = window.MOCK;
  const [search, setSearch] = useStateT('');
  const [filter, setFilter] = useStateT('all'); // all/assigned/unassigned
  const [tasks, setTasks] = useStateT(data.tasks);

  const filtered = useMemoT(() => {
    return tasks.filter(t => {
      if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false;
      const hasCatalog = data.catalogs.some(c => c.taskIds.includes(t.id));
      if (filter === 'assigned' && !hasCatalog) return false;
      if (filter === 'unassigned' && hasCatalog) return false;
      return true;
    });
  }, [tasks, search, filter]);

  const removeTask = (id) => { setTasks(arr => arr.filter(t => t.id !== id)); toast.push({kind:'lime', title:'Задача удалена'}); };

  return React.createElement('div', null,
    React.createElement('div', { className:'between', style:{marginBottom:14, flexWrap:'wrap', gap:12} },
      React.createElement('input', { className:'input', style:{width:280, height:38}, placeholder:'Поиск среди ваших задач…', value:search, onChange:e=>setSearch(e.target.value) }),
      React.createElement('div', { className:'wrap' },
        React.createElement(Chip, { active:filter==='all', onClick:()=>setFilter('all') }, 'Все'),
        React.createElement(Chip, { active:filter==='assigned', pp:true, onClick:()=>setFilter('assigned') }, 'Назначенные'),
        React.createElement(Chip, { active:filter==='unassigned', onClick:()=>setFilter('unassigned') }, 'Без каталога'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>navigate('/teacher/create-task') }, '+ Создать задачу'),
      )
    ),
    React.createElement('div', { className:'card card-pad' },
      React.createElement('table', { className:'table' },
        React.createElement('thead', null, React.createElement('tr', null,
          React.createElement('th', null, 'Задача'),
          React.createElement('th', null, 'Тип'),
          React.createElement('th', null, 'Язык'),
          React.createElement('th', null, 'Сложность'),
          React.createElement('th', null, 'Каталог'),
          React.createElement('th', null),
        )),
        React.createElement('tbody', null, filtered.map(t => {
          const cat = data.catalogs.find(c => c.taskIds.includes(t.id));
          return React.createElement('tr', { key:t.id, className:'no-hover' },
            React.createElement('td', { className:'t-name' }, t.title),
            React.createElement('td', { className:'muted' }, data.taskTypes.find(x=>x.id===t.type)?.label || t.type),
            React.createElement('td', { className:'muted' }, t.lang),
            React.createElement('td', null, React.createElement(DiffBadge, { diff:t.diff })),
            React.createElement('td', null, cat ? React.createElement(Badge, { kind:'purple' }, cat.name) : React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, '—')),
            React.createElement('td', { style:{textAlign:'right'} },
              React.createElement('div', { className:'row', style:{gap:6, justifyContent:'flex-end'} },
                React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>navigate(`/tasks/${t.id}`) }, 'Открыть'),
                React.createElement('button', { className:'btn btn-secondary btn-sm', onClick:()=>navigate(t.type==='code_assembly'||t.type==='block_reorder' ? `/teacher/code-assembly/${t.id}/edit` : `/teacher/tasks/${t.id}/edit`) }, 'Редактировать'),
              )
            )
          );
        }))
      )
    )
  );
}

function TeacherSolutionsPanel() {
  const data = window.MOCK;
  const [filter, setFilter] = useStateT('all');
  const filtered = data.submissions.filter(s => filter==='all' || s.status === filter);
  return React.createElement('div', null,
    React.createElement('div', { className:'wrap', style:{marginBottom:14} },
      React.createElement(Chip, { active:filter==='all', onClick:()=>setFilter('all') }, 'Все'),
      React.createElement(Chip, { active:filter==='accepted', onClick:()=>setFilter('accepted') }, 'Принятые'),
      React.createElement(Chip, { active:filter==='failed', onClick:()=>setFilter('failed') }, 'С ошибкой'),
      React.createElement(Chip, { active:filter==='reviewing', pp:true, onClick:()=>setFilter('reviewing') }, 'На проверке'),
    ),
    React.createElement('div', { className:'card card-pad' },
      React.createElement('table', { className:'table' },
        React.createElement('thead', null, React.createElement('tr', null,
          React.createElement('th', null, 'Студент'),
          React.createElement('th', null, 'Задача'),
          React.createElement('th', null, 'Язык'),
          React.createElement('th', null, 'Статус'),
          React.createElement('th', null, 'Дата'),
          React.createElement('th', null),
        )),
        React.createElement('tbody', null, filtered.map((s,i) => {
          const studentNames = ['Влада М.','Никита П.','Ольга С.','Дмитрий О.','Анна К.','Михаил В.'];
          const initials = ['В','Н','О','Д','А','М'];
          return React.createElement('tr', { key:s.id, className:'no-hover' },
            React.createElement('td', null, React.createElement('div', { className:'row', style:{gap:9} },
              React.createElement('span', { className:'avatar sm' }, initials[i % initials.length]),
              React.createElement('span', { className:'t-name' }, studentNames[i % studentNames.length])
            )),
            React.createElement('td', null, s.title),
            React.createElement('td', { className:'muted' }, s.lang),
            React.createElement('td', null, React.createElement(StatusBadge, { status:s.status })),
            React.createElement('td', { className:'muted' }, s.date),
            React.createElement('td', { style:{textAlign:'right'} }, React.createElement('button', { className:'btn btn-ghost btn-sm' }, 'Проверить'))
          );
        }))
      )
    )
  );
}

function TeacherAnalyticsPanel() {
  const a = window.MOCK.teacherAnalytics;
  return React.createElement('div', null,
    React.createElement('div', { className:'cards3', style:{marginBottom:18} },
      React.createElement(StatCard, { label:'Студентов', value:a.students, badge:`+${a.weekly} за неделю`, badgeKind:'lime' }),
      React.createElement(StatCard, { label:'Активных задач', value:a.activeTasks, badge:`в ${a.catalogs} каталогах`, badgeKind:'purple' }),
      React.createElement(StatCard, { label:'Средняя сдача', value: Math.round(a.acceptance*100)+'%', badge:`${a.deltaMonth>0?'+':''}${Math.round(a.deltaMonth*100)}% к месяцу`, badgeKind: a.deltaMonth<0?'warn':'lime' }),
    ),
    React.createElement('div', { className:'card card-pad' },
      React.createElement('div', { className:'between', style:{marginBottom:16} },
        React.createElement('b', { style:{fontSize:15} }, 'Решения по дням'),
        React.createElement('select', { className:'select', style:{width:140, height:34, padding:'6px 12px', fontSize:13} },
          React.createElement('option', null, '30 дней'),
          React.createElement('option', null, '7 дней'),
        )
      ),
      React.createElement('div', { style:{display:'flex', alignItems:'flex-end', gap:5, height:140} },
        a.bars.map((v,i) => React.createElement('div', { key:i, style:{flex:1, background: v>85?'var(--lime)':'var(--purple)', height:v+'%', borderRadius:4, opacity: v<25?0.35:1} }))
      ),
      React.createElement('div', { className:'wrap', style:{marginTop:14, gap:18, fontSize:12.5, color:'var(--text-2)'} },
        legendDot('var(--purple)', 'Принятые решения'),
        legendDot('var(--lime)', 'Пики активности'),
      )
    ),
    React.createElement('div', { className:'cards2', style:{marginTop:16} },
      React.createElement('div', { className:'card card-pad' },
        React.createElement('b', { style:{fontSize:14} }, 'Топ задач по решениям'),
        React.createElement('div', { className:'grid', style:{gap:10, marginTop:14} },
          ['Линейный поиск — 42','Развернуть массив — 38','Двоичный поиск — 31','Палиндром — 22'].map((t,i) =>
            React.createElement('div', { key:i, className:'between', style:{fontSize:13.5, padding:'8px 0', borderTop: i?'1px solid var(--border)':'none'} },
              React.createElement('span', null, t.split('—')[0]),
              React.createElement('b', { className:'mono', style:{color:'var(--lime)'} }, t.split('—')[1])
            ))
        )
      ),
      React.createElement('div', { className:'card card-pad' },
        React.createElement('b', { style:{fontSize:14} }, 'Проблемные задачи'),
        React.createElement('div', { className:'grid', style:{gap:10, marginTop:14} },
          ['Сортировка слиянием — 38% сдают','Числа Фибоначчи (DP) — 41% сдают','Кратчайший путь BFS — 22% сдают'].map((t,i) =>
            React.createElement('div', { key:i, className:'between', style:{fontSize:13.5, padding:'8px 0', borderTop: i?'1px solid var(--border)':'none'} },
              React.createElement('span', null, t.split('—')[0]),
              React.createElement(Badge, { kind:'warn' }, t.split('—')[1].trim())
            ))
        )
      )
    )
  );
}
function legendDot(color, label) {
  return React.createElement('span', { style:{display:'inline-flex', alignItems:'center', gap:7} },
    React.createElement('i', { style:{width:11, height:11, borderRadius:3, background:color, display:'inline-block'} }),
    label
  );
}

function TeacherCatalogsPanel() {
  const { navigate } = useRouter();
  const toast = useToast();
  const data = window.MOCK;
  const [cats, setCats] = useStateT(data.catalogs);
  const [createOpen, setCreateOpen] = useStateT(false);
  const [newName, setNewName] = useStateT('');
  const [confirmDel, setConfirmDel] = useStateT(null);
  const [assignOpen, setAssignOpen] = useStateT(null);
  const [pickedGroup, setPickedGroup] = useStateT('');

  const create = () => {
    if (!newName.trim()) return;
    const id = newName.toLowerCase().replace(/\s/g,'-').slice(0,15);
    setCats(arr => [...arr, { id, name:newName.trim(), taskIds:[], assignedTo:[] }]);
    setCreateOpen(false); setNewName('');
    toast.push({kind:'lime', title:'Каталог создан', body:newName});
  };
  const del = () => { setCats(arr => arr.filter(c => c.id !== confirmDel.id)); toast.push({kind:'lime', title:'Каталог удалён'}); setConfirmDel(null); };

  return React.createElement('div', null,
    React.createElement('div', { className:'between', style:{marginBottom:16} },
      React.createElement('b', { style:{fontSize:15} }, 'Каталоги задач'),
      React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>setCreateOpen(true) }, '+ Создать каталог')
    ),
    React.createElement('div', { className:'cards3' },
      cats.map(c => React.createElement('div', { key:c.id, className:'course-card pp' },
        React.createElement('div', { className:'between' },
          React.createElement('div', { className:'ico' }, c.name.split(' ').map(w=>w[0]).slice(0,2).join('').toUpperCase()),
          React.createElement(Badge, { kind:'purple' }, `${c.taskIds.length} задач`)
        ),
        React.createElement('b', { style:{display:'block', marginTop:12, fontSize:15} }, c.name),
        React.createElement('p', { className:'muted', style:{fontSize:13, margin:'6px 0 14px'} },
          c.assignedTo.length ? `Назначен ${c.assignedTo.length} группе(ам)` : 'Не назначен ни одной группе'
        ),
        React.createElement('div', { className:'row', style:{gap:8, flexWrap:'wrap'} },
          React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>navigate(`/teacher/catalogs/${c.id}`) }, 'Открыть'),
          React.createElement('button', { className:'btn btn-secondary btn-sm', onClick:()=>setAssignOpen(c) }, 'Назначить группе'),
          React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>setConfirmDel(c) }, '✕'),
        )
      )),
      React.createElement('div', {
        className:'course-card',
        style:{display:'grid', placeItems:'center', borderStyle:'dashed', minHeight:170, cursor:'pointer'},
        onClick:()=>setCreateOpen(true)
      },
        React.createElement('div', { style:{textAlign:'center'} },
          React.createElement('div', { style:{fontSize:28, color:'var(--text-3)'} }, '+'),
          React.createElement('span', { className:'muted', style:{fontSize:13.5} }, 'Новый каталог')
        )
      )
    ),
    // create modal
    React.createElement(Modal, {
      open:createOpen, onClose:()=>setCreateOpen(false), title:'Новый каталог',
      footer:React.createElement(React.Fragment, null,
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setCreateOpen(false) }, 'Отмена'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:create }, 'Создать')
      )
    },
      React.createElement('div', { className:'field' },
        React.createElement('label', { className:'label' }, 'Название'),
        React.createElement('input', { className:'input', placeholder:'Алгоритмы · продвинутый', value:newName, onChange:e=>setNewName(e.target.value), autoFocus:true })
      )
    ),
    // delete modal
    React.createElement(ConfirmDialog, {
      open: !!confirmDel, onClose:()=>setConfirmDel(null), onConfirm:del,
      title:'Удалить каталог?', danger:true, confirmLabel:'Удалить',
      body: confirmDel ? `Каталог «${confirmDel.name}» и связи с группами будут удалены. Задачи останутся в общем списке.` : ''
    }),
    // assign modal
    React.createElement(Modal, {
      open: !!assignOpen, onClose:()=>setAssignOpen(null), title: assignOpen ? `Назначить «${assignOpen.name}»` : '',
      footer:React.createElement(React.Fragment, null,
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setAssignOpen(null) }, 'Отмена'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>{
          if (!pickedGroup) return;
          const grp = window.MOCK.groups.find(g=>g.id===pickedGroup);
          setCats(arr => arr.map(c => c.id===assignOpen.id ? {...c, assignedTo:[...new Set([...c.assignedTo, grp.name])]} : c));
          toast.push({kind:'lime', title:'Каталог назначен', body:grp.name});
          setAssignOpen(null); setPickedGroup('');
        }}, 'Назначить')
      )
    },
      React.createElement('div', { className:'field' },
        React.createElement('label', { className:'label' }, 'Группа'),
        React.createElement('select', { className:'select', value:pickedGroup, onChange:e=>setPickedGroup(e.target.value) },
          React.createElement('option', { value:'' }, 'Выберите группу…'),
          window.MOCK.groups.map(g => React.createElement('option', { key:g.id, value:g.id }, g.name))
        )
      )
    ),
  );
}

function TeacherGroupsPanel() {
  const data = window.MOCK;
  const [active, setActive] = useStateT(data.groups[0].id);
  const [createOpen, setCreateOpen] = useStateT(false);
  const [name, setName] = useStateT('');
  const [groups, setGroups] = useStateT(data.groups);
  const toast = useToast();
  const group = groups.find(g => g.id === active) || groups[0];
  const students = data.groupStudents[group.id] || [];

  return React.createElement('div', { style:{display:'grid', gridTemplateColumns:'230px 1fr', gap:18, alignItems:'start'} },
    React.createElement('aside', { className:'card card-pad' },
      React.createElement('div', { className:'between', style:{marginBottom:12} },
        React.createElement('b', { style:{fontSize:14} }, 'Группы'),
        React.createElement('button', { className:'btn btn-ghost btn-icon btn-xs', onClick:()=>setCreateOpen(true) }, '+')
      ),
      React.createElement('div', { className:'grid', style:{gap:8} },
        groups.map(g => React.createElement('button', {
          key:g.id, onClick:()=>setActive(g.id),
          style:{
            border: active===g.id ? '1px solid rgba(139,83,254,.4)' : '1px solid var(--border)',
            background: active===g.id ? 'var(--purple-soft)' : 'transparent',
            borderRadius:10, padding:11, textAlign:'left', cursor:'pointer'
          }
        },
          React.createElement('b', { style:{fontSize:13.5, color: active===g.id?'#b89bff':'var(--text)'} }, g.name),
          React.createElement('div', { className:'mut3', style:{fontSize:12, marginTop:2} }, `${g.students} студентов`)
        ))
      )
    ),
    React.createElement('div', null,
      React.createElement('div', { className:'card card-pad', style:{marginBottom:16} },
        React.createElement('div', { className:'between' },
          React.createElement('div', null,
            React.createElement('b', { style:{fontSize:16} }, group.name),
            React.createElement('p', { className:'mut3', style:{fontSize:12.5, margin:'4px 0 0'} },
              'Инвайт-код: ', React.createElement('span', { className:'mono', style:{color:'var(--lime)'} }, group.invite)
            )
          ),
          React.createElement('div', { className:'row' },
            React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>{ navigator.clipboard?.writeText(group.invite); toast.push({kind:'lime', title:'Код скопирован', body:group.invite}); } }, '⧉ Копировать код'),
            React.createElement(Badge, { kind:'lime' }, `Средний прогресс ${group.avgProgress}%`)
          )
        )
      ),
      React.createElement('div', { className:'card card-pad' },
        React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:6} }, 'Прогресс студентов'),
        React.createElement('table', { className:'table' },
          React.createElement('thead', null, React.createElement('tr', null,
            React.createElement('th', null, 'Студент'),
            React.createElement('th', null, 'Решено'),
            React.createElement('th', null, 'Прогресс'),
            React.createElement('th', null, 'Активность'),
          )),
          React.createElement('tbody', null, students.map((s,i) => React.createElement('tr', { key:s.id, onClick:()=>window.location.hash=`/students/${s.id+810}`, style:{cursor:'pointer'} },
            React.createElement('td', null, React.createElement('div', { className:'row', style:{gap:9} },
              React.createElement('span', { className:'avatar sm', style:{width:28, height:28, fontSize:12} }, s.initials),
              React.createElement('span', { className:'t-name' }, s.name)
            )),
            React.createElement('td', { className:'mono' }, `${s.solved} / ${s.total}`),
            React.createElement('td', { style:{minWidth:140} }, React.createElement('div', { className:'progress '+(i%3===2?'pp':'') }, React.createElement('i', { style:{width: Math.round((s.solved/s.total)*100)+'%'} }))),
            React.createElement('td', { className:'muted' }, s.lastActive),
          )))
        )
      )
    ),
    React.createElement(Modal, {
      open:createOpen, onClose:()=>setCreateOpen(false), title:'Создать группу',
      footer:React.createElement(React.Fragment, null,
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setCreateOpen(false) }, 'Отмена'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>{
          if (!name.trim()) return;
          const id = name.toLowerCase().replace(/\s/g,'-').slice(0,12);
          const invite = 'GRP-' + Math.random().toString(36).slice(2,6).toUpperCase();
          const ng = { id, name:name.trim(), invite, teacher:'Алексей Петров', students:0, catalogs:[], avgProgress:0 };
          setGroups(arr => [...arr, ng]); setActive(id);
          toast.push({kind:'lime', title:'Группа создана', body:`Код: ${invite}`});
          setCreateOpen(false); setName('');
        }}, 'Создать')
      )
    },
      React.createElement('div', { className:'field' },
        React.createElement('label', { className:'label' }, 'Название группы'),
        React.createElement('input', { className:'input', value:name, onChange:e=>setName(e.target.value), placeholder:'ИВТ-302', autoFocus:true })
      )
    )
  );
}

function TeacherEmbeddedSettings() {
  // dupes /settings/profile + /settings/security inline (per audit)
  const { navigate } = useRouter();
  return React.createElement('div', null,
    React.createElement('div', { className:'note', style:{marginBottom:16} },
      'Эти же настройки доступны на отдельной странице ',
      React.createElement('button', { className:'btn btn-secondary btn-xs', onClick:()=>navigate('/settings/profile'), style:{marginLeft:6} }, '/settings/*'),
      ' — здесь они встроены для удобства.'
    ),
    React.createElement(window.ProfileTab),
    React.createElement('div', { style:{height:16} }),
    React.createElement(window.SecurityTab),
  );
}

/* =========================================================
   TEACHER TASKS PAGE  (/teacher/tasks) — full-page list
   ========================================================= */
function TeacherTasksPage() {
  const { navigate } = useRouter();
  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: teacherSidebarItems(), role:'TEACHER', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Преподаватель', crumbCurrent:'Задачи' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, {
          title:'Мои задачи',
          subtitle:'Создавайте, редактируйте и распределяйте задачи по каталогам.',
          right:[
            React.createElement('button', { key:1, className:'btn btn-ghost btn-sm', onClick:()=>navigate('/teacher/profile', { query:{tab:'tasks'} }) }, '← В кабинет'),
            React.createElement('button', { key:2, className:'btn btn-primary btn-sm', onClick:()=>navigate('/teacher/create-task') }, '+ Создать задачу'),
          ]
        }),
        React.createElement(TeacherTasksPanel),
      )
    )
  );
}

/* =========================================================
   TEACHER CATALOG DETAIL  (/teacher/catalogs/:catalogId)
   ========================================================= */
function TeacherCatalogPage({ catalogId }) {
  const { navigate } = useRouter();
  const data = window.MOCK;
  const toast = useToast();
  const cat = data.catalogs.find(c => c.id === catalogId) || data.catalogs[0];
  const [taskIds, setTaskIds] = useStateT(cat.taskIds);
  const [search, setSearch] = useStateT('');
  const [picks, setPicks] = useStateT([]);

  const inside = taskIds.map(id => data.tasks.find(t => t.id === id)).filter(Boolean);
  const candidates = data.tasks.filter(t => !taskIds.includes(t.id) && (!search || t.title.toLowerCase().includes(search.toLowerCase())));

  const togglePick = (id) => setPicks(p => p.includes(id) ? p.filter(x=>x!==id) : [...p,id]);
  const addPicks = () => { setTaskIds(arr => [...arr, ...picks]); toast.push({kind:'lime', title:`Добавлено ${picks.length} задач`}); setPicks([]); };
  const remove = (id) => { setTaskIds(arr => arr.filter(x => x !== id)); toast.push({kind:'lime', title:'Задача убрана'}); };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: teacherSidebarItems(), role:'TEACHER', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome: React.createElement('a', { onClick:()=>navigate('/teacher/profile', { query:{tab:'catalogs'} }), style:{cursor:'pointer'} }, 'Каталоги'), crumbCurrent: cat.name }),
      React.createElement('div', { className:'content' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:14}, onClick:()=>navigate('/teacher/profile', { query:{tab:'catalogs'} }) }, '← К каталогам'),
        React.createElement(PageHeader, {
          title: cat.name,
          subtitle: `${inside.length} задач · ${cat.assignedTo.length ? `назначен ${cat.assignedTo.join(', ')}` : 'без назначений'}`,
          right:[ React.createElement('button', { key:1, className:'btn btn-secondary btn-sm' }, 'Назначить группе') ]
        }),
        React.createElement('div', { style:{display:'grid', gridTemplateColumns:'1fr 360px', gap:18, alignItems:'start'} },
          React.createElement('div', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:10} }, 'Задачи внутри каталога'),
            inside.length === 0
              ? React.createElement(EmptyState, { icon:'📚', title:'В каталоге пока нет задач', text:'Выберите задачи в панели справа и нажмите «Добавить выбранные» — они появятся здесь.' })
              : React.createElement('table', { className:'table' },
                  React.createElement('thead', null, React.createElement('tr', null,
                    React.createElement('th', null, 'Задача'), React.createElement('th', null, 'Тип'), React.createElement('th', null, 'Сложность'), React.createElement('th', null)
                  )),
                  React.createElement('tbody', null, inside.map(t => React.createElement('tr', { key:t.id, className:'no-hover' },
                    React.createElement('td', { className:'t-name' }, t.title),
                    React.createElement('td', { className:'muted' }, data.taskTypes.find(x=>x.id===t.type)?.label || t.type),
                    React.createElement('td', null, React.createElement(DiffBadge, { diff:t.diff })),
                    React.createElement('td', { style:{textAlign:'right'} },
                      React.createElement('div', { className:'row', style:{gap:6, justifyContent:'flex-end'} },
                        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>navigate(`/teacher/tasks/${t.id}/edit`) }, 'Редактор'),
                        React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>remove(t.id) }, 'Убрать')
                      )
                    )
                  )))
                )
          ),
          React.createElement('aside', { className:'card card-pad' },
            React.createElement('div', { className:'between', style:{marginBottom:4} },
              React.createElement('b', { style:{fontSize:14} }, 'Добавить существующие задачи'),
              picks.length > 0 && React.createElement('button', { className:'btn btn-primary btn-sm', onClick:addPicks }, `Добавить выбранные (${picks.length})`)
            ),
            React.createElement('p', { className:'mut3', style:{fontSize:12, margin:'0 0 12px'} }, 'Можно выбрать сразу несколько задач'),
            React.createElement('input', { className:'input', style:{height:36, marginBottom:10}, placeholder:'Поиск задач…', value:search, onChange:e=>setSearch(e.target.value) }),
            candidates.length === 0
              ? React.createElement(EmptyState, { icon:'🔍', title:'Нет задач для добавления', text: search ? 'По запросу ничего не найдено.' : 'Все ваши задачи уже в этом каталоге.' })
              : React.createElement('div', { className:'grid', style:{gap:6, maxHeight:380, overflow:'auto'} },
                candidates.map(t => {
                  const on = picks.includes(t.id);
                  return React.createElement('label', {
                    key:t.id, className:'candidate-tile '+(on?'on':''),
                  },
                    React.createElement('span', { className:'checkbox '+(on?'on':''), onClick:(e)=>{ e.preventDefault(); togglePick(t.id); } }),
                    React.createElement('span', { style:{flex:1, minWidth:0} },
                      React.createElement('span', { style:{display:'block', fontSize:13.5, color:'var(--text)', fontWeight:500} }, t.title),
                      React.createElement('span', { className:'mono mut3', style:{fontSize:11} }, `#${t.id} · ${data.taskTypes.find(x=>x.id===t.type)?.label || t.type}`)
                    ),
                    React.createElement(DiffBadge, { diff:t.diff })
                  );
                })
              )
          )
        )
      )
    )
  );
}

/* =========================================================
   TASK EDITOR  (/teacher/create-task & .../:id/edit)
   Tabs-based config + live preview + preview mode + run
   ========================================================= */
function TaskEditorPage({ taskId, isEdit }) {
  const { navigate } = useRouter();
  const toast = useToast();
  const data = window.MOCK;
  const base = isEdit ? (data.tasks.find(t => t.id === +taskId) || data.tasks[0]) : null;

  const [form, setForm] = useStateT(() => ({
    title:     base?.title || '',
    type:      base?.type || 'algorithm',
    lang:      base?.lang === '—' ? 'Python' : (base?.lang || 'Python'),
    diff:      base?.diff || 'Средняя',
    desc:      base?.desc || '',
    complexity: base?.complexity || 'O(n)',
    constraints: '1 ≤ n ≤ 10⁵\nмассив отсортирован\n−10⁹ ≤ arr[i] ≤ 10⁹',
    tests:     '[1,3,5,7,9],5 -> 2\n[2,4,6,8],8 -> 3\n[],4 -> -1',
    reference: data.codeSample[base?.lang === '—' ? 'Python' : (base?.lang || 'Python')] || data.codeSample.Python,
    catalog:   data.catalogs.find(c => c.taskIds.includes(base?.id))?.id || '',
    patterns:  base?.pattern ? [base.pattern] : [],
    hint:      'Сужайте диапазон поиска вдвое на каждой итерации.',
    visible:   true,
    groups:    [],
  }));
  const set = (k,v) => setForm(f => ({...f, [k]:v}));

  // tabs for config
  const [configTab, setConfigTab] = useStateT('basic'); // basic | condition | tests | reference | placement
  const [previewMode, setPreviewMode] = useStateT(false);
  const [discardOpen, setDiscardOpen] = useStateT(false);

  // autosave indicator (debounced)
  const [savedAt, setSavedAt] = useStateT(null);
  const [dirty, setDirty] = useStateT(false);
  useEffectT(() => {
    setDirty(true);
    const t = setTimeout(() => { setSavedAt(new Date().toLocaleTimeString().slice(0,5)); setDirty(false); }, 700);
    return () => clearTimeout(t);
  }, [form]);

  const [runState, setRunState] = useStateT(null); // null | 'running' | {pass, total, results}
  const testCount = useMemoT(() => form.tests.split('\n').filter(l => l.trim()).length, [form.tests]);
  const runRef = () => {
    setRunState('running');
    setTimeout(() => {
      const total = Math.max(1, testCount);
      // Demo logic: pass all if reference is non-empty + has return statement, else partial
      const looksReal = /return|=>/.test(form.reference) && form.reference.trim().length > 30;
      const pass = looksReal ? total : Math.max(0, total - 1);
      const results = Array.from({length:total}, (_,i) => ({ idx:i+1, pass: i < pass, expected:i*2, actual: i < pass ? i*2 : -1 }));
      setRunState({ pass, total, results });
      toast.push({
        kind: pass === total ? 'lime' : 'warn',
        title: pass === total ? 'Эталон прошёл все тесты' : `${pass}/${total} тестов прошло`,
        body: pass === total ? 'Можно публиковать' : 'Проверьте тесты или эталонный код'
      });
    }, 900);
  };

  const save = () => {
    if (!form.title.trim()) { toast.push({kind:'err', title:'Укажите название задачи'}); setConfigTab('basic'); return; }
    if (!form.desc.trim())  { toast.push({kind:'err', title:'Заполните условие'}); setConfigTab('condition'); return; }
    toast.push({kind:'lime', title:isEdit?'Задача обновлена':'Задача создана', body:form.title});
    navigate('/teacher/profile', { query:{tab:'tasks'} });
  };

  const ext = form.lang==='Python'?'py':form.lang==='JavaScript'?'js':form.lang==='C++'?'cpp':form.lang==='Java'?'java':'txt';
  const typeLabel = data.taskTypes.find(t => t.id === form.type)?.label || form.type;

  return React.createElement('div', { style:{minHeight:'100vh', display:'flex', flexDirection:'column'} },
    // === TOP BAR ===
    React.createElement('div', { className:'topbar', style:{padding:'12px 20px'} },
      React.createElement('div', { className:'row' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>{ if (dirty) setDiscardOpen(true); else navigate('/teacher/profile', { query:{tab:'tasks'} }); } }, '← Назад'),
        React.createElement('div', { className:'crumb' }, isEdit?'Редактор':'Новая задача', ' / ', React.createElement('b', null, form.title || 'Без названия')),
        React.createElement(Badge, { kind:'purple' }, typeLabel),
        React.createElement(DiffBadge, { diff:form.diff }),
      ),
      React.createElement('div', { className:'row' },
        savedAt && !dirty && React.createElement('span', { className:'muted', style:{fontSize:12.5} }, '✓ Автосохранение · ', savedAt),
        dirty && React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, '○ Сохранение…'),
        // Mode toggle
        React.createElement('div', { style:{display:'flex', background:'var(--surface-2)', borderRadius:10, padding:3, gap:2, border:'1px solid var(--border-2)'} },
          React.createElement('button', {
            className:'btn-xs',
            style:{
              padding:'6px 12px', borderRadius:7, border:0, cursor:'pointer', fontSize:12, fontWeight:600,
              background: previewMode ? 'transparent' : 'var(--lime)',
              color: previewMode ? 'var(--text-2)' : '#0a0e15'
            },
            onClick:()=>setPreviewMode(false)
          }, '✎ Редактор'),
          React.createElement('button', {
            className:'btn-xs',
            style:{
              padding:'6px 12px', borderRadius:7, border:0, cursor:'pointer', fontSize:12, fontWeight:600,
              background: previewMode ? 'var(--purple)' : 'transparent',
              color: previewMode ? '#fff' : 'var(--text-2)'
            },
            onClick:()=>setPreviewMode(true)
          }, '👁 Превью'),
        ),
        React.createElement('button', { className:'btn btn-secondary btn-sm', onClick:runRef, disabled:runState==='running' },
          runState==='running' ? '⟳ Прогон…' : '▸ Прогнать эталон'
        ),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:save }, isEdit?'Сохранить':'Создать задачу')
      )
    ),

    // === BODY ===
    previewMode
      ? React.createElement(TaskEditorPreview, { form, runState })
      : React.createElement('div', { style:{display:'grid', gridTemplateColumns:'minmax(380px,1fr) 1.05fr', flex:1, minHeight:0} },
          // CONFIG (LEFT)
          React.createElement('div', { style:{display:'flex', flexDirection:'column', borderRight:'1px solid var(--border)', minHeight:0} },
            React.createElement('div', { className:'tabbar', style:{margin:'0 24px', flex:'none'} },
              React.createElement('button', { className: configTab==='basic'?'on':'',     onClick:()=>setConfigTab('basic') },     'Основное'),
              React.createElement('button', { className: configTab==='condition'?'on':'', onClick:()=>setConfigTab('condition') }, 'Условие'),
              React.createElement('button', { className: configTab==='tests'?'on':'',     onClick:()=>setConfigTab('tests') },     'Тесты',
                React.createElement('span', { className:'mut3', style:{marginLeft:6, fontSize:11, fontFamily:'var(--mono)'} }, testCount)
              ),
              React.createElement('button', { className: configTab==='reference'?'on':'', onClick:()=>setConfigTab('reference') }, 'Эталон'),
              React.createElement('button', { className: configTab==='placement'?'on':'', onClick:()=>setConfigTab('placement') }, 'Назначение'),
            ),
            React.createElement('div', { style:{padding:'18px 24px 32px', overflow:'auto', flex:1, minHeight:0} },
              configTab === 'basic'      && React.createElement(TabBasic,     { form, set, data }),
              configTab === 'condition'  && React.createElement(TabCondition, { form, set, data }),
              configTab === 'tests'      && React.createElement(TabTests,     { form, set, runState }),
              configTab === 'reference'  && React.createElement(TabReference, { form, set, ext, runState, runRef }),
              configTab === 'placement'  && React.createElement(TabPlacement, { form, set, data }),
            )
          ),
          // LIVE PREVIEW (RIGHT)
          React.createElement('div', { style:{display:'flex', flexDirection:'column', background:'var(--bg-2)', minHeight:0, overflow:'hidden'} },
            React.createElement('div', { className:'row', style:{padding:'14px 22px', borderBottom:'1px solid var(--border)', justifyContent:'space-between', flex:'none', background:'#0c111a'} },
              React.createElement('div', { className:'row', style:{gap:10} },
                React.createElement('div', { className:'eyebrow', style:{margin:0} }, 'Предпросмотр'),
                React.createElement('span', { className:'mut3', style:{fontSize:12} }, '· как увидит студент')
              ),
              React.createElement('button', { className:'btn btn-ghost btn-xs', onClick:()=>setPreviewMode(true) }, 'Полноэкранно →')
            ),
            React.createElement('div', { style:{flex:1, overflow:'auto', padding:'22px 26px'} },
              React.createElement(LivePreviewCard, { form, ext })
            ),
            // Run result strip at the bottom
            React.createElement(RunResultStrip, { runState, runRef })
          )
        ),
    React.createElement(ConfirmDialog, {
      open:discardOpen, onClose:()=>setDiscardOpen(false),
      onConfirm:()=>navigate('/teacher/profile', { query:{tab:'tasks'} }),
      title:'Выйти без сохранения?', confirmLabel:'Выйти', danger:true,
      body:'У вас есть несохранённые изменения. Изменения сохранятся автоматически — но вы можете уйти прямо сейчас.'
    })
  );
}

/* ===== Editor sub-tabs ===== */
function TabBasic({ form, set, data }) {
  return React.createElement(React.Fragment, null,
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Название задачи'),
      React.createElement('input', { className:'input', value:form.title, onChange:e=>set('title', e.target.value), placeholder:'Например, Двоичный поиск' })
    ),
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Тип задания'),
      React.createElement('div', { className:'wrap' },
        data.taskTypes.slice(0,5).map(t => React.createElement(Chip, { key:t.id, active:form.type===t.id, pp:true, onClick:()=>set('type', t.id) }, t.label))
      ),
      React.createElement('div', { className:'help' }, 'От типа зависит, какой редактор увидит студент: Monaco, блок-схема или блоки.')
    ),
    React.createElement('div', { className:'row', style:{gap:12, alignItems:'flex-start'} },
      React.createElement('div', { className:'field', style:{flex:1} },
        React.createElement('label', { className:'label' }, 'Язык'),
        React.createElement('select', { className:'select', value:form.lang, onChange:e=>set('lang', e.target.value) },
          data.languages.map(l => React.createElement('option', { key:l, value:l }, l))
        )
      ),
      React.createElement('div', { className:'field', style:{flex:1} },
        React.createElement('label', { className:'label' }, 'Сложность'),
        React.createElement('div', { className:'wrap' },
          data.difficulties.map(d => React.createElement(Chip, { key:d, active:form.diff===d, onClick:()=>set('diff', d) }, d))
        )
      ),
    ),
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Конструкции / Паттерны'),
      React.createElement('div', { className:'wrap' },
        data.patterns.map(p => React.createElement(Chip, { key:p, sm:true, active:form.patterns.includes(p), onClick:()=>{
          set('patterns', form.patterns.includes(p) ? form.patterns.filter(x=>x!==p) : [...form.patterns, p]);
        } }, p))
      ),
      React.createElement('div', { className:'help' }, 'Выберите 1–3 ключевых паттерна. Они показываются студенту в подсказках.')
    ),
    React.createElement('div', { className:'field', style:{marginBottom:0} },
      React.createElement('label', { className:'label' }, 'Видимость'),
      React.createElement('label', { className:'check-row', onClick:e=>e.preventDefault(), style:{padding:'10px 12px', border:'1px solid var(--border)', borderRadius:10, cursor:'pointer'} },
        React.createElement('span', { className:'checkbox '+(form.visible?'on':''), onClick:()=>set('visible', !form.visible) }),
        React.createElement('span', { style:{flex:1, fontSize:13.5, color:'var(--text)'} }, 'Опубликовать задачу студентам'),
        React.createElement(Badge, { kind: form.visible?'lime':'muted' }, form.visible?'Видна':'Черновик')
      )
    ),
  );
}

function TabCondition({ form, set }) {
  return React.createElement(React.Fragment, null,
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Условие задачи'),
      React.createElement('textarea', {
        className:'textarea',
        style:{fontFamily:'var(--font)', minHeight:140},
        value:form.desc, onChange:e=>set('desc', e.target.value),
        placeholder:'Опишите задачу в одном-двух абзацах. Поддерживается Markdown.'
      }),
      React.createElement('div', { className:'help' }, 'Совет: первая строка — короткая постановка («Дан массив…»). Дальше — детали.')
    ),
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Алгоритмическая сложность'),
      React.createElement('input', { className:'input mono', value:form.complexity, onChange:e=>set('complexity', e.target.value), placeholder:'O(log n)' })
    ),
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Ограничения'),
      React.createElement('textarea', {
        className:'textarea', style:{minHeight:96},
        value:form.constraints, onChange:e=>set('constraints', e.target.value),
        placeholder:'Каждая строка — отдельное ограничение'
      }),
    ),
    React.createElement('div', { className:'field', style:{marginBottom:0} },
      React.createElement('label', { className:'label' }, 'Подсказка для студента'),
      React.createElement('textarea', {
        className:'textarea', style:{fontFamily:'var(--font)', minHeight:80},
        value:form.hint, onChange:e=>set('hint', e.target.value),
        placeholder:'Появится во вкладке «Подсказки» у студента.'
      }),
    ),
  );
}

function TabTests({ form, set, runState }) {
  const lines = form.tests.split('\n').filter(l => l.trim());
  return React.createElement(React.Fragment, null,
    React.createElement('div', { className:'note', style:{marginBottom:14, fontSize:12.5} },
      React.createElement('b', null, 'Формат: '), React.createElement('span', { className:'mono' }, 'input -> expected'),
      ' · по одному тесту на строку. Поддерживаются массивы, числа, строки.'
    ),
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, `Тесты (${lines.length})`),
      React.createElement('textarea', {
        className:'textarea',
        style:{minHeight:200, fontSize:12.5},
        value:form.tests, onChange:e=>set('tests', e.target.value),
        placeholder:'[1,3,5,7,9],5 -> 2\n[2,4,6,8],8 -> 3'
      })
    ),
    runState && runState !== 'running' && React.createElement('div', { className:'field', style:{marginBottom:0} },
      React.createElement('label', { className:'label' }, 'Результат последнего прогона'),
      React.createElement('div', { className:'card', style:{padding:14} },
        React.createElement('div', { className:'between', style:{marginBottom:10} },
          React.createElement('b', { style:{fontSize:13.5} }, `${runState.pass} / ${runState.total} пройдено`),
          React.createElement(Badge, { kind: runState.pass===runState.total?'lime':'warn' },
            runState.pass===runState.total ? 'все OK' : 'есть ошибки')
        ),
        React.createElement('div', { className:'wrap', style:{gap:6} },
          runState.results.map(r => React.createElement('span', {
            key:r.idx,
            className:`badge ${r.pass?'badge-lime':'badge-danger'}`,
            style:{width:26,height:26,padding:0,justifyContent:'center',borderRadius:8}
          }, r.idx))
        )
      )
    )
  );
}

function TabReference({ form, set, ext, runState, runRef }) {
  return React.createElement(React.Fragment, null,
    React.createElement('div', { className:'between', style:{marginBottom:10} },
      React.createElement('div', null,
        React.createElement('div', { className:'label', style:{margin:0} }, 'Эталонное решение'),
        React.createElement('div', { className:'help', style:{margin:'4px 0 0'} }, `solution.${ext}`)
      ),
      React.createElement('button', { className:'btn btn-secondary btn-xs', onClick:runRef, disabled:runState==='running' },
        runState==='running' ? '⟳ Прогон…' : '▸ Прогнать'
      )
    ),
    React.createElement('div', { className:'editor', style:{minHeight:340, marginBottom:14} },
      React.createElement('div', { className:'eh' },
        React.createElement('span', { className:'t' }, `solution.${ext}`),
        React.createElement('span', { className:'mut3', style:{fontSize:11, marginLeft:'auto', fontFamily:'var(--mono)'} }, `${form.lang}`),
      ),
      React.createElement('textarea', {
        value:form.reference, onChange:e=>set('reference', e.target.value), spellCheck:false,
        style:{minHeight:300}
      })
    ),
    React.createElement('div', { className:'note warn', style:{margin:0, fontSize:12.5} },
      React.createElement('b', null, 'Важно: '),
      'эталон не показывается студенту по умолчанию — только во вкладке «Эталон», доступной как подсказка после первой неудачной попытки.'
    )
  );
}

function TabPlacement({ form, set, data }) {
  return React.createElement(React.Fragment, null,
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Каталог'),
      React.createElement('select', { className:'select', value:form.catalog, onChange:e=>set('catalog', e.target.value) },
        React.createElement('option', { value:'' }, '— Без каталога —'),
        data.catalogs.map(c => React.createElement('option', { key:c.id, value:c.id }, c.name))
      ),
      React.createElement('div', { className:'help' }, 'Каталог — это сборник задач. Назначайте каталоги группам, а не задачи поштучно.')
    ),
    React.createElement('div', { className:'field', style:{marginBottom:0} },
      React.createElement('label', { className:'label' }, 'Прямое назначение группам (опционально)'),
      React.createElement('div', { className:'grid', style:{gap:8} },
        data.groups.map(g => React.createElement('label', {
          key:g.id, className:'check-row',
          style:{padding:'10px 12px', border:'1px solid var(--border)', borderRadius:10, cursor:'pointer',
                  background: form.groups.includes(g.id) ? 'var(--purple-soft)' : 'transparent'}
        },
          React.createElement('span', { className:'checkbox '+(form.groups.includes(g.id)?'on':''), onClick:(e)=>{
            e.preventDefault();
            set('groups', form.groups.includes(g.id) ? form.groups.filter(x=>x!==g.id) : [...form.groups, g.id]);
          } }),
          React.createElement('div', { style:{flex:1} },
            React.createElement('div', { style:{fontSize:13.5, color:'var(--text)', fontWeight:600} }, g.name),
            React.createElement('div', { className:'mut3', style:{fontSize:12} }, `${g.students} студентов · ${g.teacher}`)
          )
        ))
      ),
      React.createElement('div', { className:'help', style:{marginTop:10} }, 'Студенты этих групп увидят задачу в своём списке вне зависимости от каталога.')
    ),
  );
}

/* ===== Live preview card (right column) ===== */
function LivePreviewCard({ form, ext }) {
  return React.createElement('div', null,
    React.createElement('div', { style:{display:'flex', alignItems:'center', gap:12, marginBottom:10, flexWrap:'wrap'} },
      React.createElement('h2', { style:{fontSize:22, fontWeight:800, letterSpacing:'-.4px', margin:0} }, form.title || 'Без названия'),
      React.createElement(DiffBadge, { diff:form.diff }),
      form.lang && React.createElement(Badge, { kind:'purple' }, form.lang),
    ),
    form.patterns.length > 0 && React.createElement('div', { className:'wrap', style:{marginBottom:12, gap:6} },
      form.patterns.map(p => React.createElement(Badge, { key:p, kind:'muted' }, p))
    ),
    React.createElement('p', {
      style:{fontSize:14, lineHeight:1.65, margin:'0 0 14px', color:'var(--text-2)', whiteSpace:'pre-wrap'}
    }, form.desc || React.createElement('span', { className:'mut3' }, '(заполните условие в левой панели)')),

    form.complexity && React.createElement('div', { className:'hint-block' },
      React.createElement('div', { className:'ttl' }, 'Сложность'),
      React.createElement('p', { style:{fontFamily:'var(--mono)'} }, form.complexity)
    ),

    form.constraints && React.createElement('div', { className:'hint-block' },
      React.createElement('div', { className:'ttl' }, 'Ограничения'),
      React.createElement('ul', { style:{margin:0, paddingLeft:18, fontSize:13.5, lineHeight:1.9, color:'var(--text-2)'} },
        form.constraints.split('\n').filter(l=>l.trim()).map((l,i) => React.createElement('li', { key:i }, l))
      )
    ),

    form.hint && React.createElement('div', { className:'hint-block' },
      React.createElement('div', { className:'ttl' }, 'Подсказка'),
      React.createElement('p', null, form.hint)
    ),

    // Test examples preview
    React.createElement('div', { className:'hint-block' },
      React.createElement('div', { className:'ttl' }, 'Примеры'),
      React.createElement('div', { className:'editor', style:{marginTop:6} },
        React.createElement('div', { className:'body' },
          form.tests.split('\n').filter(l=>l.trim()).slice(0,3).map((ln, i) => {
            const m = ln.split('->');
            return React.createElement('div', { key:i, className:'ln' },
              React.createElement('span', { className:'n' }, '›'),
              React.createElement('span', { className:'cm' }, `in: `),
              React.createElement('span', { className:'nm2' }, (m[0] || '').trim()),
              React.createElement('span', { className:'cm', style:{marginLeft:18} }, `out: `),
              React.createElement('span', { className:'fn' }, (m[1] || '').trim())
            );
          })
        )
      )
    ),

    React.createElement('div', { className:'eyebrow' }, 'Эталонное решение'),
    React.createElement('div', { className:'editor' },
      React.createElement('div', { className:'eh' }, React.createElement('span', { className:'t' }, `solution.${ext}`)),
      React.createElement('div', { className:'body' },
        form.reference.split('\n').map((ln, i) => React.createElement('div', { key:i, className:'ln' },
          React.createElement('span', { className:'n' }, i+1),
          React.createElement('span', { className:'mono', style:{color:'var(--text)'} }, ln || ' ')
        ))
      )
    ),
  );
}

/* ===== Bottom strip with the latest run result ===== */
function RunResultStrip({ runState, runRef }) {
  if (!runState) return React.createElement('div', { style:{padding:'12px 22px', borderTop:'1px solid var(--border)', background:'#0c111a', flex:'none', display:'flex', alignItems:'center', justifyContent:'space-between'} },
    React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, 'Прогон эталона не запускался'),
    React.createElement('button', { className:'btn btn-secondary btn-xs', onClick:runRef }, '▸ Прогнать сейчас')
  );
  if (runState === 'running') return React.createElement('div', { style:{padding:'12px 22px', borderTop:'1px solid var(--border)', background:'#0c111a', flex:'none', display:'flex', alignItems:'center', gap:10} },
    React.createElement('span', { className:'spinner', style:{width:16,height:16,borderWidth:2,margin:0} }),
    React.createElement('span', { className:'muted', style:{fontSize:13} }, 'Запуск эталонного решения по тестам…')
  );
  const allPass = runState.pass === runState.total;
  return React.createElement('div', { style:{padding:'12px 22px', borderTop:'1px solid var(--border)', background: allPass?'rgba(142,255,1,.04)':'rgba(255,77,106,.04)', flex:'none', display:'flex', alignItems:'center', justifyContent:'space-between'} },
    React.createElement('div', { className:'row', style:{gap:10} },
      React.createElement(Badge, { kind: allPass?'lime':'warn' }, React.createElement(Dot), `${runState.pass} / ${runState.total}`),
      React.createElement('span', { style:{fontSize:13, color: allPass?'var(--lime)':'var(--warning)', fontWeight:600} },
        allPass ? 'Эталон проходит все тесты' : 'Есть проваленные тесты — проверьте код или тесты')
    ),
    React.createElement('button', { className:'btn btn-ghost btn-xs', onClick:runRef }, 'Прогнать ещё раз')
  );
}

/* ===== Full-screen Preview Mode (as student sees it) ===== */
function TaskEditorPreview({ form, runState }) {
  const ext = form.lang==='Python'?'py':form.lang==='JavaScript'?'js':form.lang==='C++'?'cpp':'txt';
  return React.createElement('div', { style:{flex:1, display:'grid', gridTemplateColumns:'minmax(360px,1fr) 1.1fr', minHeight:0} },
    // Left: student view of the task
    React.createElement('div', { className:'task-left' },
      React.createElement('div', { className:'tabbar', style:{marginBottom:14} },
        React.createElement('button', { className:'on' }, 'Условие'),
        React.createElement('button', null, 'Примеры'),
        React.createElement('button', null, 'Подсказки'),
        React.createElement('button', null, 'Эталон'),
      ),
      React.createElement('div', { style:{display:'flex', alignItems:'center', gap:12, marginBottom:14, flexWrap:'wrap'} },
        React.createElement('h2', { style:{fontSize:22, fontWeight:800, letterSpacing:'-.4px', margin:0} }, form.title || 'Без названия'),
        React.createElement(DiffBadge, { diff:form.diff }),
      ),
      React.createElement('p', { style:{fontSize:14, lineHeight:1.65, margin:'0 0 16px', color:'var(--text-2)', whiteSpace:'pre-wrap'} }, form.desc || '(условие пустое)'),
      form.complexity && React.createElement(React.Fragment, null,
        React.createElement('div', { className:'eyebrow' }, 'Сложность'),
        React.createElement('p', { className:'mono', style:{margin:'0 0 14px', color:'var(--lime)'} }, form.complexity)
      ),
      form.constraints && React.createElement(React.Fragment, null,
        React.createElement('div', { className:'eyebrow' }, 'Ограничения'),
        React.createElement('ul', { className:'muted', style:{fontSize:13.5, margin:0, paddingLeft:18, lineHeight:1.9} },
          form.constraints.split('\n').filter(l=>l.trim()).map((l,i) => React.createElement('li', { key:i }, l))
        )
      ),
      form.patterns.length > 0 && React.createElement(React.Fragment, null,
        React.createElement('div', { className:'eyebrow' }, 'Паттерн'),
        React.createElement('div', { className:'wrap' }, form.patterns.map(p => React.createElement(Badge, { key:p, kind:'purple' }, p)))
      ),
    ),
    // Right: editor (read-only preview of what student sees)
    React.createElement('div', { className:'task-right' },
      React.createElement('div', { className:'row', style:{gap:6, padding:'12px 16px', borderBottom:'1px solid var(--border)', background:'#0c111a'} },
        React.createElement(Chip, { sm:true, active:true }, 'Код (Monaco)'),
        React.createElement(Chip, { sm:true }, 'Блоки'),
        React.createElement(Chip, { sm:true }, 'Блок-схема'),
        React.createElement('span', { className:'select inline', style:{marginLeft:'auto', display:'inline-flex', alignItems:'center'} }, form.lang),
      ),
      React.createElement('div', { className:'editor', style:{borderRadius:0, border:0, flex:1, minHeight:280} },
        React.createElement('div', { className:'eh' },
          React.createElement('span', { className:'t' }, `solution.${ext}`),
          React.createElement('span', { className:'mut3', style:{fontSize:11, marginLeft:'auto', fontFamily:'var(--mono)'} }, 'студенту даётся пустой редактор'),
        ),
        React.createElement('div', { className:'body', style:{padding:'14px 16px', color:'var(--text-3)', fontStyle:'italic'} },
          `# напишите свое решение на ${form.lang}…`
        )
      ),
      React.createElement('div', { className:'between', style:{padding:'12px 16px', borderTop:'1px solid var(--border)', background:'#0c111a'} },
        React.createElement('span', { className:'muted', style:{fontSize:13} }, 'Автосохранение'),
        React.createElement('button', { className:'btn btn-primary', disabled:true, style:{opacity:.85} }, '▸ Запуск')
      ),
      // Tests preview at the bottom
      runState && runState !== 'running' && React.createElement('div', { style:{padding:'14px 16px', borderTop:'1px solid var(--border)', background:'var(--surface)'} },
        React.createElement('div', { className:'between', style:{marginBottom:10} },
          React.createElement('b', { style:{fontSize:13.5} }, 'Тесты (предпросмотр прогона)'),
          React.createElement(Badge, { kind: runState.pass===runState.total?'lime':'warn' }, `${runState.pass} / ${runState.total} OK`)
        ),
        React.createElement('div', { className:'wrap', style:{gap:6} },
          runState.results.map(r => React.createElement('span', {
            key:r.idx, className:`badge ${r.pass?'badge-lime':'badge-danger'}`,
            style:{width:26,height:26,padding:0,justifyContent:'center',borderRadius:8}
          }, r.idx))
        )
      )
    )
  );
}

/* =========================================================
   CODE-ASSEMBLY EDITOR  (/teacher/code-assembly/:taskId/edit)
   ========================================================= */
function TeacherEditCodeAssemblyPage({ taskId }) {
  const { navigate } = useRouter();
  const toast = useToast();
  const data = window.MOCK;
  const t = data.tasks.find(x => x.id === +taskId) || data.tasks.find(t => t.type === 'code_assembly') || data.tasks[6];

  const [title, setTitle] = useStateT(t.title);
  const [lang, setLang] = useStateT(t.lang === '—' ? 'Python' : t.lang);
  const [desc, setDesc] = useStateT(t.desc);
  const [originalCode, setOriginalCode] = useStateT(`def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)`);
  const [distractors, setDistractors] = useStateT(['return n + 1','n = n - 1']);
  const [newDistractor, setNewDistractor] = useStateT('');

  const lines = originalCode.split('\n').filter(l => l.trim());

  return React.createElement('div', { style:{minHeight:'100vh', display:'flex', flexDirection:'column'} },
    React.createElement('div', { className:'topbar', style:{padding:'12px 20px'} },
      React.createElement('div', { className:'row' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>navigate('/teacher/profile', { query:{tab:'tasks'} }) }, '← Назад'),
        React.createElement('div', { className:'crumb' }, 'Code-assembly / ', React.createElement('b', null, title)),
        React.createElement(Badge, { kind:'purple' }, 'block_reorder')
      ),
      React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>{ toast.push({kind:'lime', title:'Сохранено'}); navigate('/teacher/profile', { query:{tab:'tasks'} }); } }, 'Сохранить')
    ),
    React.createElement('div', { style:{display:'grid', gridTemplateColumns:'1fr 1.1fr', flex:1, minHeight:0} },
      React.createElement('div', { style:{padding:'22px 24px', borderRight:'1px solid var(--border)', overflow:'auto'} },
        React.createElement('div', { className:'eyebrow', style:{marginTop:0} }, 'Параметры сборки'),
        React.createElement('div', { className:'field' }, React.createElement('label', { className:'label' }, 'Название'), React.createElement('input', { className:'input', value:title, onChange:e=>setTitle(e.target.value) })),
        React.createElement('div', { className:'field' }, React.createElement('label', { className:'label' }, 'Язык'),
          React.createElement('select', { className:'select', value:lang, onChange:e=>setLang(e.target.value) },
            ['Python','JavaScript','C++'].map(l => React.createElement('option', { key:l }, l))
          )
        ),
        React.createElement('div', { className:'field' }, React.createElement('label', { className:'label' }, 'Условие'),
          React.createElement('textarea', { className:'textarea', style:{fontFamily:'var(--font)'}, value:desc, onChange:e=>setDesc(e.target.value) })
        ),
        React.createElement('div', { className:'field' },
          React.createElement('label', { className:'label' }, 'Эталонный код'),
          React.createElement('textarea', { className:'textarea', style:{minHeight:160}, value:originalCode, onChange:e=>{ setOriginalCode(e.target.value); } })
        ),
        React.createElement('div', { className:'note warn', style:{marginBottom:16} },
          'При изменении эталонного кода блоки и шаблон сбрасываются на сервере. Используйте редактор блоков ниже, чтобы добавить дистракторы.'
        ),
        React.createElement('div', { className:'field', style:{marginBottom:0} },
          React.createElement('label', { className:'label' }, 'Блоки-дистракторы (лишние)'),
          React.createElement('div', { className:'wrap', style:{marginBottom:8} },
            distractors.map((d,i) => React.createElement('span', { key:i, className:'badge badge-muted', style:{height:28, padding:'0 12px', cursor:'pointer'}, onClick:()=>setDistractors(arr=>arr.filter((_,j)=>j!==i)) }, d, ' ✕'))
          ),
          React.createElement('div', { className:'row' },
            React.createElement('input', { className:'input mono', style:{height:34, fontSize:12.5}, placeholder:'lines that should NOT be used', value:newDistractor, onChange:e=>setNewDistractor(e.target.value) }),
            React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>{ if (newDistractor.trim()) { setDistractors(arr => [...arr, newDistractor]); setNewDistractor(''); } } }, '+ Добавить')
          ),
        ),
      ),
      React.createElement('div', { style:{padding:'22px 24px', background:'var(--bg-2)', overflow:'auto'} },
        React.createElement('div', { className:'between', style:{marginBottom:14} },
          React.createElement('div', { className:'eyebrow', style:{margin:0} }, 'Правильная сборка'),
          React.createElement('span', { className:'muted', style:{fontSize:12} }, 'на основе эталонного кода')
        ),
        React.createElement('div', { className:'grid', style:{gap:8} },
          lines.map((ln, i) => React.createElement('div', { key:i, className:'block-row', style:{marginLeft: ln.startsWith('    ') ? 18 : 0} },
            React.createElement('span', { className:'block-handle' }, '⠿'),
            React.createElement('span', { className:'badge badge-lime', style:{height:20, width:24, padding:0, justifyContent:'center', borderRadius:6} }, i+1),
            React.createElement('span', { className:'mono' }, ln.trim())
          ))
        ),
        React.createElement('div', { style:{marginTop:18, paddingTop:16, borderTop:'1px dashed var(--border-2)'} },
          React.createElement('span', { className:'muted', style:{fontSize:12.5, display:'block', marginBottom:8} }, 'Так увидит студент (перемешано):'),
          React.createElement('div', { className:'grid', style:{gap:6} },
            [...lines, ...distractors]
              .sort(() => Math.random() - 0.5)
              .map((ln, i) => React.createElement('div', { key:i, className:'mono', style:{background:'var(--surface-2)', border:'1px dashed var(--border-2)', borderRadius:9, padding:'9px 13px', fontSize:12.5, opacity:0.85} }, ln.trim()))
          )
        )
      )
    )
  );
}

Object.assign(window, {
  teacherSidebarItems,
  TeacherProfilePage, TeacherTasksPage, TeacherCatalogPage,
  TaskEditorPage, TeacherEditCodeAssemblyPage,
  TeacherTasksPanel, TeacherSolutionsPanel, TeacherAnalyticsPanel,
  TeacherCatalogsPanel, TeacherGroupsPanel
});
