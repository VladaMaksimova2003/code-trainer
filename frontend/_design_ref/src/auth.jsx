/* global React */
const { useState } = React;

const SOCIAL_PROVIDERS = [
  { id:'vk',     label:'Войти через VK',     glyph:'VK' },
  { id:'google', label:'Войти через Google', glyph:'G' },
  { id:'github', label:'Войти через GitHub', glyph:'GH' },
];

function SocialAuth({ onPick, title }) {
  return React.createElement('div', { className:'social-subtle' },
    React.createElement('div', { className:'lbl' }, title || 'Или войдите через'),
    React.createElement('div', { className:'icons' },
      SOCIAL_PROVIDERS.map(p => React.createElement('button', {
        key:p.id, type:'button', className:`social-ico ${p.id}`, onClick:()=>onPick(p.id), title:p.label
      }, p.glyph))
    )
  );
}

function LoginPage() {
  const { login, loginGuest, loginSocial } = useAuth();
  const { navigate } = useRouter();
  const toast = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState('');

  const onSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) { setError('Заполните email и пароль.'); return; }
    if (password.length < 6) { setError('Пароль слишком короткий.'); return; }
    setError('');
    const u = login(email, password, remember);
    toast.push({ kind:'lime', title:'Добро пожаловать', body:`Вход как ${u.name}` });
    navigate(roleHome(u.role));
  };

  const onGuest = () => {
    const u = loginGuest();
    toast.push({ kind:'info', title:'Вы вошли как гость', body:'Прогресс не сохраняется между сессиями.' });
    navigate(roleHome(u.role));
  };

  const onSocial = (provider) => {
    const u = loginSocial(provider);
    toast.push({ kind:'lime', title:'Добро пожаловать', body:`Вход через ${provider.toUpperCase()}` });
    navigate(roleHome(u.role));
  };

  return React.createElement('div', { className:'auth-shell' },
    React.createElement('div', { className:'auth-split' },
      // brand panel
      React.createElement('div', { className:'auth-brand' },
        React.createElement(Brand),
        React.createElement('div', null,
          React.createElement('div', { style:{fontSize:34,fontWeight:800,letterSpacing:'-1px',lineHeight:1.1} },
            'Тренажёр, который', React.createElement('br'), 'учит писать ',
            React.createElement('em', { style:{fontFamily:'var(--serif)',fontStyle:'italic',fontWeight:400,color:'var(--lime)'} }, 'код')
          ),
          React.createElement('p', { className:'muted', style:{marginTop:14,maxWidth:340,fontSize:14} },
            'Задачи, автоматические тесты и прогресс — в одном тёмном минималистичном интерфейсе.'
          ),
          React.createElement('div', { className:'wrap', style:{marginTop:22} },
            React.createElement(Badge, { kind:'lime' }, '600+ задач'),
            React.createElement(Badge, { kind:'purple' }, '3 языка'),
            React.createElement(Badge, { kind:'muted' }, 'Авто-проверка'),
          ),
        ),
        React.createElement('span', { className:'mut3', style:{fontSize:12} }, '© 2026 Toxic Pulse')
      ),
      // form panel
      React.createElement('div', { className:'auth-form' },
        React.createElement('form', { className:'auth-form-inner', onSubmit },
          React.createElement('h1', { style:{fontSize:24,fontWeight:800,margin:'0 0 6px'} }, 'С возвращением'),
          React.createElement('p', { className:'muted', style:{fontSize:14,margin:'0 0 24px'} }, 'Войдите, чтобы продолжить обучение.'),
          error && React.createElement('div', { className:'note err', style:{marginBottom:14,padding:'10px 12px'} }, error),
          React.createElement('div', { className:'field' },
            React.createElement('label', { className:'label' }, 'Email'),
            React.createElement('input', { className:'input', type:'email', placeholder:'you@example.com', value:email, onChange:e=>setEmail(e.target.value), autoFocus:true })
          ),
          React.createElement('div', { className:'field' },
            React.createElement('label', { className:'label' }, 'Пароль'),
            React.createElement('input', { className:'input', type:'password', placeholder:'••••••••', value:password, onChange:e=>setPassword(e.target.value) })
          ),
          React.createElement('div', { className:'between', style:{margin:'4px 0 20px'} },
            React.createElement('label', { className:'check-row', onClick:e=>e.preventDefault() },
              React.createElement('span', { className:'checkbox '+(remember?'on':''), onClick:()=>setRemember(r=>!r) }),
              'Запомнить меня'
            ),
            React.createElement('a', { onClick:()=>navigate('/reset-password'), style:{fontSize:13,color:'var(--lime)',fontWeight:600,cursor:'pointer'} }, 'Забыли пароль?')
          ),
          React.createElement('button', { type:'submit', className:'btn btn-primary btn-full' }, 'Войти'),
          React.createElement('button', { type:'button', className:'btn-guest', style:{marginTop:10}, onClick:onGuest },
            '→ Войти без регистрации'
          ),
          React.createElement('p', { className:'muted', style:{textAlign:'center',fontSize:13.5,marginTop:20} },
            'Нет аккаунта? ',
            React.createElement('a', { onClick:()=>navigate('/register'), style:{color:'#b89bff',fontWeight:600,cursor:'pointer'} }, 'Зарегистрироваться')
          ),
          React.createElement(SocialAuth, { onPick:onSocial }),
        )
      )
    )
  );
}

function RegisterPage() {
  const { register, loginSocial } = useAuth();
  const { navigate } = useRouter();
  const toast = useToast();
  const [form, setForm] = useState({ name:'', email:'', password:'', invite:'' });
  const [errs, setErrs] = useState({});
  const [pwHint, setPwHint] = useState(false);

  const set = (k,v) => setForm(f => ({ ...f, [k]:v }));

  const onSocial = (provider) => {
    const u = loginSocial(provider);
    toast.push({ kind:'lime', title:'Аккаунт создан', body:`Регистрация через ${provider.toUpperCase()}` });
    navigate('/');
  };

  const onSubmit = (e) => {
    e.preventDefault();
    const ne = {};
    if (!form.name.trim()) ne.name = 'Укажите имя';
    if (!form.email.includes('@')) ne.email = 'Введите корректный email';
    if (form.password.length < 8) ne.password = 'Минимум 8 символов';
    setErrs(ne);
    if (Object.keys(ne).length) return;
    const u = register(form.name, form.email);
    if (form.invite.trim()) {
      const g = window.MOCK.groups.find(x => x.invite.toUpperCase() === form.invite.toUpperCase().trim());
      if (g) {
        toast.push({ kind:'lime', title:'Вы вступили в группу', body: g.name });
        navigate(`/student/groups/${g.id}`);
        return;
      } else {
        toast.push({ kind:'warn', title:'Инвайт-код не найден', body:'Аккаунт создан, но в группу вступить не удалось.' });
      }
    }
    toast.push({ kind:'lime', title:'Аккаунт создан', body:`Привет, ${u.name}!` });
    navigate('/');
  };

  return React.createElement('div', { className:'auth-shell' },
    React.createElement('form', { className:'auth-card', onSubmit },
      React.createElement('div', { className:'brand', style:{justifyContent:'center',marginBottom:18} },
        React.createElement('span',{className:'dot'}),
        React.createElement('b', null, 'Toxic', React.createElement('span',{className:'pulse'},' Pulse'))
      ),
      React.createElement('h1', { style:{fontSize:24,fontWeight:800,textAlign:'center',margin:'0 0 6px'} }, 'Создать аккаунт'),
      React.createElement('p', { className:'muted', style:{fontSize:14,textAlign:'center',margin:'0 0 24px'} }, 'Бесплатно. Старт за минуту.'),
      React.createElement(FormField, { label:'Имя', err:errs.name },
        React.createElement('input', { className:'input '+(errs.name?'err':''), placeholder:'Влада', value:form.name, onChange:e=>set('name',e.target.value) })
      ),
      React.createElement(FormField, { label:'Email', err:errs.email },
        React.createElement('input', { className:'input '+(errs.email?'err':''), type:'email', placeholder:'you@example.com', value:form.email, onChange:e=>set('email',e.target.value) })
      ),
      React.createElement(FormField, { label:'Пароль', err:errs.password, help: pwHint && !errs.password ? 'Используйте хотя бы 8 символов, цифры и буквы.' : null },
        React.createElement('input', { className:'input '+(errs.password?'err':''), type:'password', placeholder:'Минимум 8 символов', value:form.password, onChange:e=>set('password',e.target.value), onFocus:()=>setPwHint(true), onBlur:()=>setPwHint(false) })
      ),
      React.createElement(FormField, { label: React.createElement(React.Fragment,null,'Инвайт-код группы ', React.createElement('span',{className:'mut3'},'(необязательно)')) },
        React.createElement('input', { className:'input mono', placeholder:'GRP-7K2A', value:form.invite, onChange:e=>set('invite',e.target.value.toUpperCase()) })
      ),
      React.createElement('button', { type:'submit', className:'btn btn-primary btn-full', style:{marginTop:6} }, 'Зарегистрироваться'),
      React.createElement('p', { className:'mut3', style:{fontSize:12,textAlign:'center',margin:'14px 0 0'} }, 'Регистрируясь, вы принимаете условия использования'),
      React.createElement('p', { className:'muted', style:{textAlign:'center',fontSize:13.5,marginTop:14} },
        'Уже есть аккаунт? ',
        React.createElement('a', { onClick:()=>navigate('/login'), style:{color:'var(--lime)',fontWeight:600,cursor:'pointer'} }, 'Войти')
      ),
      React.createElement(SocialAuth, { onPick:onSocial, title:'Или зарегистрируйтесь через' }),
    )
  );
}

function FormField({ label, err, help, children }) {
  return React.createElement('div', { className:'field' },
    React.createElement('label', { className:'label' }, label),
    children,
    err
      ? React.createElement('div', { className:'help err' }, err)
      : help && React.createElement('div', { className:'help' }, help)
  );
}

function ResetPasswordPage() {
  const { navigate } = useRouter();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const onSubmit = (e) => { e.preventDefault(); if (email.includes('@')) setSent(true); };

  return React.createElement('div', { className:'auth-shell' },
    React.createElement('form', { className:'auth-card', style:{textAlign:'center'}, onSubmit },
      React.createElement('div', { style:{
        width:64,height:64,borderRadius:18,margin:'0 auto 18px',
        background:'var(--lime-soft)',border:'1px solid rgba(142,255,1,.3)',color:'var(--lime)',
        display:'grid',placeItems:'center',fontSize:26
      } }, sent ? '✓' : '↻'),
      React.createElement('h1', { style:{fontSize:22,fontWeight:800,margin:'0 0 6px'} }, sent ? 'Письмо отправлено' : 'Сброс пароля'),
      React.createElement('p', { className:'muted', style:{fontSize:14,margin:'0 0 22px'} },
        sent ? `Если ${email} есть в системе, мы отправили ссылку для восстановления.` : 'Введите email — пришлём ссылку для восстановления.'
      ),
      !sent && React.createElement(React.Fragment, null,
        React.createElement('div', { className:'field', style:{textAlign:'left'} },
          React.createElement('label', { className:'label' }, 'Email'),
          React.createElement('input', { className:'input', placeholder:'you@example.com', value:email, onChange:e=>setEmail(e.target.value), autoFocus:true })
        ),
        React.createElement('button', { type:'submit', className:'btn btn-primary btn-full' }, 'Отправить ссылку'),
      ),
      sent && React.createElement('button', { type:'button', className:'btn btn-ghost btn-full', onClick:()=>setSent(false) }, 'Отправить ещё раз'),
      React.createElement('a', { onClick:()=>navigate('/login'), style:{display:'inline-block',marginTop:18,fontSize:13.5,color:'var(--text-2)',cursor:'pointer'} }, '← Назад ко входу')
    )
  );
}

Object.assign(window, { LoginPage, RegisterPage, ResetPasswordPage, FormField });
