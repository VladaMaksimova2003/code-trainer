/* global React */
const { useState: useStateS, useMemo: useMemoS } = React;

function settingsTabsFor(role) {
  const base = [
    { to:'/settings/profile',  label:'Профиль' },
    { to:'/settings/security', label:'Безопасность' },
    { to:'/settings/learning', label:'Обучение' },
  ];
  if (role === 'TEACHER' || role === 'ADMIN') base.push({ to:'/settings/teacher', label:'Преподаватель' });
  return base;
}

function SettingsLayout({ tab, children }) {
  const { user } = useAuth();
  const { navigate, path } = useRouter();
  const tabs = settingsTabsFor(user?.role || 'STUDENT');

  const sidebar = user?.role === 'TEACHER' ? window.teacherSidebarItems()
    : user?.role === 'ADMIN' ? window.adminSidebarItems()
    : window.studentSidebarItems();

  const backTo = user?.role === 'TEACHER' ? '/teacher/profile' : user?.role === 'ADMIN' ? '/admin' : '/';

  return React.createElement('div', { className:'app-root' },
    React.createElement(Sidebar, { items: sidebar, role: user?.role || 'STUDENT', brandPP: user?.role !== 'STUDENT' }),
    React.createElement('div', null,
      React.createElement(Topbar, { crumbHome:'Тренажёр', crumbCurrent:'Настройки' }),
      React.createElement('div', { className:'content' },
        React.createElement('button', { className:'btn btn-ghost btn-sm', style:{marginBottom:14}, onClick:()=>navigate(backTo) }, '← Назад'),
        React.createElement(PageHeader, { title:'Настройки', subtitle:'Управляйте профилем, безопасностью и предпочтениями обучения.' }),
        React.createElement('div', { className:'tabbar' },
          tabs.map(t => React.createElement('button', {
            key:t.to, className: path===t.to ? (user?.role!=='STUDENT'?'on pp':'on') : '',
            onClick:()=>navigate(t.to)
          }, t.label))
        ),
        children
      )
    )
  );
}

/* ----- TABS ----- */
function ProfileTab() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const [form, setForm] = useStateS({ name:user?.name || '', email:user?.email || '', about:'Студент-фронтендер, учусь алгоритмам.' });
  const set = (k,v) => setForm(f => ({...f, [k]:v}));
  const save = (e) => {
    e?.preventDefault();
    const emailChanged = form.email !== user?.email;
    const patch = { ...user, name:form.name, email:form.email, initials:(form.name[0]||'У').toUpperCase() };
    if (emailChanged) { patch.emailVerified = false; patch.pendingVerifyEmail = form.email; }
    setUser(patch);
    if (emailChanged) toast.push({kind:'info', title:'Подтвердите новый email', body:`Мы отправили код на ${form.email}`});
    else toast.push({kind:'lime', title:'Сохранено'});
  };
  return React.createElement('form', { className:'card card-pad', style:{maxWidth:640}, onSubmit:save },
    React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:14} }, 'Профиль'),
    React.createElement(window.FormField, { label:'Имя' },
      React.createElement('input', { className:'input', value:form.name, onChange:e=>set('name', e.target.value) })
    ),
    React.createElement(window.FormField, { label:'Email' },
      React.createElement('input', { className:'input', type:'email', value:form.email, onChange:e=>set('email', e.target.value) })
    ),
    React.createElement(window.FormField, { label:'О себе' },
      React.createElement('textarea', { className:'textarea', style:{fontFamily:'var(--font)', minHeight:80}, value:form.about, onChange:e=>set('about', e.target.value) })
    ),
    React.createElement('div', { className:'field' },
      React.createElement('label', { className:'label' }, 'Роли (только для чтения)'),
      React.createElement('div', { className:'wrap' },
        React.createElement(RoleBadge, { role:user?.role || 'STUDENT' }),
        user?.role !== 'STUDENT' && React.createElement(Badge, { kind:'lime' }, 'STUDENT'),
      )
    ),
    React.createElement('div', { className:'row', style:{justifyContent:'flex-end', gap:10} },
      React.createElement('button', { type:'button', className:'btn btn-ghost' }, 'Отмена'),
      React.createElement('button', { type:'submit', className:'btn btn-primary' }, 'Сохранить')
    )
  );
}

function SecurityTab() {
  const toast = useToast();
  const { logout } = useAuth();
  const { navigate } = useRouter();
  const [form, setForm] = useStateS({ cur:'', next:'', confirm:'' });
  const set = (k,v) => setForm(f => ({...f, [k]:v}));
  const change = (e) => {
    e.preventDefault();
    if (form.next.length < 8) return toast.push({kind:'err', title:'Пароль слишком короткий', body:'Минимум 8 символов'});
    if (form.next !== form.confirm) return toast.push({kind:'err', title:'Пароли не совпадают'});
    toast.push({kind:'lime', title:'Пароль изменён'});
    setForm({cur:'',next:'',confirm:''});
  };
  return React.createElement('div', { style:{display:'grid', gap:16, maxWidth:640} },
    React.createElement('form', { className:'card card-pad', onSubmit:change },
      React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:14} }, 'Смена пароля'),
      React.createElement(window.FormField, { label:'Текущий пароль' },
        React.createElement('input', { className:'input', type:'password', value:form.cur, onChange:e=>set('cur', e.target.value) })
      ),
      React.createElement(window.FormField, { label:'Новый пароль', help:'Минимум 8 символов.' },
        React.createElement('input', { className:'input', type:'password', value:form.next, onChange:e=>set('next', e.target.value) })
      ),
      React.createElement(window.FormField, { label:'Подтверждение' },
        React.createElement('input', { className:'input', type:'password', value:form.confirm, onChange:e=>set('confirm', e.target.value) })
      ),
      React.createElement('div', { className:'row', style:{justifyContent:'flex-end'} },
        React.createElement('button', { type:'submit', className:'btn btn-primary' }, 'Сменить пароль')
      )
    ),
    React.createElement('div', { className:'card card-pad' },
      React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:6} }, 'Сессии'),
      React.createElement('p', { className:'muted', style:{fontSize:13.5, margin:'0 0 14px'} }, 'Завершайте сессии на устройствах, которыми больше не пользуетесь.'),
      React.createElement('div', { className:'row', style:{flexWrap:'wrap'} },
        React.createElement('button', { className:'btn btn-ghost btn-sm', onClick:()=>{ toast.push({kind:'lime', title:'Сессия завершена'}); }}, 'Завершить текущую'),
        React.createElement('button', { className:'btn btn-danger btn-sm', onClick:()=>{ toast.push({kind:'lime', title:'Все сессии завершены'}); logout(); navigate('/login'); }}, 'Выйти со всех устройств'),
      )
    )
  );
}

function LearningTab() {
  const toast = useToast();
  const data = window.MOCK;
  const [diff, setDiff] = useStateS('Средняя');

  return React.createElement('form', { className:'card card-pad', style:{maxWidth:640}, onSubmit:(e)=>{e.preventDefault(); toast.push({kind:'lime', title:'Предпочтения сохранены'});} },
    React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:14} }, 'Обучение'),
    React.createElement('p', { className:'muted', style:{fontSize:13.5, margin:'0 0 18px'} }, 'Уровень сложности задач, которые вам будут рекомендоваться по умолчанию.'),
    React.createElement('label', { className:'label' }, 'Стартовая сложность'),
    React.createElement('div', { className:'wrap', style:{marginBottom:20} },
      data.difficulties.map(d => React.createElement(Chip, { key:d, active:diff===d, onClick:()=>setDiff(d) }, d))
    ),
    React.createElement('div', { className:'row', style:{justifyContent:'flex-end', gap:10} },
      React.createElement('button', { type:'button', className:'btn btn-ghost' }, 'Отмена'),
      React.createElement('button', { type:'submit', className:'btn btn-primary' }, 'Сохранить')
    )
  );
}

function TeacherSettingsTab() {
  const toast = useToast();
  const data = window.MOCK;
  const [form, setForm] = useStateS({
    displayName:'Алексей Петров',
    bio:'Преподаватель кафедры алгоритмов. 8 лет опыта.',
    expertise: ['Алгоритмы','DP','Графы'],
  });
  const toggle = (k,v) => setForm(f => ({...f, [k]: f[k].includes(v) ? f[k].filter(x=>x!==v) : [...f[k], v] }));

  return React.createElement('div', { style:{display:'grid', gap:16, maxWidth:720} },
    React.createElement('form', { className:'card card-pad', onSubmit:(e)=>{e.preventDefault(); toast.push({kind:'lime', title:'Настройки преподавателя сохранены'});} },
      React.createElement('b', { style:{fontSize:14, display:'block', marginBottom:14} }, 'Профиль преподавателя'),
      React.createElement(window.FormField, { label:'Отображаемое имя' },
        React.createElement('input', { className:'input', value:form.displayName, onChange:e=>setForm(f=>({...f, displayName:e.target.value})) })
      ),
      React.createElement(window.FormField, { label:'Био / о себе' },
        React.createElement('textarea', { className:'textarea', style:{fontFamily:'var(--font)'}, value:form.bio, onChange:e=>setForm(f=>({...f, bio:e.target.value})) })
      ),
      React.createElement('label', { className:'label' }, 'Экспертные темы'),
      React.createElement('div', { className:'wrap', style:{marginBottom:8} },
        data.patterns.map((p,i) => React.createElement(Chip, { key:p, active:form.expertise.includes(p), pp:i%2===1, onClick:()=>toggle('expertise', p) }, p))
      ),
      React.createElement('div', { className:'row', style:{justifyContent:'flex-end'} },
        React.createElement('button', { type:'submit', className:'btn btn-primary' }, 'Сохранить')
      )
    ),
    React.createElement('div', { className:'cards3' },
      React.createElement(StatCard, { label:'Моих задач', value:42, badge:'+3 за неделю', badgeKind:'lime' }),
      React.createElement(StatCard, { label:'Моих каталогов', value:4, badge:'2 группам', badgeKind:'purple' }),
      React.createElement(StatCard, { label:'Студентов', value:36, badge:'+4', badgeKind:'lime' }),
    ),
  );
}

Object.assign(window, { SettingsLayout, ProfileTab, SecurityTab, LearningTab, TeacherSettingsTab });
