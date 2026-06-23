/* global React */
const { useState, useEffect, useRef, useMemo, useCallback, createContext, useContext } = React;

/* ===================== HASH ROUTER ===================== */
const RouterCtx = createContext(null);

function parseHash() {
  const h = window.location.hash.replace(/^#/, '') || '/login';
  const [pathPart, qs] = h.split('?');
  const query = Object.fromEntries(new URLSearchParams(qs || '').entries());
  return { path: pathPart, query };
}

function RouterProvider({ children }) {
  const [route, setRoute] = useState(parseHash());
  useEffect(() => {
    const onHash = () => setRoute(parseHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);
  const navigate = useCallback((to, opts = {}) => {
    let target = to;
    if (opts.query) {
      const qs = new URLSearchParams(opts.query).toString();
      target = `${to}?${qs}`;
    }
    if (opts.replace) window.location.replace('#' + target);
    else window.location.hash = target;
  }, []);
  return React.createElement(RouterCtx.Provider, { value: { ...route, navigate } }, children);
}

function useRouter() { return useContext(RouterCtx); }

function matchRoute(path, pattern) {
  const pp = pattern.split('/').filter(Boolean);
  const pa = path.split('/').filter(Boolean);
  if (pp.length !== pa.length) return null;
  const params = {};
  for (let i = 0; i < pp.length; i++) {
    if (pp[i].startsWith(':')) params[pp[i].slice(1)] = decodeURIComponent(pa[i]);
    else if (pp[i] !== pa[i]) return null;
  }
  return params;
}

/* ===================== AUTH ===================== */
const AuthCtx = createContext(null);
const ROLE_KEYS = { STUDENT: 'STUDENT', TEACHER: 'TEACHER', ADMIN: 'ADMIN' };

const DEMO_USERS = {
  STUDENT: { id:812, name:'Влада Максимова', email:'vlada@code.dev',     initials:'В', role:'STUDENT', level:6 },
  TEACHER: { id:113, name:'Алексей Петров',  email:'a.petrov@uni.ru',    initials:'А', role:'TEACHER', dept:'Алгоритмы и структуры данных' },
  ADMIN:   { id:54,  name:'София Орлова',    email:'sofia@admin.dev',    initials:'С', role:'ADMIN' },
};

function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('tp_user') || 'null'); }
    catch { return null; }
  });

  useEffect(() => {
    if (user) localStorage.setItem('tp_user', JSON.stringify(user));
    else localStorage.removeItem('tp_user');
  }, [user]);

  const login = useCallback((email, password, remember) => {
    // demo: pick role by email prefix
    const role = email.startsWith('teacher') || email.includes('petrov') || email.includes('smirnova')
      ? 'TEACHER'
      : email.startsWith('admin') || email.includes('sofia') || email.includes('orlova')
        ? 'ADMIN'
        : 'STUDENT';
    const u = { ...DEMO_USERS[role], email, emailVerified:true };
    setUser(u);
    return u;
  }, []);

  const register = useCallback((name, email) => {
    const u = { ...DEMO_USERS.STUDENT, name, email, initials:(name[0]||'У').toUpperCase(), emailVerified:false, pendingVerifyEmail:email };
    setUser(u);
    return u;
  }, []);

  // Гостевой вход — без регистрации, ограниченный демо-аккаунт
  const loginGuest = useCallback(() => {
    const u = {
      id: 0, name:'Гость', email:'guest@local', initials:'Г',
      role:'STUDENT', level:1, emailVerified:true, isGuest:true,
    };
    setUser(u);
    return u;
  }, []);

  // Вход/регистрация через провайдера (VK, Google, GitHub, Email-link…)
  const loginSocial = useCallback((provider) => {
    const names = { vk:'Пользователь VK', google:'Google User', github:'GitHub User', yandex:'Яндекс ID' };
    const u = {
      ...DEMO_USERS.STUDENT,
      name: names[provider] || 'Студент',
      email: `${provider}-user@code.dev`,
      initials: (names[provider] || 'С')[0],
      role:'STUDENT', emailVerified:true, provider,
    };
    setUser(u);
    return u;
  }, []);

  const logout = useCallback(() => setUser(null), []);
  const switchRole = useCallback((role) => setUser(DEMO_USERS[role]), []);

  return React.createElement(AuthCtx.Provider, { value: { user, login, register, loginGuest, loginSocial, logout, switchRole, setUser } }, children);
}
function useAuth() { return useContext(AuthCtx); }

/* ===================== TOASTS ===================== */
const ToastCtx = createContext(null);
function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const push = useCallback((t) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((arr) => [...arr, { id, ...t }]);
    setTimeout(() => setToasts((arr) => arr.filter((x) => x.id !== id)), t.duration || 3800);
  }, []);
  return React.createElement(ToastCtx.Provider, { value: { push } },
    children,
    React.createElement('div', { className: 'toast-stack' },
      toasts.map(t => React.createElement(Toast, { key: t.id, ...t }))
    )
  );
}
function useToast() { return useContext(ToastCtx); }
function Toast({ kind = 'lime', title, body }) {
  const cls = kind === 'err' ? 'toast err' : kind === 'warn' ? 'toast warn' : kind === 'info' ? 'toast info' : 'toast';
  const sym = kind === 'err' ? '!' : kind === 'warn' ? '!' : kind === 'info' ? 'i' : '✓';
  const symColor = kind === 'err' ? 'var(--danger)' : kind === 'warn' ? 'var(--warning)' : kind === 'info' ? 'var(--purple)' : 'var(--lime)';
  return React.createElement('div', { className: cls },
    React.createElement('span', { style:{color:symColor,fontWeight:800,minWidth:16,display:'inline-flex',justifyContent:'center'} }, sym),
    React.createElement('div', null,
      React.createElement('div', { className:'tt' }, title),
      body && React.createElement('div', { className:'tx' }, body),
    )
  );
}

/* ===================== MODAL ===================== */
function Modal({ open, onClose, title, children, footer, width }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === 'Escape') onClose && onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);
  if (!open) return null;
  return React.createElement('div', { className:'modal-backdrop', onClick:(e)=>{ if(e.target===e.currentTarget) onClose && onClose(); } },
    React.createElement('div', { className:'modal', style: width ? {maxWidth:width} : null },
      title && React.createElement('div', { className:'mh' },
        React.createElement('b', { style:{fontSize:16} }, title),
        React.createElement('button', { className:'icon-btn', onClick: onClose }, '✕')
      ),
      React.createElement('div', { className:'mb' }, children),
      footer && React.createElement('div', { className:'mf' }, footer)
    )
  );
}

function ConfirmDialog({ open, onClose, onConfirm, title, body, confirmLabel='Подтвердить', danger=false }) {
  return React.createElement(Modal, {
    open, onClose, title,
    footer: React.createElement(React.Fragment, null,
      React.createElement('button', { className:'btn btn-ghost btn-sm', onClick: onClose }, 'Отмена'),
      React.createElement('button', { className: `btn ${danger?'btn-danger':'btn-primary'} btn-sm`, onClick: () => { onConfirm && onConfirm(); onClose && onClose(); } }, confirmLabel),
    ),
  }, React.createElement('p', { className:'muted', style:{margin:0,fontSize:14} }, body));
}

/* ===================== LAYOUT PRIMITIVES ===================== */
function Brand({ pp, small }) {
  return React.createElement('div', { className:'brand', style: small ? {gap:8} : null },
    React.createElement('span', { className:'dot ' + (pp ? 'pp' : '') }),
    React.createElement('b', null, 'Toxic', React.createElement('span', { className:'pulse' }, ' Pulse'))
  );
}

function PageHeader({ title, subtitle, right }) {
  return React.createElement('div', { className:'page-h' },
    React.createElement('div', null,
      React.createElement('h1', null, title),
      subtitle && React.createElement('p', null, subtitle)
    ),
    right && React.createElement('div', { className:'wrap' }, right)
  );
}

function Topbar({ crumbHome, crumbCurrent, right, children }) {
  const { user } = useAuth();
  const { navigate } = useRouter();
  return React.createElement('div', { className:'topbar' },
    React.createElement('div', { className:'crumb' },
      crumbHome ? React.createElement(React.Fragment, null, crumbHome, ' / ', React.createElement('b', null, crumbCurrent)) : React.createElement('b', null, crumbCurrent || '')
    ),
    React.createElement('div', { className:'right' },
      children,
      right,
      user && React.createElement(UserMenu, null)
    )
  );
}

function UserMenu() {
  const { user, logout } = useAuth();
  const { navigate } = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const onDoc = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);
  const ppCls = user.role === 'STUDENT' ? '' : 'pp';
  return React.createElement('div', { style:{position:'relative'}, ref },
    React.createElement('button', { className:'avatar sm '+ppCls, style:{cursor:'pointer',border:0}, onClick:()=>setOpen(o=>!o), title:user.name },
      user.initials || (user.name || 'U')[0]
    ),
    open && React.createElement('div', { style:{
        position:'absolute', right:0, top:42, minWidth:220, background:'var(--surface)', border:'1px solid var(--border-2)',
        borderRadius:12, boxShadow:'0 30px 60px -20px #000', padding:8, zIndex:50
      } },
      React.createElement('div', { style:{padding:'10px 12px',borderBottom:'1px solid var(--border)',marginBottom:6} },
        React.createElement('div', { style:{fontSize:13,fontWeight:600} }, user.name),
        React.createElement('div', { className:'mono mut3', style:{fontSize:11,marginTop:2} }, user.email),
      ),
      React.createElement(MenuItem, { onClick:()=>{ setOpen(false); navigate(roleHome(user.role)); } }, 'Профиль'),
      React.createElement(MenuItem, { onClick:()=>{ setOpen(false); navigate('/settings/profile'); } }, 'Настройки'),
      user.role === 'ADMIN' && React.createElement(MenuItem, { onClick:()=>{ setOpen(false); navigate('/admin'); } }, 'Админ-панель'),
      React.createElement('div', { style:{height:1,background:'var(--border)',margin:'6px 0'} }),
      React.createElement(MenuItem, { onClick:()=>{ setOpen(false); logout(); window.location.hash='/login'; }, danger:true }, 'Выйти'),
    )
  );
}
function MenuItem({ children, onClick, danger }) {
  return React.createElement('button', {
    onClick, style:{
      display:'block', width:'100%', textAlign:'left', padding:'9px 12px', borderRadius:8,
      background:'transparent', border:0, cursor:'pointer', color: danger?'#ff8198':'var(--text)', fontSize:13.5, fontWeight:500
    },
    onMouseEnter:(e)=>{ e.currentTarget.style.background='var(--surface-2)'; },
    onMouseLeave:(e)=>{ e.currentTarget.style.background='transparent'; },
  }, children);
}

function roleHome(role) {
  if (role === 'TEACHER') return '/teacher/profile';
  if (role === 'ADMIN')   return '/admin';
  return '/';
}

/* ===================== SIDEBAR ===================== */
function Sidebar({ items, role, brandPP }) {
  const { path, navigate } = useRouter();
  const ppCls = role !== 'STUDENT' ? 'pp' : '';
  return React.createElement('nav', { className:'sb' },
    React.createElement('div', { className:'b' },
      React.createElement('span', { className:'dot '+(brandPP?'pp':'') }),
      role === 'ADMIN' ? 'Admin' : React.createElement(React.Fragment, null, 'Toxic', React.createElement('span', {className:'pulse', style:{fontFamily:'var(--serif)',fontStyle:'italic',color:'var(--purple)',fontWeight:400}}, ' Pulse'))
    ),
    items.map(it => {
      if (it.divider) return React.createElement('div', { key: it.divider, className:'sb-group' }, it.divider);
      const active = it.matches ? it.matches(path) : path === it.to;
      return React.createElement('button', {
        key: it.to + it.label,
        className: `navlink ${active?'active':''} ${active && ppCls?ppCls:''}`,
        onClick: () => navigate(it.to),
      }, React.createElement('span', { className:'ic' }), it.label);
    }),
    React.createElement('div', { className:'sb-bottom' },
      role === 'STUDENT' && React.createElement('div', { className:'card-soft', style:{padding:'12px 14px'} },
        React.createElement('div', { className:'mono mut3', style:{fontSize:10.5} }, 'Серия дней'),
        React.createElement('div', { className:'row', style:{marginTop:4,gap:8} },
          React.createElement('span', { className:'stat', style:{fontSize:22,color:'var(--lime)'} }, '7'),
          React.createElement('span', { className:'muted', style:{fontSize:12} }, '🔥 дней подряд')
        )
      ),
      React.createElement('button', {
        className:'navlink',
        style:{marginTop:14},
        onClick: () => { const { logout } = window.__auth; logout(); navigate('/login'); }
      }, React.createElement('span',{className:'ic'}), 'Выйти')
    )
  );
}

/* ===================== UTILS ===================== */
function Badge({ kind='muted', children, style }) {
  return React.createElement('span', { className:`badge badge-${kind}`, style }, children);
}
function Dot() { return React.createElement('span', { className:'dotb' }); }

function StatusBadge({ status }) {
  switch (status) {
    case 'solved':
    case 'accepted':
      return React.createElement(Badge, { kind:'lime' }, React.createElement(Dot), 'Решено');
    case 'attempted':
      return React.createElement(Badge, { kind:'purple' }, React.createElement(Dot), 'В процессе');
    case 'todo':
      return React.createElement(Badge, { kind:'muted' }, React.createElement(Dot), 'Не начато');
    case 'failed':
      return React.createElement(Badge, { kind:'danger' }, React.createElement(Dot), 'Ошибка тестов');
    case 'reviewing':
      return React.createElement(Badge, { kind:'warn' }, React.createElement(Dot), 'На проверке');
    default:
      return React.createElement(Badge, { kind:'muted' }, status);
  }
}

function DiffBadge({ diff }) {
  const kind = diff === 'Лёгкая' ? 'muted' : diff === 'Средняя' ? 'warn' : 'danger';
  return React.createElement(Badge, { kind }, diff);
}

function RoleBadge({ role }) {
  const map = { STUDENT:{k:'lime',l:'Студент'}, TEACHER:{k:'purple',l:'Преподаватель'}, ADMIN:{k:'purple',l:'Админ'} };
  const v = map[role] || map.STUDENT;
  return React.createElement(Badge, { kind:v.k }, v.l);
}

function StatCard({ label, value, badge, badgeKind='muted' }) {
  return React.createElement('div', { className:'card card-pad' },
    React.createElement('div', { className:'mut3', style:{fontSize:12,textTransform:'uppercase',letterSpacing:'.06em'} }, label),
    React.createElement('div', { className:'stat', style:{marginTop:6} }, value),
    badge && React.createElement('span', { className:`badge badge-${badgeKind}`, style:{marginTop:8,display:'inline-flex'} }, badge),
  );
}

function ProtectedRoute({ allow, children }) {
  const { user } = useAuth();
  const { navigate } = useRouter();
  useEffect(() => {
    if (!user) { navigate('/login', { replace:true }); return; }
    if (allow && !allow.includes(user.role)) { navigate(roleHome(user.role), { replace:true }); }
  }, [user, allow, navigate]);
  if (!user) return null;
  if (allow && !allow.includes(user.role)) return null;
  return children;
}

function EmptyState({ icon='∅', title, text, action }) {
  return React.createElement('div', { className:'empty' },
    React.createElement('div', { className:'ill' }, icon),
    React.createElement('b', { style:{fontSize:16} }, title),
    text && React.createElement('p', { className:'muted', style:{fontSize:13.5, margin:'8px auto 18px', maxWidth:320} }, text),
    action
  );
}

function RoleSwitcher() {
  const { user, switchRole, setUser } = useAuth();
  if (!user) return null;
  const triggerVerify = () => setUser({ ...user, emailVerified:false, pendingVerifyEmail:user.email });
  return React.createElement('div', { className:'role-switcher', title:'Демо: переключение роли' },
    React.createElement('span', { className:'rs-lbl' }, 'Demo · Роль'),
    React.createElement('button', { className: user.role==='STUDENT' ? 'on' : '', onClick:()=>switchRole('STUDENT') }, 'Студент'),
    React.createElement('button', { className: user.role==='TEACHER' ? 'on pp' : '', onClick:()=>switchRole('TEACHER') }, 'Преподаватель'),
    React.createElement('button', { className: user.role==='ADMIN' ? 'on adm' : '', onClick:()=>switchRole('ADMIN') }, 'Админ'),
    React.createElement('span', { style:{width:1, height:18, background:'var(--border-2)', margin:'0 4px'} }),
    React.createElement('button', { onClick:triggerVerify, title:'Показать баннер подтверждения email' }, '✉ Verify'),
  );
}

/* ===================== CONTRIB GRAPH (GitHub-style) ===================== */
function ContribGraph({ pp, weeks = 26 }) {
  const seed = useMemo(() => {
    const out = [];
    let s = 7;
    for (let w = 0; w < weeks; w++) {
      const days = [];
      for (let d = 0; d < 7; d++) {
        s = (s * 9301 + 49297) % 233280;
        const r = s / 233280;
        // skew so most cells are empty/low (GitHub-like distribution)
        const lv = r < 0.42 ? 0 : r < 0.66 ? 1 : r < 0.84 ? 2 : r < 0.94 ? 3 : 4;
        days.push(lv);
      }
      out.push(days);
    }
    return out;
  }, [weeks]);

  // Month labels spaced roughly every 4–5 weeks
  const monthNames = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];
  const now = new Date();
  const labels = [];
  // start: weeks*7 days ago, mark first week of each new month
  const startDate = new Date(now);
  startDate.setDate(now.getDate() - weeks * 7);
  let lastMonth = -1;
  for (let w = 0; w < weeks; w++) {
    const d = new Date(startDate);
    d.setDate(startDate.getDate() + w * 7);
    if (d.getMonth() !== lastMonth) {
      labels.push({ w, m: monthNames[d.getMonth()] });
      lastMonth = d.getMonth();
    }
  }
  // Build a months grid string: month spans, blanks otherwise
  const monthCells = Array.from({ length: weeks }, () => '');
  labels.forEach(({ w, m }) => { monthCells[w] = m; });
  const monthsStyle = { gridTemplateColumns: `repeat(${weeks}, 1fr)` };

  return React.createElement('div', { className: 'contrib-wrap ' + (pp ? 'pp' : '') },
    React.createElement('div', { className: 'contrib-months', style: monthsStyle },
      monthCells.map((m, i) => React.createElement('span', { key: i }, m))
    ),
    React.createElement('div', { className: 'contrib-grid' },
      React.createElement('div', { className: 'contrib-days' },
        ['', 'Пн', '', 'Ср', '', 'Пт', ''].map((d, i) => React.createElement('span', { key: i }, d))
      ),
      React.createElement('div', { className: 'contrib-weeks' },
        seed.map((week, i) => React.createElement('div', { key: i, className: 'contrib-week' },
          week.map((lv, j) => React.createElement('i', {
            key: j,
            className: lv ? `l${lv}` : '',
            title: lv ? `${lv * 2 + 1} решений` : 'нет решений'
          }))
        ))
      )
    ),
    React.createElement('div', { className: 'contrib-legend' },
      'меньше',
      [0,1,2,3,4].map(lv => React.createElement('i', {
        key: lv,
        style: {
          background: lv === 0 ? 'var(--surface-3)' :
            pp ? `rgba(139,83,254,${0.22 + lv * 0.18})` : `rgba(142,255,1,${0.22 + lv * 0.18})`
        }
      })),
      'больше'
    )
  );
}

/* ===================== EXPORT TO WINDOW ===================== */
Object.assign(window, {
  RouterProvider, useRouter, matchRoute,
  AuthProvider, useAuth,
  ToastProvider, useToast, Toast,
  Modal, ConfirmDialog,
  Brand, Sidebar, Topbar, UserMenu, PageHeader,
  Badge, Dot, StatusBadge, DiffBadge, RoleBadge, StatCard,
  ProtectedRoute, EmptyState, RoleSwitcher, ContribGraph,
  roleHome,
});
