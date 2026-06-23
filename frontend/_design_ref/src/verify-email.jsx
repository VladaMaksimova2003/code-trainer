/* global React */
/* Email verification banner — sticky at top until user verifies. */
const { useState: useStV, useEffect: useEfV, useRef: useRfV, useCallback: useCbV } = React;

const DEMO_OTP = '123456';

function VerifyEmailBanner() {
  const { user, setUser } = window.useAuth();
  const { path } = window.useRouter();
  const toast = window.useToast();

  const [dismissed, setDismissed] = useStV(false);
  // Reset dismiss on every route change (so banner reappears)
  useEfV(() => { setDismissed(false); }, [path]);

  // Body padding adjustment
  const visible = !!(user && user.emailVerified === false && !dismissed);
  useEfV(() => {
    if (visible) document.body.classList.add('has-banner');
    else document.body.classList.remove('has-banner');
    return () => document.body.classList.remove('has-banner');
  }, [visible]);

  // ----- OTP state -----
  const [digits, setDigits]     = useStV(['','','','','','']);
  const [status, setStatus]     = useStV('idle'); // idle | loading | error | success
  const [errorMsg, setErrorMsg] = useStV('');
  const [resendIn, setResendIn] = useStV(30);
  const inputsRef = useRfV([]);

  // Resend countdown
  useEfV(() => {
    if (!visible) return;
    const t = setInterval(() => setResendIn(n => Math.max(0, n-1)), 1000);
    return () => clearInterval(t);
  }, [visible]);
  // Reset state when banner re-shows for new email
  useEfV(() => {
    if (visible) {
      setDigits(['','','','','','']); setStatus('idle'); setErrorMsg('');
    }
  }, [user?.pendingVerifyEmail]);

  // ----- OTP handlers -----
  const submit = useCbV((codeArr) => {
    const code = codeArr.join('');
    if (code.length < 6) return;
    setStatus('loading'); setErrorMsg('');
    setTimeout(() => {
      if (code === DEMO_OTP) {
        setStatus('success');
        // brief delay then mark verified
        setTimeout(() => {
          setUser({ ...user, emailVerified:true, pendingVerifyEmail:null });
          toast.push({ kind:'lime', title:'Email подтверждён', body:user.email });
        }, 600);
      } else {
        setStatus('error');
        setErrorMsg('Неверный код. Попробуйте ещё раз.');
        // small reset of last 3 cells so user can retry
        setTimeout(() => {
          setDigits(['','','','','','']);
          inputsRef.current[0] && inputsRef.current[0].focus();
          setStatus('idle');
        }, 1100);
      }
    }, 700);
  }, [user, setUser, toast]);

  const setDigit = (i, val) => {
    const cleaned = val.replace(/[^0-9]/g,'').slice(0,1);
    setDigits(prev => {
      const next = [...prev]; next[i] = cleaned;
      if (cleaned && i < 5) inputsRef.current[i+1] && inputsRef.current[i+1].focus();
      if (next.every(d => d !== '') && next.join('').length === 6) submit(next);
      return next;
    });
  };

  const onKeyDown = (i) => (e) => {
    if (e.key === 'Backspace' && !digits[i] && i > 0) {
      inputsRef.current[i-1] && inputsRef.current[i-1].focus();
      setDigits(prev => { const n=[...prev]; n[i-1]=''; return n; });
      e.preventDefault();
    } else if (e.key === 'ArrowLeft' && i > 0) { inputsRef.current[i-1].focus(); e.preventDefault(); }
    else if (e.key === 'ArrowRight' && i < 5) { inputsRef.current[i+1].focus(); e.preventDefault(); }
  };

  const onPaste = (e) => {
    const txt = (e.clipboardData.getData('text') || '').replace(/[^0-9]/g,'').slice(0,6);
    if (!txt) return;
    e.preventDefault();
    const next = ['','','','','',''];
    for (let i=0; i<txt.length; i++) next[i] = txt[i];
    setDigits(next);
    const focusIdx = Math.min(txt.length, 5);
    inputsRef.current[focusIdx] && inputsRef.current[focusIdx].focus();
    if (txt.length === 6) submit(next);
  };

  const resend = () => {
    setResendIn(30); setStatus('idle'); setErrorMsg('');
    setDigits(['','','','','','']);
    toast.push({ kind:'info', title:'Код отправлен повторно', body:`Проверьте почту ${user.email}` });
    setTimeout(() => inputsRef.current[0] && inputsRef.current[0].focus(), 50);
  };

  if (!visible) return null;

  const otpCls = status === 'success' ? 'ok' : status === 'error' ? 'err' : '';

  return React.createElement('div', { className: `verify-banner ${status==='success'?'ok':status==='error'?'err':''}` },
    React.createElement('div', { className:'verify-inner' },
      // text block
      React.createElement('div', { className:'verify-text' },
        React.createElement('b', null,
          '🔒 Подтвердите email',
          status === 'success' && React.createElement('span', { style:{color:'var(--lime)', marginLeft:8, fontWeight:600} }, '· подтверждено'),
        ),
        React.createElement('div', { className:'row2' },
          React.createElement('span', null,
            'Мы отправили код на ',
            React.createElement('span', { className:'email' }, user.pendingVerifyEmail || user.email)
          ),
          React.createElement('span', { className:'mut3' }, '·'),
          resendIn > 0
            ? React.createElement('span', { className:'mut3' }, `повтор через ${formatTime(resendIn)}`)
            : React.createElement('button', { className:'verify-resend', onClick:resend }, 'Отправить код повторно'),
          React.createElement('span', { className:'mut3' }, '·'),
          React.createElement('span', { className:'mut3', style:{fontFamily:'var(--mono)'} }, 'тестовый код: 123456'),
        )
      ),
      // OTP + status
      React.createElement('div', { className:'row', style:{gap:14} },
        React.createElement('div', { className:`otp ${otpCls}` },
          digits.map((d, i) => React.createElement('input', {
            key:i,
            ref: el => inputsRef.current[i] = el,
            type:'text',
            inputMode:'numeric',
            autoComplete:'one-time-code',
            maxLength:1,
            value:d,
            className: d ? 'filled' : '',
            disabled: status === 'loading' || status === 'success',
            onChange: e => setDigit(i, e.target.value),
            onKeyDown: onKeyDown(i),
            onPaste,
            onFocus: e => e.target.select(),
          }))
        ),
        React.createElement('div', { className:`otp-status ${status}` },
          status === 'loading' && React.createElement(React.Fragment, null,
            React.createElement('span', { className:'spinner' }), 'Проверка…'),
          status === 'error' && React.createElement(React.Fragment, null,
            React.createElement('span', { style:{fontWeight:800, fontSize:14} }, '!'), errorMsg),
          status === 'success' && React.createElement(React.Fragment, null,
            React.createElement('span', { style:{fontWeight:800, fontSize:14} }, '✓'), 'Email подтверждён'),
        )
      ),
      // close
      React.createElement('button', {
        className:'verify-close',
        onClick:()=>setDismissed(true),
        title:'Скрыть до следующей страницы',
        disabled: status==='loading' || status==='success'
      }, '✕')
    )
  );
}

function formatTime(sec) {
  const m = Math.floor(sec/60); const s = sec % 60;
  return `${m}:${String(s).padStart(2,'0')}`;
}

Object.assign(window, { VerifyEmailBanner, DEMO_OTP });
