/* global React */
/* Student profile — as a teacher sees it. Route: /students/:studentId (TEACHER/ADMIN) */
const { useState: useStSP, useMemo: useMmSP } = React;

function levelFor(solved) {
  if (solved >= 80) return { name:'Middle', tone:'lime' };
  if (solved >= 30) return { name:'Junior', tone:'lime' };
  if (solved >= 10) return { name:'Newcomer', tone:'purple' };
  return { name:'Beginner', tone:'muted' };
}

function StudentPublicProfilePage({ studentId }) {
  const { navigate } = window.useRouter();
  const toast = window.useToast();
  const data = window.MOCK;
  const student = data.adminUsers.find(u => u.id === +studentId && u.role === 'STUDENT')
    || data.adminUsers.find(u => u.role === 'STUDENT')
    || { id: 812, name:'Влада Максимова', email:'vlada@code.dev', initials:'В', role:'STUDENT', solved:128, groups:['ИВТ-301'], lastLogin:'сегодня' };

  const username = '@' + (student.email || 'student@code.dev').split('@')[0];
  const lvl = levelFor(student.solved || 0);
  const accuracy = 82;
  const streak = 7;

  // Aggregate this student's submissions (mock — reuse all submissions as if they're this student's)
  const submissions = data.submissions;

  // Recent actions (synthesised)
  const actions = useMmSP(() => ([
    { kind:'ok',   title:'Решила задачу',     task:'Двоичный поиск',       meta:'все 12 тестов пройдены', time:'2 ч назад' },
    { kind:'err',  title:'Не прошли тесты',   task:'Сумма двух чисел',     meta:'тест 4: ожидалось 8, получено 6', time:'вчера 18:05' },
    { kind:'warn', title:'Попытка отправки',  task:'Перевод в двоичную',   meta:'TLE на тесте 9',         time:'вчера 16:30' },
    { kind:'ok',   title:'Решила задачу',     task:'Блок-схема цикла',     meta:'с первой попытки',       time:'19 мая' },
    { kind:'ok',   title:'Решила задачу',     task:'Линейный поиск',       meta:'2 попытки',              time:'15 мая' },
  ]), []);

  const skills = useMmSP(() => ([
    { name:'Алгоритмы',          pct:78, tasks:'42 / 54',  tone:'' },
    { name:'Структуры данных',   pct:54, tasks:'18 / 33',  tone:'pp' },
    { name:'Строки',             pct:91, tasks:'21 / 23',  tone:'' },
    { name:'Графы',              pct:32, tasks:'6 / 19',   tone:'pp' },
    { name:'Динамическое прог.', pct:18, tasks:'3 / 17',   tone:'low' },
  ]), []);

  const studentGroups = (student.groups || []).map(name => data.groups.find(g => g.name === name)).filter(Boolean);

  const [msgOpen, setMsgOpen] = useStSP(false);
  const [msg, setMsg] = useStSP('');
  const sendMsg = () => {
    if (!msg.trim()) return;
    toast.push({ kind:'lime', title:'Сообщение отправлено', body:`${student.name} увидит его при следующем входе.` });
    setMsg(''); setMsgOpen(false);
  };

  return React.createElement('div', { className:'app-root' },
    React.createElement(window.Sidebar, { items: window.teacherSidebarItems(), role:'TEACHER', brandPP:true }),
    React.createElement('div', null,
      React.createElement(window.Topbar, { crumbHome:'Преподаватель', crumbCurrent:'Студент' }),
      React.createElement('div', { className:'content' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:14}, onClick:()=>history.back() }, '← Назад'),

        // ===== HERO =====
        React.createElement('div', { className:'spp-hero' },
          React.createElement('div', { className:'spp-hero-main' },
            React.createElement('div', { className:'spp-avatar' }, student.initials),
            React.createElement('div', { style:{minWidth:0} },
              React.createElement('h1', { className:'spp-name' }, student.name),
              React.createElement('p', { className:'spp-username' }, username),
              React.createElement('div', { className:'spp-meta' },
                React.createElement(window.RoleBadge, { role:'STUDENT' }),
                React.createElement(window.Badge, { kind: lvl.tone }, 'Уровень · ' + lvl.name),
                student.blocked
                  ? React.createElement(window.Badge, { kind:'danger' }, window.Dot(), 'Заблокирован')
                  : React.createElement('span', { className:'online-dot' }, React.createElement('i'), `последний вход — ${student.lastLogin || 'сегодня'}`),
              )
            )
          ),
          // quick stats
          React.createElement('div', { className:'spp-stats' },
            stat('Решено задач', student.solved || 128, 'lime'),
            stat('Точность',     accuracy + '%',        ''),
            stat('Серия дней',   streak + ' 🔥',        'lime'),
            stat('Попыток',      String(submissions.length * 14), 'purple'),
          )
        ),

        // ===== TWO-COLUMN =====
        React.createElement('div', { className:'spp-grid' },
          // LEFT main column
          React.createElement('div', { className:'grid', style:{gap:18} },
            // Activity
            React.createElement('div', { className:'spp-section' },
              React.createElement('div', { className:'spp-section-h' },
                React.createElement('b', null, 'Активность'),
                React.createElement('span', { className:'small' }, 'последние 26 недель')
              ),
              React.createElement(window.ContribGraph, { weeks: 26 }),
              React.createElement('div', { style:{marginTop:18, paddingTop:18, borderTop:'1px solid var(--border)'} },
                React.createElement('div', { className:'small', style:{marginBottom:10, fontWeight:700, letterSpacing:'.06em', textTransform:'uppercase', color:'var(--text-3)'} }, 'Последние действия'),
                actions.map((a,i) => React.createElement('div', { key:i, className:`spp-action ${a.kind}` },
                  React.createElement('div', { className:'ico' }, a.kind==='ok'?'✓':a.kind==='warn'?'⌛':'!'),
                  React.createElement('div', { className:'body' },
                    React.createElement('div', null, a.title, ' ', React.createElement('b', null, '«'+a.task+'»')),
                    React.createElement('div', { className:'meta' }, a.meta)
                  ),
                  React.createElement('time', null, a.time)
                ))
              )
            ),

            // Solutions
            React.createElement('div', { className:'spp-section' },
              React.createElement('div', { className:'spp-section-h' },
                React.createElement('b', null, 'Последние решения'),
                React.createElement('span', { className:'small' }, `всего ${submissions.length}`)
              ),
              React.createElement('table', { className:'table' },
                React.createElement('thead', null, React.createElement('tr', null,
                  React.createElement('th', null, 'Задача'),
                  React.createElement('th', null, 'Язык'),
                  React.createElement('th', null, 'Попытка'),
                  React.createElement('th', null, 'Статус'),
                  React.createElement('th', null, 'Дата'),
                )),
                React.createElement('tbody', null, submissions.map(s => React.createElement('tr', {
                  key:s.id, onClick:()=>navigate(`/tasks/${s.taskId}`)
                },
                  React.createElement('td', { className:'t-name' }, s.title),
                  React.createElement('td', { className:'muted' }, s.lang),
                  React.createElement('td', { className:'mono mut3' }, '#'+s.attempt),
                  React.createElement('td', null, React.createElement(window.StatusBadge, { status:s.status })),
                  React.createElement('td', { className:'muted' }, s.date)
                )))
              )
            ),
          ),

          // RIGHT sidebar
          React.createElement('div', { className:'grid', style:{gap:18} },
            // Teacher actions
            React.createElement('div', { className:'spp-section compact' },
              React.createElement('div', { className:'grid', style:{gap:8} },
                React.createElement('button', { className:'btn btn-primary btn-full', onClick:()=>setMsgOpen(true) }, '✉ Написать студенту'),
                React.createElement('button', { className:'btn btn-secondary btn-full', onClick:()=>toast.push({kind:'info', title:'Аналитика', body:'Откроется расширенный отчёт по этому студенту.'}) }, 'Подробная аналитика'),
                React.createElement('button', { className:'btn btn-ghost btn-full', onClick:()=>navigate(`/admin/users/${student.id}`) }, 'Карточка в админке')
              )
            ),

            // Skills
            React.createElement('div', { className:'spp-section' },
              React.createElement('div', { className:'spp-section-h' },
                React.createElement('b', null, 'Прогресс по темам')
              ),
              skills.map((s, i) => React.createElement('div', { key:i, className:'spp-skill' },
                React.createElement('div', { className:'spp-skill-h' },
                  React.createElement('span', null,
                    React.createElement('span', { className:'name' }, s.name),
                    React.createElement('span', { className:'sub' }, s.tasks)
                  ),
                  React.createElement('span', { className: `pct ${s.tone}` }, s.pct + '%')
                ),
                React.createElement('div', { className:'progress ' + (s.tone==='pp'?'pp':'') },
                  React.createElement('i', { style:{ width: s.pct + '%', background: s.tone==='low'?'linear-gradient(90deg,var(--warning),#ffd479)':null } })
                )
              ))
            ),

            // Groups
            React.createElement('div', { className:'spp-section' },
              React.createElement('div', { className:'spp-section-h' },
                React.createElement('b', null, 'Группы'),
                React.createElement('span', { className:'small' }, `${studentGroups.length}`)
              ),
              studentGroups.length === 0
                ? React.createElement('p', { className:'mut3', style:{fontSize:13, margin:0} }, 'Студент не состоит ни в одной группе.')
                : studentGroups.map(g => React.createElement('div', {
                    key:g.id, className:'tpp-listitem',
                    onClick:()=>navigate(`/student/groups/${g.id}`)
                  },
                    React.createElement('div', { className:'ico' }, g.name.split(' ')[0].slice(0,2).toUpperCase()),
                    React.createElement('div', { className:'body' },
                      React.createElement('b', null, g.name),
                      React.createElement('span', null, `${g.teacher} · ${g.students} студентов`)
                    ),
                    React.createElement('span', { className:'arr' }, '→')
                  ))
            ),
          )
        )
      )
    ),

    // ===== Message Modal =====
    React.createElement(window.Modal, {
      open: msgOpen, onClose:()=>setMsgOpen(false),
      title: `Сообщение для ${student.name}`,
      width: 520,
      footer: React.createElement(React.Fragment, null,
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setMsgOpen(false) }, 'Отмена'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:sendMsg, disabled:!msg.trim() }, 'Отправить')
      )
    },
      React.createElement('div', { className:'row', style:{gap:12, marginBottom:14, paddingBottom:14, borderBottom:'1px solid var(--border)'} },
        React.createElement('div', { className:'avatar', style:{width:38, height:38, fontSize:14, borderRadius:12} }, student.initials),
        React.createElement('div', null,
          React.createElement('div', { style:{fontSize:14, fontWeight:600} }, student.name),
          React.createElement('div', { className:'mut3', style:{fontSize:12} }, username + ' · ' + lvl.name)
        )
      ),
      React.createElement('textarea', {
        className:'textarea', style:{fontFamily:'var(--font)', minHeight:120, fontSize:14},
        placeholder:'Например: «Видела вашу попытку по двоичному поиску — давайте разберём…»',
        value:msg, onChange:e=>setMsg(e.target.value), autoFocus:true
      }),
      React.createElement('p', { className:'mut3', style:{fontSize:11.5, margin:'10px 0 0'} },
        'Будьте конкретны и доброжелательны — это самый быстрый способ помочь студенту.'
      )
    )
  );
}

function stat(label, value, tone) {
  return React.createElement('div', { className:'spp-stat' },
    React.createElement('div', { className: 'v ' + (tone || '') }, value),
    React.createElement('div', { className:'l' }, label)
  );
}

Object.assign(window, { StudentPublicProfilePage });
