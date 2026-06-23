/* global React */
const { useState: useStateA, useMemo: useMemoA, useEffect: useEffectA } = React;

function adminSidebarItems() {
  return [
    { divider:'Администратор' },
    { to:'/admin',                  label:'Обзор',                   matches:(p)=>p==='/admin' },
    { to:'/admin/users',            label:'Пользователи',            matches:(p)=>p.startsWith('/admin/users') },
    { to:'/admin/teacher-requests', label:'Заявки преподавателей',   matches:(p)=>p.startsWith('/admin/teacher-requests') },
    { to:'/admin/assignments',      label:'Задания',                 matches:(p)=>p.startsWith('/admin/assignments') },
    { to:'/admin/statistics',       label:'Статистика',              matches:(p)=>p.startsWith('/admin/statistics') },
    { to:'/admin/create-teacher',   label:'Создать преподавателя',   matches:(p)=>p.startsWith('/admin/create-teacher') },
    { divider:'Платформа' },
    { to:'/',                       label:'← К задачам' },
  ];
}

/* =========================================================
   ADMIN OVERVIEW
   ========================================================= */
function AdminOverviewPage() {
  const { navigate } = useRouter();
  const data = window.MOCK;
  const stats = data.adminStats;
  const requests = data.teacherRequests.filter(r => r.status === 'pending');

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Админка', crumbCurrent:'Обзор' }, React.createElement(RoleBadge, { role:'ADMIN' })),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, { title:'Обзор платформы', subtitle:'Сводка по пользователям, задачам и активности' }),
        React.createElement('div', { className:'cards3', style:{marginBottom:16} },
          React.createElement(StatCard, { label:'Пользователей', value:stats.users.toLocaleString('ru'), badge:'+62 за неделю', badgeKind:'lime' }),
          React.createElement(StatCard, { label:'Преподавателей', value:stats.teachers, badge:`${stats.pendingTeacherRequests} заявок`, badgeKind:'purple' }),
          React.createElement(StatCard, { label:'Задач в базе', value:stats.tasks, badge:'+18 за месяц', badgeKind:'muted' }),
        ),
        React.createElement('div', { style:{display:'grid', gridTemplateColumns:'1.4fr 1fr', gap:16, alignItems:'start'} },
          React.createElement('div', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:15} }, 'Регистрации за 30 дней'),
            React.createElement('div', { style:{display:'flex', alignItems:'flex-end', gap:4, height:140, marginTop:16} },
              [40,55,48,80,62,70,100,58,66,30,72,90,55,68,42,88,62,46,72,55,80,65,45,70,52,62,77,40,58,72].map((v,i) =>
                React.createElement('div', { key:i, style:{flex:1, background: v>=80?'var(--lime)':'var(--purple)', height:v+'%', borderRadius:4, opacity: v<35?0.4:1} })
              )
            ),
            React.createElement('div', { className:'wrap', style:{marginTop:14, gap:18, fontSize:12.5, color:'var(--text-2)'} },
              React.createElement('span', { style:{display:'inline-flex', alignItems:'center', gap:7} }, React.createElement('i', { style:{width:11, height:11, borderRadius:3, background:'var(--purple)'} }), 'Регистрации'),
              React.createElement('span', { style:{display:'inline-flex', alignItems:'center', gap:7} }, React.createElement('i', { style:{width:11, height:11, borderRadius:3, background:'var(--lime)'} }), 'Пики'),
            )
          ),
          React.createElement('div', { className:'card card-pad' },
            React.createElement('div', { className:'between', style:{marginBottom:14} },
              React.createElement('b', { style:{fontSize:15} }, 'Заявки преподавателей'),
              React.createElement('a', { onClick:()=>navigate('/admin/teacher-requests'), style:{fontSize:12.5, color:'var(--lime)', cursor:'pointer'} }, 'Все →')
            ),
            requests.length === 0
              ? React.createElement('p', { className:'muted', style:{fontSize:13, margin:0} }, 'Новых заявок нет.')
              : React.createElement('div', { className:'grid', style:{gap:10} },
                requests.slice(0,3).map(r => React.createElement('div', { key:r.id, className:'between' },
                  React.createElement('div', { className:'row', style:{gap:10} },
                    React.createElement('span', { className:'avatar pp', style:{width:32, height:32, fontSize:13} }, r.name[0]),
                    React.createElement('div', null,
                      React.createElement('div', { style:{fontSize:13.5, fontWeight:600} }, r.name),
                      React.createElement('div', { className:'mut3', style:{fontSize:12} }, r.dept)
                    )
                  ),
                  React.createElement('div', { className:'row' },
                    React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>navigate('/admin/teacher-requests') }, '✓'),
                    React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>navigate('/admin/teacher-requests') }, '✕')
                  )
                ))
              )
          ),
        ),
        React.createElement('div', { className:'cards2', style:{marginTop:16} },
          React.createElement('div', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:14} }, 'Роли'),
            React.createElement('div', { className:'grid', style:{gap:12, marginTop:14} },
              stats.breakdown.roles.map(r => React.createElement('div', { key:r.label },
                React.createElement('div', { className:'between', style:{fontSize:13, marginBottom:6} },
                  React.createElement('span', { className:'muted' }, r.label),
                  React.createElement('b', { className:'mono' }, r.value)
                ),
                React.createElement('div', { className:'progress '+(r.color==='purple'?'pp':'') },
                  React.createElement('i', { style:{width: Math.min(100, (r.value/stats.users)*100*4) + '%', background: r.color==='danger'?'var(--danger)':null} })
                )
              ))
            )
          ),
          React.createElement('div', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:14} }, 'Типы задач'),
            React.createElement('div', { className:'grid', style:{gap:12, marginTop:14} },
              stats.breakdown.taskTypes.map((r,i) => React.createElement('div', { key:r.label },
                React.createElement('div', { className:'between', style:{fontSize:13, marginBottom:6} },
                  React.createElement('span', { className:'muted mono' }, r.label),
                  React.createElement('b', { className:'mono' }, r.value)
                ),
                React.createElement('div', { className:'progress '+(i%2?'pp':'') },
                  React.createElement('i', { style:{width: Math.min(100,(r.value/stats.tasks)*100*2) + '%'} })
                )
              ))
            )
          )
        ),
        React.createElement('div', { className:'cards3', style:{marginTop:16} },
          quickLink(()=>navigate('/admin/users'), '👥', 'Пользователи', 'Поиск, фильтры, действия'),
          quickLink(()=>navigate('/admin/assignments'), '📚', 'Задания', 'Workflow, версии, архив'),
          quickLink(()=>navigate('/admin/create-teacher'), '＋', 'Создать преподавателя', 'Минуя заявки'),
        )
      )
    )
  );
}
function quickLink(onClick, icon, title, sub) {
  return React.createElement('button', { onClick, className:'card card-pad', style:{textAlign:'left', cursor:'pointer', transition:'.15s'},
    onMouseEnter:e=>e.currentTarget.style.borderColor='rgba(139,83,254,.4)',
    onMouseLeave:e=>e.currentTarget.style.borderColor='var(--border)'
  },
    React.createElement('div', { style:{fontSize:22, marginBottom:8} }, icon),
    React.createElement('b', null, title),
    React.createElement('p', { className:'mut3', style:{fontSize:12.5, margin:'4px 0 0'} }, sub)
  );
}

/* =========================================================
   ADMIN USERS LIST
   ========================================================= */
function AdminUsersPage() {
  const { navigate } = useRouter();
  const data = window.MOCK;
  const [search, setSearch] = useStateA('');
  const [role, setRole] = useStateA('all');
  const [status, setStatus] = useStateA('all');
  const [includeDeleted, setIncludeDeleted] = useStateA(false);
  const [page, setPage] = useStateA(1);
  const pageSize = 8;

  const filtered = useMemoA(() => data.adminUsers.filter(u => {
    if (search && !(u.name+u.email).toLowerCase().includes(search.toLowerCase())) return false;
    if (role !== 'all' && u.role !== role) return false;
    if (status === 'active' && u.blocked) return false;
    if (status === 'blocked' && !u.blocked) return false;
    return true;
  }), [data.adminUsers, search, role, status, includeDeleted]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const paged = filtered.slice((page-1)*pageSize, page*pageSize);

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Админка', crumbCurrent:'Пользователи' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, {
          title:'Пользователи', subtitle:`${data.adminUsers.length} аккаунтов`,
          right:[
            React.createElement('input', { key:1, className:'input', style:{width:240, height:38}, placeholder:'Поиск по имени/email…', value:search, onChange:e=>{setSearch(e.target.value); setPage(1);} }),
            React.createElement('select', { key:2, className:'select', style:{width:160, height:38, padding:'8px 12px', fontSize:13}, value:role, onChange:e=>{setRole(e.target.value); setPage(1);} },
              React.createElement('option', { value:'all' }, 'Все роли'),
              React.createElement('option', { value:'STUDENT' }, 'Студент'),
              React.createElement('option', { value:'TEACHER' }, 'Преподаватель'),
              React.createElement('option', { value:'ADMIN' }, 'Админ'),
            ),
            React.createElement('select', { key:3, className:'select', style:{width:160, height:38, padding:'8px 12px', fontSize:13}, value:status, onChange:e=>{setStatus(e.target.value); setPage(1);} },
              React.createElement('option', { value:'all' }, 'Все статусы'),
              React.createElement('option', { value:'active' }, 'Активные'),
              React.createElement('option', { value:'blocked' }, 'Заблокированные'),
            ),
            React.createElement('label', { key:4, className:'check-row', style:{cursor:'pointer'} },
              React.createElement('span', { className:'checkbox '+(includeDeleted?'on':''), onClick:e=>{e.preventDefault(); setIncludeDeleted(s=>!s);} }),
              'Удалённые'
            ),
          ]
        }),
        React.createElement('div', { className:'card card-pad' },
          paged.length === 0
            ? React.createElement(EmptyState, { icon:'⌕', title:'Ничего не найдено', text:'Попробуйте сбросить фильтры.' })
            : React.createElement('table', { className:'table' },
                React.createElement('thead', null, React.createElement('tr', null,
                  React.createElement('th', null, 'Пользователь'),
                  React.createElement('th', null, 'Email'),
                  React.createElement('th', null, 'Роль'),
                  React.createElement('th', null, 'Статус'),
                  React.createElement('th', null, 'Регистрация'),
                  React.createElement('th', null),
                )),
                React.createElement('tbody', null,
                  paged.map(u => React.createElement('tr', { key:u.id, onClick:()=>navigate(`/admin/users/${u.id}`) },
                    React.createElement('td', null, React.createElement('div', { className:'row', style:{gap:10} },
                      React.createElement('span', { className:'avatar sm '+(u.role!=='STUDENT'?'pp':'') }, u.initials),
                      React.createElement('span', { className:'t-name' }, u.name)
                    )),
                    React.createElement('td', { className:'muted mono', style:{fontSize:12.5} }, u.email),
                    React.createElement('td', null, React.createElement(RoleBadge, { role:u.role })),
                    React.createElement('td', null, u.blocked
                      ? React.createElement(Badge, { kind:'danger' }, React.createElement(Dot), 'Заблокирован')
                      : React.createElement(Badge, { kind:'muted' }, React.createElement(Dot), 'Активен')),
                    React.createElement('td', { className:'muted', style:{fontSize:12.5} }, u.registered),
                    React.createElement('td', { style:{textAlign:'right'} }, React.createElement('button', { className:'btn btn-ghost btn-sm' }, 'Открыть')),
                  ))
                )
              ),
          paged.length > 0 && React.createElement('div', { className:'between', style:{marginTop:16} },
            React.createElement('span', { className:'mut3', style:{fontSize:13} }, `${(page-1)*pageSize+1}–${Math.min(page*pageSize, filtered.length)} из ${filtered.length}`),
            React.createElement(window.Pagination || (()=>null), { page, pageCount, onChange:setPage })
          )
        )
      )
    )
  );
}

/* =========================================================
   ADMIN USER DETAIL
   ========================================================= */
function AdminUserDetailPage({ userId }) {
  const { navigate } = useRouter();
  const toast = useToast();
  const initial = window.MOCK.adminUsers.find(u => u.id === +userId) || window.MOCK.adminUsers[0];
  const [user, setUser] = useStateA(initial);
  const [confirm, setConfirm] = useStateA(null);
  const [pendingRole, setPendingRole] = useStateA(user.role);

  const block = () => { setUser(u => ({...u, blocked: !u.blocked})); toast.push({kind:'lime', title: user.blocked?'Пользователь разблокирован':'Пользователь заблокирован'}); };
  const remove = () => { toast.push({kind:'lime', title:'Аккаунт удалён', body:user.name}); navigate('/admin/users'); };
  const resetPw = () => toast.push({kind:'info', title:'Письмо отправлено', body:'Ссылка для сброса пароля выслана.'});
  const saveRole = () => { setUser(u => ({...u, role: pendingRole})); toast.push({kind:'lime', title:'Роль обновлена', body: pendingRole}); };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, {
        crumbHome: React.createElement('a', { onClick:()=>navigate('/admin/users'), style:{color:'var(--text-2)', cursor:'pointer'} }, 'Пользователи'),
        crumbCurrent: user.name
      }),
      React.createElement('div', { className:'content' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:16}, onClick:()=>navigate('/admin/users') }, '← Все пользователи'),
        React.createElement('div', { style:{display:'grid', gridTemplateColumns:'300px 1fr', gap:20, alignItems:'start'} },
          // profile card
          React.createElement('aside', { className:'card card-pad', style:{textAlign:'center'} },
            React.createElement('div', { className:'avatar lg '+(user.role!=='STUDENT'?'pp':''), style:{margin:'0 auto 12px'} }, user.initials),
            React.createElement('b', { style:{fontSize:17} }, user.name),
            React.createElement('p', { className:'mut3 mono', style:{fontSize:12.5, margin:'4px 0 12px'} }, user.email),
            React.createElement('div', { className:'wrap', style:{justifyContent:'center', marginBottom:18} },
              React.createElement(RoleBadge, { role:user.role }),
              user.blocked
                ? React.createElement(Badge, { kind:'danger' }, React.createElement(Dot), 'Заблокирован')
                : React.createElement(Badge, { kind:'muted' }, React.createElement(Dot), 'Активен'),
            ),
            React.createElement('div', { className:'grid', style:{gap:0, textAlign:'left'} },
              kvRow('ID', React.createElement('b', { className:'mono', style:{fontSize:13} }, '#'+user.id)),
              kvRow('Регистрация', user.registered),
              kvRow('Последний вход', user.lastLogin),
              kvRow('Решено задач', React.createElement('b', { style:{color:'var(--lime)'} }, user.solved)),
            )
          ),
          // actions stack
          React.createElement('div', { className:'grid', style:{gap:16} },
            React.createElement('div', { className:'card card-pad' },
              React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:14} }, 'Управление аккаунтом'),
              React.createElement('div', { className:'row', style:{gap:10, flexWrap:'wrap'} },
                React.createElement('select', { className:'select', style:{width:220}, value:pendingRole, onChange:e=>setPendingRole(e.target.value) },
                  React.createElement('option', { value:'STUDENT' }, 'Роль: Студент'),
                  React.createElement('option', { value:'TEACHER' }, 'Роль: Преподаватель'),
                  React.createElement('option', { value:'ADMIN' }, 'Роль: Админ'),
                ),
                React.createElement('button', { className:'btn btn-secondary btn-sm', onClick:saveRole, disabled:pendingRole===user.role }, 'Сохранить роль'),
                React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:resetPw }, 'Сбросить пароль'),
                React.createElement('button', { className:'btn btn-ghost btn-sm' }, 'Отправить инвайт')
              )
            ),
            user.groups.length > 0 && React.createElement('div', { className:'card card-pad' },
              React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:12} }, 'Группы пользователя'),
              React.createElement('div', { className:'wrap' }, user.groups.map(g => React.createElement(Badge, { key:g, kind:'purple' }, g)))
            ),
            React.createElement('div', { className:'card card-pad' },
              React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:12} }, 'Последняя активность'),
              React.createElement('div', { className:'grid', style:{gap:10} },
                [
                  ['Решена «Двоичный поиск»','сегодня 11:42'],
                  ['Попытка «Сумма двух чисел»','вчера 18:05'],
                  ['Вошёл в систему','вчера 09:14'],
                ].map(([a,b],i) => React.createElement('div', { key:i, className:'between' },
                  React.createElement('span', { style:{fontSize:13.5} }, a),
                  React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, b)
                ))
              )
            ),
            React.createElement('div', { className:'card card-pad', style:{borderColor:'rgba(255,77,106,.3)'} },
              React.createElement('div', { className:'between', style:{flexWrap:'wrap', gap:12} },
                React.createElement('div', null,
                  React.createElement('b', { style:{fontSize:14, color:'#ff8198'} }, 'Опасная зона'),
                  React.createElement('p', { className:'muted', style:{fontSize:13, margin:'4px 0 0'} }, 'Блокировка ограничит доступ пользователя к платформе.')
                ),
                React.createElement('div', { className:'row' },
                  React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>setConfirm('block') }, user.blocked?'Разблокировать':'Заблокировать'),
                  React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>setConfirm('delete') }, 'Удалить'),
                )
              )
            )
          )
        )
      )
    ),
    React.createElement(ConfirmDialog, {
      open:confirm==='block', onClose:()=>setConfirm(null), onConfirm:block,
      title: user.blocked?'Разблокировать пользователя?':'Заблокировать пользователя?', danger:!user.blocked,
      confirmLabel: user.blocked?'Разблокировать':'Заблокировать',
      body: user.blocked?'Пользователь снова сможет войти в систему.':'Пользователь не сможет войти в систему, пока вы не разблокируете аккаунт.'
    }),
    React.createElement(ConfirmDialog, {
      open:confirm==='delete', onClose:()=>setConfirm(null), onConfirm:remove,
      title:'Удалить аккаунт?', danger:true, confirmLabel:'Удалить навсегда',
      body:'Это действие необратимо. Все данные пользователя будут удалены.'
    }),
  );
}
function kvRow(label, value) {
  return React.createElement('div', { className:'between', style:{padding:'11px 0', borderTop:'1px solid var(--border)'} },
    React.createElement('span', { className:'muted', style:{fontSize:13} }, label),
    typeof value === 'string' ? React.createElement('b', { style:{fontSize:13} }, value) : value
  );
}

/* =========================================================
   ADMIN — TEACHER REQUESTS
   ========================================================= */
function AdminTeacherRequestsPage() {
  const toast = useToast();
  const [filter, setFilter] = useStateA('pending');
  const [reqs, setReqs] = useStateA(window.MOCK.teacherRequests);
  const [confirm, setConfirm] = useStateA(null);

  const filtered = reqs.filter(r => filter === 'all' || r.status === filter);

  const decide = (r, status) => {
    setReqs(arr => arr.map(x => x.id === r.id ? {...x, status} : x));
    toast.push({ kind: status==='approved'?'lime':'info', title: status==='approved'?'Заявка одобрена':'Заявка отклонена', body:r.name });
  };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Админка', crumbCurrent:'Заявки преподавателей' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, { title:'Заявки на роль преподавателя', subtitle:`${reqs.filter(r=>r.status==='pending').length} ожидают рассмотрения` }),
        React.createElement('div', { className:'wrap', style:{marginBottom:16} },
          React.createElement(Chip, { active:filter==='pending', pp:true, onClick:()=>setFilter('pending') }, 'Ожидают'),
          React.createElement(Chip, { active:filter==='approved', onClick:()=>setFilter('approved') }, 'Одобренные'),
          React.createElement(Chip, { active:filter==='rejected', onClick:()=>setFilter('rejected') }, 'Отклонённые'),
          React.createElement(Chip, { active:filter==='all', onClick:()=>setFilter('all') }, 'Все'),
        ),
        React.createElement('div', { className:'card card-pad' },
          filtered.length === 0
            ? React.createElement(EmptyState, { icon:'✓', title:'Нет заявок', text:'Когда студенты подадут заявку на роль преподавателя, они появятся здесь.' })
            : React.createElement('table', { className:'table' },
              React.createElement('thead', null, React.createElement('tr', null,
                React.createElement('th', null, 'Кандидат'),
                React.createElement('th', null, 'Email'),
                React.createElement('th', null, 'Кафедра'),
                React.createElement('th', null, 'Подано'),
                React.createElement('th', null, 'Статус'),
                React.createElement('th', null),
              )),
              React.createElement('tbody', null, filtered.map(r => React.createElement('tr', { key:r.id, className:'no-hover' },
                React.createElement('td', null, React.createElement('div', { className:'row', style:{gap:9} },
                  React.createElement('span', { className:'avatar pp sm' }, r.name[0]),
                  React.createElement('span', { className:'t-name' }, r.name)
                )),
                React.createElement('td', { className:'mono muted', style:{fontSize:12.5} }, r.email),
                React.createElement('td', { className:'muted' }, r.dept),
                React.createElement('td', { className:'muted' }, r.requestedAt),
                React.createElement('td', null, r.status==='pending'
                  ? React.createElement(Badge, { kind:'warn' }, React.createElement(Dot), 'Ожидает')
                  : r.status==='approved'
                    ? React.createElement(Badge, { kind:'lime' }, React.createElement(Dot), 'Одобрена')
                    : React.createElement(Badge, { kind:'danger' }, React.createElement(Dot), 'Отклонена')
                ),
                React.createElement('td', { style:{textAlign:'right'} },
                  r.status === 'pending'
                    ? React.createElement('div', { className:'row', style:{justifyContent:'flex-end'} },
                        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:()=>setConfirm({type:'approve', r}) }, 'Одобрить'),
                        React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>setConfirm({type:'reject', r}) }, 'Отклонить'),
                      )
                    : React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, '—')
                )
              )))
            )
        )
      )
    ),
    React.createElement(ConfirmDialog, {
      open:!!confirm, onClose:()=>setConfirm(null),
      onConfirm:()=>{ if (confirm) decide(confirm.r, confirm.type==='approve'?'approved':'rejected'); },
      title: confirm?.type==='approve' ? 'Одобрить заявку?' : 'Отклонить заявку?',
      confirmLabel: confirm?.type==='approve' ? 'Одобрить' : 'Отклонить',
      danger: confirm?.type==='reject',
      body: confirm ? `${confirm.r.name} получит ${confirm.type==='approve'?'роль преподавателя':'уведомление об отказе'}.` : ''
    })
  );
}

/* =========================================================
   ADMIN — ASSIGNMENTS
   ========================================================= */
function AdminAssignmentsPage() {
  const toast = useToast();
  const data = window.MOCK;
  const [search, setSearch] = useStateA('');
  const [workflow, setWorkflow] = useStateA('all');
  const [showArchived, setShowArchived] = useStateA(false);
  const [items, setItems] = useStateA(data.adminAssignments);
  const [versionsOf, setVersionsOf] = useStateA(null);

  const filtered = items.filter(a => {
    if (!showArchived && a.archived) return false;
    if (workflow !== 'all' && a.workflow !== workflow) return false;
    if (search && !a.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const setW = (id, w) => { setItems(arr => arr.map(x => x.id===id ? {...x, workflow:w} : x)); toast.push({kind:'lime', title:'Статус обновлён', body:w}); };
  const archive = (id) => { setItems(arr => arr.map(x => x.id===id ? {...x, archived:true, workflow:'archived'} : x)); toast.push({kind:'info', title:'Задание архивировано'}); };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Админка', crumbCurrent:'Задания' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, {
          title:'Задания', subtitle:`${items.filter(i=>!i.archived).length} активных · ${items.filter(i=>i.archived).length} в архиве`,
          right:[
            React.createElement('input', { key:1, className:'input', style:{width:240, height:38}, placeholder:'Поиск задания…', value:search, onChange:e=>setSearch(e.target.value) }),
            React.createElement('select', { key:2, className:'select', style:{width:160, height:38, padding:'8px 12px', fontSize:13}, value:workflow, onChange:e=>setWorkflow(e.target.value) },
              React.createElement('option', { value:'all' }, 'Все статусы'),
              React.createElement('option', { value:'draft' }, 'Черновик'),
              React.createElement('option', { value:'review' }, 'На проверке'),
              React.createElement('option', { value:'published' }, 'Опубликован'),
              React.createElement('option', { value:'archived' }, 'В архиве'),
            ),
            React.createElement('label', { key:3, className:'check-row', style:{cursor:'pointer'} },
              React.createElement('span', { className:'checkbox '+(showArchived?'on':''), onClick:e=>{e.preventDefault(); setShowArchived(s=>!s);} }),
              'Архив'
            ),
          ]
        }),
        React.createElement('div', { className:'card card-pad' },
          filtered.length === 0
            ? React.createElement(EmptyState, { icon:'⌕', title:'Ничего не найдено', text:'Снимите фильтры или попробуйте другой запрос.' })
            : React.createElement('table', { className:'table' },
              React.createElement('thead', null, React.createElement('tr', null,
                React.createElement('th', null, 'Задание'),
                React.createElement('th', null, 'Автор'),
                React.createElement('th', null, 'Версия'),
                React.createElement('th', null, 'Workflow'),
                React.createElement('th', null, 'Обновлено'),
                React.createElement('th', null),
              )),
              React.createElement('tbody', null, filtered.map(a => React.createElement('tr', { key:a.id, className:'no-hover' },
                React.createElement('td', { className:'t-name' }, a.title, a.archived && React.createElement('span', { className:'badge badge-muted', style:{marginLeft:8} }, 'архив')),
                React.createElement('td', { className:'muted' }, a.author),
                React.createElement('td', null, React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setVersionsOf(a) }, a.version)),
                React.createElement('td', null,
                  React.createElement('select', {
                    className:'select', style:{width:160, height:32, padding:'4px 12px', fontSize:12.5},
                    value:a.workflow, onChange:e=>setW(a.id, e.target.value)
                  },
                    React.createElement('option', { value:'draft' }, 'Черновик'),
                    React.createElement('option', { value:'review' }, 'На проверке'),
                    React.createElement('option', { value:'published' }, 'Опубликован'),
                    React.createElement('option', { value:'archived' }, 'В архиве'),
                  )
                ),
                React.createElement('td', { className:'muted' }, a.updated),
                React.createElement('td', { style:{textAlign:'right'} },
                  !a.archived && React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>archive(a.id) }, 'Архив')
                )
              )))
            )
        )
      )
    ),
    React.createElement(Modal, {
      open:!!versionsOf, onClose:()=>setVersionsOf(null), title: versionsOf ? `Версии · ${versionsOf.title}` : '',
      footer: React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setVersionsOf(null) }, 'Закрыть')
    }, versionsOf && React.createElement('div', { className:'grid', style:{gap:10} },
      ['v3 · текущая','v2 · 15 апр','v1 · 02 мар'].map((v,i) => React.createElement('div', { key:i, className:'between', style:{padding:'10px 12px', border:'1px solid var(--border)', borderRadius:10} },
        React.createElement('div', null,
          React.createElement('b', { style:{fontSize:13.5} }, v.split('·')[0]),
          React.createElement('span', { className:'mut3', style:{fontSize:12, marginLeft:8} }, v.split('·')[1])
        ),
        i === 0
          ? React.createElement(Badge, { kind:'lime' }, 'Активна')
          : React.createElement('button', { className:'btn btn-secondary btn-sm' }, 'Активировать')
      ))
    ))
  );
}

/* =========================================================
   ADMIN — STATISTICS (deep dive — duplicates overview metrics)
   ========================================================= */
function AdminStatisticsPage() {
  const stats = window.MOCK.adminStats;
  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Админка', crumbCurrent:'Статистика' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, { title:'Статистика платформы', subtitle:'Расширенные метрики, дублирующие обзор, но с детализацией.' }),
        React.createElement('div', { className:'cards3', style:{marginBottom:16} },
          React.createElement(StatCard, { label:'Всего пользователей', value:stats.users.toLocaleString('ru'), badge:'+5.2% мес', badgeKind:'lime' }),
          React.createElement(StatCard, { label:'Студентов', value:stats.students.toLocaleString('ru'), badge:'94% базы', badgeKind:'muted' }),
          React.createElement(StatCard, { label:'Преподавателей', value:stats.teachers, badge:`${stats.pendingTeacherRequests} заявок`, badgeKind:'purple' }),
        ),
        React.createElement('div', { className:'cards3', style:{marginBottom:16} },
          React.createElement(StatCard, { label:'Решений за 30 дней', value:stats.submissionsLast30.toLocaleString('ru'), badge:'+12% к месяцу', badgeKind:'lime' }),
          React.createElement(StatCard, { label:'Средняя сдача', value: Math.round(stats.acceptanceRate*100)+'%', badge:'+1% к месяцу', badgeKind:'lime' }),
          React.createElement(StatCard, { label:'Заблокированы', value:stats.blocked, badge:'1% базы', badgeKind:'danger' }),
        ),
        React.createElement('div', { className:'card card-pad' },
          React.createElement('b', { style:{fontSize:15} }, 'Решения по дням (90 дней)'),
          React.createElement('div', { style:{display:'flex', alignItems:'flex-end', gap:3, height:160, marginTop:16} },
            Array.from({length:60}, (_, i) => {
              const v = 30 + Math.round(Math.sin(i / 4) * 25 + Math.cos(i/9)*15 + 25);
              return React.createElement('div', { key:i, style:{flex:1, background: v>70?'var(--lime)':'var(--purple)', height:v+'%', borderRadius:2, opacity: v<25?0.35:1} });
            })
          )
        ),
        React.createElement('div', { className:'cards2', style:{marginTop:16} },
          React.createElement('div', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:14} }, 'Распределение по ролям'),
            React.createElement('div', { className:'grid', style:{gap:12, marginTop:14} }, stats.breakdown.roles.map(r =>
              React.createElement('div', { key:r.label },
                React.createElement('div', { className:'between', style:{fontSize:13, marginBottom:6} },
                  React.createElement('span', { className:'muted' }, r.label),
                  React.createElement('b', { className:'mono' }, r.value)
                ),
                React.createElement('div', { className:'progress '+(r.color==='purple'?'pp':'') },
                  React.createElement('i', { style:{width: Math.min(100,(r.value/stats.users)*100*4) + '%', background: r.color==='danger'?'var(--danger)':null} })
                )
              )
            ))
          ),
          React.createElement('div', { className:'card card-pad' },
            React.createElement('b', { style:{fontSize:14} }, 'Типы задач'),
            React.createElement('div', { className:'grid', style:{gap:12, marginTop:14} }, stats.breakdown.taskTypes.map((r,i) =>
              React.createElement('div', { key:r.label },
                React.createElement('div', { className:'between', style:{fontSize:13, marginBottom:6} },
                  React.createElement('span', { className:'muted mono' }, r.label),
                  React.createElement('b', { className:'mono' }, r.value)
                ),
                React.createElement('div', { className:'progress '+(i%2?'pp':'') }, React.createElement('i', { style:{width: Math.min(100,(r.value/stats.tasks)*100*2) + '%'} }))
              )
            ))
          )
        ),
      )
    )
  );
}

/* =========================================================
   ADMIN — CREATE TEACHER
   ========================================================= */
function AdminCreateTeacherPage() {
  const { navigate } = useRouter();
  const toast = useToast();
  const [form, setForm] = useStateA({ name:'', email:'', password:'', dept:'' });
  const [errs, setErrs] = useStateA({});
  const set = (k,v) => setForm(f => ({...f, [k]:v}));
  const submit = (e) => {
    e.preventDefault();
    const ne = {};
    if (!form.name.trim()) ne.name = 'Укажите имя';
    if (!form.email.includes('@')) ne.email = 'Email обязателен';
    if (form.password.length < 8) ne.password = 'Минимум 8 символов';
    setErrs(ne);
    if (Object.keys(ne).length) return;
    toast.push({kind:'lime', title:'Преподаватель создан', body: form.name});
    navigate('/admin/users');
  };

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: adminSidebarItems(), role:'ADMIN', brandPP:true }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Админка', crumbCurrent:'Создать преподавателя' }),
      React.createElement('div', { className:'content' },
        React.createElement(PageHeader, { title:'Создать преподавателя', subtitle:'Минуя заявку — для ручной выдачи роли проверенным преподавателям.' }),
        React.createElement('form', { className:'card card-pad', style:{maxWidth:560}, onSubmit:submit },
          React.createElement(window.FormField, { label:'Имя', err:errs.name },
            React.createElement('input', { className:'input '+(errs.name?'err':''), value:form.name, onChange:e=>set('name', e.target.value), placeholder:'Иван Петров' })
          ),
          React.createElement(window.FormField, { label:'Email', err:errs.email },
            React.createElement('input', { className:'input '+(errs.email?'err':''), type:'email', value:form.email, onChange:e=>set('email', e.target.value), placeholder:'i.petrov@uni.ru' })
          ),
          React.createElement(window.FormField, { label:'Кафедра / предмет' },
            React.createElement('input', { className:'input', value:form.dept, onChange:e=>set('dept', e.target.value), placeholder:'Алгоритмы и структуры данных' })
          ),
          React.createElement(window.FormField, { label:'Временный пароль', err:errs.password, help:'Минимум 8 символов. Преподаватель сможет сменить его при первом входе.' },
            React.createElement('input', { className:'input mono '+(errs.password?'err':''), type:'text', value:form.password, onChange:e=>set('password', e.target.value), placeholder:'temp-1234' })
          ),
          React.createElement('div', { className:'row', style:{justifyContent:'flex-end', gap:10, marginTop:6} },
            React.createElement('button', { type:'button', className:'btn btn-ghost', onClick:()=>navigate('/admin/users') }, 'Отмена'),
            React.createElement('button', { type:'submit', className:'btn btn-primary' }, 'Создать преподавателя')
          )
        )
      )
    )
  );
}

Object.assign(window, {
  adminSidebarItems, AdminOverviewPage, AdminUsersPage, AdminUserDetailPage,
  AdminTeacherRequestsPage, AdminAssignmentsPage, AdminStatisticsPage, AdminCreateTeacherPage
});
