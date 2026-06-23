/* global React */
const { useState: useStateL, useEffect: useEffectL } = React;

/* =========================================================
   Shared bits
   ========================================================= */
function TrackProgressBar({ pct, pp }) {
  return React.createElement('div', { className:'progress '+(pp?'pp':'') },
    React.createElement('i', { style:{ width: Math.max(0, Math.min(100, pct)) + '%' } })
  );
}

// Subtle language switcher for the track hero — compact "Py ▾".
const TRACK_LANGS = [
  { id:'Python', glyph:'Py', soon:false },
  { id:'Pascal', glyph:'Pas', soon:false },
  { id:'C++',    glyph:'C++', soon:true },
  { id:'C#',     glyph:'C#',  soon:true },
  { id:'Java',   glyph:'Jv',  soon:true },
];
function LangMini({ lang, onChange }) {
  const [open, setOpen] = useStateL(false);
  const ref = React.useRef(null);
  useEffectL(() => {
    const onDoc = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);
  const cur = TRACK_LANGS.find(l => l.id === lang) || TRACK_LANGS[0];
  return React.createElement('div', { className:'lang-mini', ref },
    React.createElement('button', { className:'lang-mini-btn', onClick:()=>setOpen(o=>!o), title:'Сменить язык' },
      React.createElement('span', null, cur.id),
      React.createElement('span', { style:{fontSize:10, color:'var(--text-3)'} }, '▾')
    ),
    open && React.createElement('div', { className:'lang-mini-menu' },
      TRACK_LANGS.map(l => React.createElement('div', {
        key:l.id,
        className:'lang-mini-opt '+(l.id===lang?'on':''),
        onClick:()=>{ if (l.soon) return; onChange(l.id); setOpen(false); }
      },
        React.createElement('span', { className:'g' }, l.glyph),
        l.id,
        l.soon && React.createElement('span', { className:'soon' }, 'скоро')
      ))
    )
  );
}

// Fake async loader so we can demo loading/error states like the real API.
function useFakeFetch(producer, deps, { failKey } = {}) {
  const [state, setState] = useStateL({ loading:true, error:null, data:null });
  useEffectL(() => {
    let alive = true;
    setState({ loading:true, error:null, data:null });
    const forceFail = failKey && new URLSearchParams(window.location.hash.split('?')[1] || '').get(failKey) === '1';
    const t = setTimeout(() => {
      if (!alive) return;
      if (forceFail) { setState({ loading:false, error:'Не удалось загрузить данные. Попробуйте обновить страницу.', data:null }); return; }
      setState({ loading:false, error:null, data: producer() });
    }, 380);
    return () => { alive = false; clearTimeout(t); };
  }, deps); // eslint-disable-line
  return state;
}

function CurriculumStates({ loading, error, empty, loadingText, children, onRetry }) {
  if (loading) {
    return React.createElement('div', { className:'card card-pad', style:{display:'grid', placeItems:'center', gap:14, minHeight:240} },
      React.createElement('div', { className:'spinner' }),
      React.createElement('span', { className:'muted', style:{fontSize:13.5} }, loadingText || 'Загрузка…')
    );
  }
  if (error) {
    return React.createElement('div', { className:'card card-pad' },
      React.createElement(EmptyState, {
        icon:'!', title:'Ошибка загрузки', text:error,
        action: React.createElement('button', { className:'btn btn-primary', onClick:onRetry }, '↻ Повторить')
      })
    );
  }
  if (empty) {
    return React.createElement('div', { className:'card card-pad' },
      React.createElement(EmptyState, { icon:'📚', title:'Пока пусто', text:'Здесь появятся материалы, как только они будут добавлены.' })
    );
  }
  return children;
}

/* =========================================================
   PASCAL HUB  ( /learn/pascal )
   ========================================================= */
function PascalLanguagePage() {
  const { navigate } = useRouter();
  const toast = useToast();
  const { loading, error, data } = useFakeFetch(() => window.MOCK.pascalTrack, [], { failKey:'fail' });
  const [, force] = useStateL(0);
  const [lang, setLang] = useStateL('Python');
  const curLang = TRACK_LANGS.find(l => l.id === lang) || TRACK_LANGS[0];

  const openChapter = (ch) => navigate(`/learn/pascal/${ch.slug}`);
  const continueChapter = (ch) => {
    if (!ch.nextTaskId) return;
    toast.push({ kind: ch.completed ? 'info' : 'lime', title:'Открываем задачу', body:ch.title });
    navigate(`/tasks/${ch.nextTaskId}`);
  };

  // track-level "continue learning" → first unfinished chapter
  const nextChapter = data && data.chapters.find(c => !c.completed && c.nextTaskId);

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: studentSidebarItems(), role:'STUDENT' }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Обучение', crumbCurrent:'Pascal' }),
      React.createElement('div', { className:'content', style:{maxWidth:920} },
        React.createElement(CurriculumStates, {
          loading, error, loadingText:'Загрузка трека…', onRetry:()=>force(x=>x+1)
        },
          data && React.createElement(React.Fragment, null,
            // HERO
            React.createElement('div', { className:'track-hero', style:{marginBottom:24} },
              React.createElement('div', { style:{display:'flex', gap:18, alignItems:'flex-start', flexWrap:'wrap'} },
                React.createElement('div', { className:'track-glyph' }, curLang.glyph),
                React.createElement('div', { style:{flex:'1 1 280px', minWidth:0} },
                  React.createElement('div', { className:'row', style:{gap:10, marginBottom:6} },
                    React.createElement(Badge, { kind:'purple' }, 'Учебный трек'),
                    data.passed >= data.total && React.createElement(Badge, { kind:'lime' }, '✓ Трек пройден'),
                    React.createElement(LangMini, { lang, onChange:setLang })
                  ),
                  React.createElement('h1', { style:{fontSize:30, fontWeight:800, letterSpacing:'-.8px', margin:'0 0 6px'} },
                    curLang.id
                  ),
                  React.createElement('p', { className:'muted', style:{fontSize:14.5, margin:0, maxWidth:440} },
                    'Линейный путь от первой программы до процедур и рекурсии. Проходите сборники по порядку.'
                  ),
                ),
                // aggregate progress dial
                React.createElement('div', { style:{textAlign:'right', minWidth:140} },
                  React.createElement('div', { style:{fontSize:34, fontWeight:800, letterSpacing:'-.5px', color:'var(--lime)'} },
                    Math.round((data.passed/data.total)*100) + '%'
                  ),
                  React.createElement('div', { className:'mono mut3', style:{fontSize:12.5, marginBottom:10} },
                    `${data.passed}/${data.total} задач`
                  ),
                  React.createElement(TrackProgressBar, { pct: (data.passed/data.total)*100 })
                ),
              ),
              nextChapter && React.createElement('div', { style:{marginTop:22, paddingTop:20, borderTop:'1px solid var(--border)', display:'flex', justifyContent:'space-between', alignItems:'center', gap:14, flexWrap:'wrap'} },
                React.createElement('div', null,
                  React.createElement('div', { className:'mut3', style:{fontSize:12, textTransform:'uppercase', letterSpacing:'.06em', marginBottom:3} }, 'Продолжить с'),
                  React.createElement('b', { style:{fontSize:15} }, `${nextChapter.n}. ${nextChapter.title}`)
                ),
                React.createElement('button', { className:'btn btn-primary', onClick:()=>continueChapter(nextChapter) }, '▸ Продолжить обучение')
              )
            ),

            // CHAPTERS roadmap
            React.createElement('div', { className:'between', style:{margin:'0 0 16px'} },
              React.createElement('h2', { style:{fontSize:18, fontWeight:700, margin:0} }, 'Сборники'),
              React.createElement('span', { className:'mut3', style:{fontSize:13} }, `${data.chapters.length} глав`)
            ),
            data.chapters.length === 0
              ? React.createElement('div', { className:'card card-pad' }, React.createElement(EmptyState, { icon:'📚', title:'Сборников пока нет', text:'Материалы Pascal появятся здесь, когда преподаватель их добавит.' }))
              : React.createElement('div', { className:'roadmap' },
                data.chapters.map((ch) => React.createElement(ChapterCard, {
                  key:ch.id, ch,
                  isCurrent: nextChapter && ch.id === nextChapter.id,
                  onOpen:()=>openChapter(ch), onContinue:()=>continueChapter(ch)
                }))
              )
          )
        )
      )
    )
  );
}

function ChapterCard({ ch, isCurrent, onOpen, onContinue }) {
  const pct = Math.round((ch.passed/ch.total)*100);
  const cls = 'chapter-card ' + (ch.completed ? 'done' : isCurrent ? 'current' : '');
  return React.createElement('div', { className:cls },
    React.createElement('div', { className:'chapter-node' },
      React.createElement('div', { className:'chapter-num' }, ch.completed ? '✓' : ch.n),
      React.createElement('div', { className:'chapter-connector' })
    ),
    React.createElement('div', { style:{minWidth:0} },
      React.createElement('div', { className:'between', style:{gap:12, marginBottom:4, alignItems:'flex-start'} },
        React.createElement('div', { style:{minWidth:0} },
          React.createElement('div', { className:'row', style:{gap:8, marginBottom:3, flexWrap:'wrap'} },
            React.createElement('b', { style:{fontSize:16} }, ch.title),
            ch.completed
              ? React.createElement(Badge, { kind:'lime' }, '✓ Все пройдены')
              : isCurrent ? React.createElement(Badge, { kind:'purple' }, 'Текущий') : null
          ),
          React.createElement('p', { className:'muted', style:{fontSize:13.5, margin:0} }, ch.desc)
        ),
      ),
      React.createElement('div', { style:{display:'grid', gridTemplateColumns:'1fr auto', gap:14, alignItems:'center', marginTop:12} },
        React.createElement('div', null,
          React.createElement('div', { className:'between', style:{fontSize:12, marginBottom:6} },
            React.createElement('span', { className:'mut3 mono' }, `${ch.passed}/${ch.total} · ${pct}%`),
          ),
          React.createElement(TrackProgressBar, { pct, pp: !ch.completed && isCurrent })
        ),
        React.createElement('div', { className:'row', style:{gap:8} },
          React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:onOpen }, 'Открыть сборник'),
          React.createElement('button', { className:'btn btn-primary btn-sm', onClick:onContinue, disabled: !ch.nextTaskId }, ch.button)
        )
      )
    )
  );
}

/* =========================================================
   PASCAL CHAPTER SHOWCASE  ( /learn/pascal/:chapterSlug )
   ========================================================= */
function PascalShowcasePage({ chapterSlug }) {
  const { navigate } = useRouter();
  const toast = useToast();
  const { user } = useAuth();
  const { loading, error, data } = useFakeFetch(
    () => window.MOCK.pascalShowcase[chapterSlug] || null,
    [chapterSlug], { failKey:'fail' }
  );
  const [, force] = useStateL(0);
  const isGuest = !user; // guest = no progress card / no statuses

  const openTask = (taskId) => {
    navigate(`/tasks/${taskId}`); // returnTo:/learn/pascal/:slug, navigationMode:curriculum, collectionId (real app passes via state)
  };
  const continueCollection = () => {
    if (!data?.nextTaskId) return;
    toast.push({ kind:'lime', title:'Открываем задачу', body:data.title });
    navigate(`/tasks/${data.nextTaskId}`);
  };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: studentSidebarItems(), role:'STUDENT' }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Обучение', crumbCurrent:'Pascal · сборник' }),
      React.createElement('div', { className:'content', style:{maxWidth:960} },
        React.createElement(CurriculumStates, {
          loading, error, empty: !loading && !error && !data,
          loadingText:'Загрузка сборника…', onRetry:()=>force(x=>x+1)
        },
          data && React.createElement(React.Fragment, null,
            // back + header
            React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:14}, onClick:()=>navigate('/learn/pascal') }, '← Все сборники'),
            React.createElement('div', { className:'page-h' },
              React.createElement('div', null,
                React.createElement('div', { className:'row', style:{gap:8, marginBottom:8, flexWrap:'wrap'} },
                  React.createElement(Badge, { kind:'purple' }, `Сборник «${data.title}»`),
                  React.createElement('span', { className:'mut3', style:{fontSize:13} }, `${data.total} задач`),
                ),
                React.createElement('h1', { style:{margin:'0 0 4px'} },
                  React.createElement('span', { className:'mut3', style:{fontWeight:600, fontSize:18} }, 'Pascal / '),
                  data.title
                ),
                React.createElement('p', null, data.desc)
              ),
              React.createElement('div', { className:'wrap' },
                React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>navigate('/learn/pascal') }, 'Все сборники'),
                React.createElement('button', { className:'btn btn-primary btn-sm', onClick:continueCollection, disabled: !data.nextTaskId }, '▸ ', data.button)
              )
            ),

            // progress card (only if authed)
            !isGuest && React.createElement('div', { className:'card card-pad', style:{marginBottom:24} },
              React.createElement('div', { className:'between', style:{marginBottom:12, flexWrap:'wrap', gap:10} },
                React.createElement('b', { style:{fontSize:14} }, 'Прогресс сборника'),
                React.createElement('span', { className:'mono mut3', style:{fontSize:13} }, `${data.passed}/${data.total} · ${Math.round((data.passed/data.total)*100)}%`)
              ),
              React.createElement(TrackProgressBar, { pct:(data.passed/data.total)*100 })
            ),
            isGuest && React.createElement('div', { className:'note', style:{marginBottom:24} },
              React.createElement('b', null, 'Вы не авторизованы. '), 'Войдите, чтобы отслеживать прогресс по задачам этого сборника.'
            ),

            // sections
            React.createElement('div', { className:'grid', style:{gap:30} },
              data.sections.map((sec, i) => React.createElement(SubtopicSection, {
                key:sec.id, section:sec, num:i+1, isGuest, onOpenTask:openTask
              }))
            )
          )
        )
      )
    )
  );
}

function SubtopicSection({ section, num, isGuest, onOpenTask }) {
  const passed = section.tasks.filter(t => t.status === 'passed').length;
  const total = section.tasks.length;
  const pct = Math.round((passed/total)*100);
  return React.createElement('section', null,
    React.createElement('div', { className:'section-head' },
      React.createElement('div', { className:'row', style:{gap:10} },
        React.createElement('span', { className:'section-num' }, num),
        React.createElement('h2', { style:{fontSize:16, fontWeight:700, margin:0} }, section.name)
      ),
      !isGuest && React.createElement('div', { className:'row', style:{gap:10, minWidth:180} },
        React.createElement('span', { className:'mono mut3', style:{fontSize:12, whiteSpace:'nowrap'} }, `${passed}/${total} · ${pct}%`),
        React.createElement('div', { style:{width:120} }, React.createElement(TrackProgressBar, { pct }))
      )
    ),
    React.createElement('div', { className:'task-grid' },
      section.tasks.map(t => React.createElement(TaskCard, { key:t.task_id, task:t, isGuest, onClick:()=>onOpenTask(t.task_id) }))
    )
  );
}

function TaskCard({ task, isGuest, onClick }) {
  const meta = window.MOCK.actionMeta[task.action] || { label:task.action, kind:'muted', icon:'•' };
  const showStatus = !isGuest && task.status && task.status !== 'not_started';
  const cls = 'task-card ' + (!isGuest ? (task.status === 'passed' ? 'passed' : task.status === 'failed' ? 'failed' : '') : '');
  return React.createElement('button', { className:cls, onClick },
    // top row: action badge + difficulty + status
    React.createElement('div', { className:'between', style:{gap:8} },
      React.createElement('span', { className:`action-badge badge-${meta.kind}` }, meta.icon, ' ', meta.label),
      React.createElement('div', { className:'row', style:{gap:6} },
        React.createElement(DiffBadge, { diff:task.diff }),
        showStatus && (task.status === 'passed'
          ? React.createElement(Badge, { kind:'lime' }, '✓ Пройдено')
          : React.createElement(Badge, { kind:'warn' }, 'Ещё раз'))
      )
    ),
    // title + skill
    React.createElement('div', null,
      React.createElement('b', { style:{fontSize:15, display:'block'} }, task.title),
      React.createElement('span', { style:{fontSize:12.5, color:'#b89bff', fontWeight:600} }, task.skill)
    ),
    // action description
    React.createElement('p', { className:'muted', style:{fontSize:13, margin:0} }, task.desc),
    // instruction preview
    React.createElement('p', { className:'mut3 clamp2', style:{fontSize:12.5, margin:0, lineHeight:1.5} }, task.instruction),
    // footer: subtopic
    React.createElement('div', { className:'row', style:{gap:6, marginTop:2, paddingTop:10, borderTop:'1px solid var(--border)'} },
      React.createElement('span', { className:'mut3', style:{fontSize:11.5} }, '◷ ', task.subtopic)
    )
  );
}

Object.assign(window, { PascalLanguagePage, PascalShowcasePage });
