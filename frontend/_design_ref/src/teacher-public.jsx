/* global React */
/* Teacher public profile — as a student sees it. */
const { useState: useStTP, useMemo: useMmTP } = React;

function teacherProfileMeta(teacher) {
  const isPetrov = /петров|petrov/i.test(teacher?.name || '');
  return {
    quote: isPetrov
      ? 'Алгоритмы — это способ думать, а не зубрить. Главное — научиться формулировать задачу, всё остальное приложится.'
      : 'Любая программа начинается с простого вопроса: что мы хотим получить и из чего? Если вы научитесь чётко на него отвечать — половина работы уже сделана.',
    bio: isPetrov
      ? 'Преподаю алгоритмы и структуры данных уже 8 лет. Веду спецкурс по олимпиадному программированию. Люблю объяснять «на пальцах» и через примеры из жизни.'
      : 'Веду спецкурс по алгоритмам и подготовке к собеседованиям в IT. Помогаю студентам с проектами и научными работами. Открыт к вопросам в любое время.',
    creds: isPetrov
      ? ['8 лет опыта','к.т.н.','Олимпиадник ICPC','Mentor 50+ students']
      : ['Mentor','6 лет преподавания','Industry experience'],
    online: 'недавно · 12 минут назад',
    responseTime: 'обычно отвечает в течение 2 часов',
    timezone: 'МСК · UTC+3',
    languages: ['Русский','English'],
  };
}

function TeacherPublicProfilePage({ teacherId }) {
  const { navigate } = window.useRouter();
  const toast = window.useToast();
  const data = window.MOCK;
  const teacher = data.adminUsers.find(u => u.id === +teacherId && u.role === 'TEACHER')
    || data.adminUsers.find(u => u.role === 'TEACHER')
    || { id: 113, name:'Алексей Петров', email:'a.petrov@uni.ru', initials:'А', role:'TEACHER' };

  const meta = useMmTP(() => teacherProfileMeta(teacher), [teacher]);
  const groups = data.groups.filter(g => g.teacher === teacher.name);
  // associate catalogs with this teacher (demo: first 2 belong to Petrov, rest to Smirnova)
  const catalogs = /петров|petrov/i.test(teacher.name)
    ? data.catalogs.slice(0, 2)
    : data.catalogs.slice(2);

  const username = '@' + teacher.email.split('@')[0];

  const [msgOpen, setMsgOpen] = useStTP(false);
  const [msg, setMsg] = useStTP('');
  const sendMsg = () => {
    if (!msg.trim()) return;
    toast.push({ kind:'lime', title:'Сообщение отправлено', body: `${teacher.name} увидит его при следующем входе.` });
    setMsg(''); setMsgOpen(false);
  };

  return React.createElement('div', { className:'app-root' },
    React.createElement(window.Sidebar, { items: window.studentSidebarItems(), role:'STUDENT' }),
    React.createElement('div', null,
      React.createElement(window.Topbar, { crumbHome:'Тренажёр', crumbCurrent:'Преподаватель' }),
      React.createElement('div', { className:'content' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:14}, onClick:()=>history.back() }, '← Назад'),

        // ===== HERO =====
        React.createElement('div', { className:'tpp-hero' },
          React.createElement('div', { className:'tpp-hero-main' },
            React.createElement('div', { className:'tpp-avatar' }, teacher.initials),
            React.createElement('div', { style:{minWidth:0} },
              React.createElement('h1', { className:'tpp-name' }, teacher.name),
              React.createElement('p', { className:'tpp-username' }, username),
              React.createElement('div', { className:'tpp-meta' },
                React.createElement(window.RoleBadge, { role:'TEACHER' }),
                React.createElement('span', { className:'online-dot' }, React.createElement('i'), 'онлайн'),
                React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, '·'),
                React.createElement('span', { className:'mut3', style:{fontSize:12.5} }, meta.timezone),
              )
            )
          ),
          React.createElement('div', { className:'tpp-cta' },
            React.createElement('button', { className:'btn btn-primary', onClick:()=>setMsgOpen(true) },
              React.createElement('span', { style:{fontSize:15} }, '✉'),
              ' Написать сообщение'
            ),
            React.createElement('p', { className:'mut3', style:{fontSize:12, margin:0, textAlign:'center'} },
              meta.responseTime
            )
          )
        ),

        // ===== TWO-COLUMN GRID =====
        React.createElement('div', { className:'tpp-grid' },
          // LEFT column — about + groups + assignments
          React.createElement('div', { className:'grid', style:{gap:18} },
            // About
            React.createElement('div', { className:'tpp-section' },
              React.createElement('div', { className:'tpp-section-h' },
                React.createElement('b', null, 'О преподавателе')
              ),
              React.createElement('p', { className:'tpp-quote' }, meta.quote),
              React.createElement('p', { className:'tpp-bio' }, meta.bio),
              React.createElement('div', { className:'tpp-creds' },
                meta.creds.map((c, i) => React.createElement('span', { key:i, className:'tpp-cred' },
                  React.createElement('i'), c
                ))
              )
            ),

            // Groups
            React.createElement('div', { className:'tpp-section' },
              React.createElement('div', { className:'tpp-section-h' },
                React.createElement('b', null, 'Группы'),
                React.createElement('span', { className:'small' }, `${groups.length} активных`)
              ),
              groups.length === 0
                ? React.createElement('p', { className:'mut3', style:{fontSize:13, margin:0} }, 'У преподавателя пока нет открытых групп.')
                : groups.map(g => React.createElement('div', {
                    key:g.id, className:'tpp-listitem',
                    onClick:()=>navigate(`/student/groups/${g.id}`)
                  },
                    React.createElement('div', { className:'ico' }, g.name.split(' ')[0].slice(0,2).toUpperCase()),
                    React.createElement('div', { className:'body' },
                      React.createElement('b', null, g.name),
                      React.createElement('span', null, `${g.students} студентов · приглашение `,
                        React.createElement('span', { className:'mono', style:{color:'var(--lime)'} }, g.invite))
                    ),
                    React.createElement('span', { className:'arr' }, '→')
                  ))
            ),

            // Assignments / Catalogs
            React.createElement('div', { className:'tpp-section' },
              React.createElement('div', { className:'tpp-section-h' },
                React.createElement('b', null, 'Задания'),
                React.createElement('span', { className:'small' }, `${catalogs.length} сборников`)
              ),
              catalogs.length === 0
                ? React.createElement('p', { className:'mut3', style:{fontSize:13, margin:0} }, 'Преподаватель ещё не публиковал задания.')
                : catalogs.map(c => React.createElement('div', {
                    key:c.id, className:'tpp-listitem lime',
                    onClick:()=>{ toast.push({kind:'info', title:'Откройте задание из своей группы', body:'Сборники назначаются студентам через группы.'}); }
                  },
                    React.createElement('div', { className:'ico' }, '📚'),
                    React.createElement('div', { className:'body' },
                      React.createElement('b', null, c.name),
                      React.createElement('span', null, `${c.taskIds.length} задач${c.assignedTo.length?` · назначен ${c.assignedTo.length} группе(ам)`:''}`)
                    ),
                    React.createElement('span', { className:'arr' }, '→')
                  ))
            ),
          ),

          // RIGHT column — activity + practical info
          React.createElement('div', { className:'grid', style:{gap:18} },
            React.createElement('div', { className:'tpp-section' },
              React.createElement('div', { className:'tpp-section-h' },
                React.createElement('b', null, 'Активность')
              ),
              React.createElement('div', { className:'tpp-activity-row good' },
                React.createElement('div', { className:'ico' }, '●'),
                React.createElement('div', { className:'body' },
                  React.createElement('b', null, 'Сейчас онлайн'),
                  React.createElement('span', null, `был активен ${meta.online}`)
                )
              ),
              React.createElement('div', { className:'tpp-activity-row good' },
                React.createElement('div', { className:'ico' }, '↩'),
                React.createElement('div', { className:'body' },
                  React.createElement('b', null, 'Отвечает быстро'),
                  React.createElement('span', null, meta.responseTime)
                )
              ),
              React.createElement('div', { className:'tpp-activity-row' },
                React.createElement('div', { className:'ico' }, '◷'),
                React.createElement('div', { className:'body' },
                  React.createElement('b', null, 'Часовой пояс'),
                  React.createElement('span', null, `${meta.timezone} · доступен в рабочее время`)
                )
              ),
              React.createElement('div', { className:'tpp-activity-row' },
                React.createElement('div', { className:'ico' }, 'A'),
                React.createElement('div', { className:'body' },
                  React.createElement('b', null, 'Языки общения'),
                  React.createElement('span', null, meta.languages.join(' · '))
                )
              ),
            ),

            React.createElement('div', { className:'tpp-section' },
              React.createElement('div', { className:'tpp-section-h' },
                React.createElement('b', null, 'Как с ним связаться')
              ),
              React.createElement('p', { className:'muted', style:{fontSize:13, margin:'0 0 14px', lineHeight:1.6} },
                'Самое быстрое — отправить сообщение прямо здесь. Преподаватель видит уведомления в кабинете и отвечает обычно в течение пары часов.'
              ),
              React.createElement('button', { className:'btn btn-secondary btn-full', onClick:()=>setMsgOpen(true) },
                '✉ Открыть чат'
              ),
              React.createElement('p', { className:'mut3', style:{fontSize:11.5, margin:'14px 0 0', textAlign:'center'} },
                'Все обращения проходят через платформу — это безопасно'
              )
            )
          )
        )
      )
    ),

    // ===== Message Modal =====
    React.createElement(window.Modal, {
      open: msgOpen, onClose: ()=>setMsgOpen(false),
      title: `Сообщение для ${teacher.name}`,
      width: 520,
      footer: React.createElement(React.Fragment, null,
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>setMsgOpen(false) }, 'Отмена'),
        React.createElement('button', { className:'btn btn-primary btn-sm', onClick:sendMsg, disabled:!msg.trim() }, 'Отправить')
      )
    },
      React.createElement('div', { className:'row', style:{gap:12, marginBottom:14, paddingBottom:14, borderBottom:'1px solid var(--border)'} },
        React.createElement('div', { className:'avatar pp', style:{width:38, height:38, fontSize:14, borderRadius:12} }, teacher.initials),
        React.createElement('div', null,
          React.createElement('div', { style:{fontSize:14, fontWeight:600} }, teacher.name),
          React.createElement('div', { className:'mut3', style:{fontSize:12} }, meta.responseTime)
        )
      ),
      React.createElement('textarea', {
        className:'textarea',
        style:{fontFamily:'var(--font)', minHeight:120, fontSize:14},
        placeholder:'Здравствуйте! Хочу спросить о…', value:msg, onChange:e=>setMsg(e.target.value), autoFocus:true
      }),
      React.createElement('p', { className:'mut3', style:{fontSize:11.5, margin:'10px 0 0'} },
        'Будьте конкретны — укажите задачу или тему, по которой нужен совет. Это поможет преподавателю быстрее ответить.'
      )
    )
  );
}

Object.assign(window, { TeacherPublicProfilePage });
