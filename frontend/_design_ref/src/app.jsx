/* global React, ReactDOM */
/* Main App: router + page dispatch */

function App() {
  const route = window.useRouter();
  const { path } = route;
  const { user } = window.useAuth();

  // Auth gate — redirect away from /login if logged in (UX nicety)
  React.useEffect(() => {
    if (user && (path === '/login' || path === '/register' || path === '/reset-password')) {
      window.location.hash = window.roleHome(user.role);
    }
    // alias /tasks → /
    if (path === '/tasks') window.location.replace('#/');
    if (path === '/signin') window.location.replace('#/login');
    if (path === '/student/groups') window.location.replace('#/student/profile?tab=groups');
    if (path === '/teacher/catalogs' || path === '/teacher/catalogs/') {
      window.location.replace('#/teacher/profile?tab=catalogs');
    }
  }, [path, user]);

  // ===== route table =====
  // public
  if (path === '/login')          return React.createElement(window.LoginPage);
  if (path === '/register')       return React.createElement(window.RegisterPage);
  if (path === '/reset-password') return React.createElement(window.ResetPasswordPage);

  // tasks home (student/all auth)
  if (path === '/' || path === '/tasks') return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.TasksPage));

  // task detail
  let m = window.matchRoute(path, '/tasks/:id');
  if (m) return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.TaskPage, { id: m.id }));

  // student profile / groups
  if (path === '/student/profile') return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.StudentProfilePage));
  // curriculum (Pascal track)
  if (path === '/learn/pascal') return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.PascalLanguagePage));
  m = window.matchRoute(path, '/learn/pascal/:chapterSlug');
  if (m) return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.PascalShowcasePage, { chapterSlug: m.chapterSlug }));
  m = window.matchRoute(path, '/student/groups/:groupId');
  if (m) return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.StudentGroupDetailPage, { groupId: m.groupId }));
  m = window.matchRoute(path, '/teachers/:teacherId');
  if (m) return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.TeacherPublicProfilePage, { teacherId: m.teacherId }));
  m = window.matchRoute(path, '/students/:studentId');
  if (m) return guard(['TEACHER','ADMIN'], React.createElement(window.StudentPublicProfilePage, { studentId: m.studentId }));

  // teacher
  if (path === '/teacher/profile') return guard(['TEACHER','ADMIN'], React.createElement(window.TeacherProfilePage));
  if (path === '/teacher/tasks')    return guard(['TEACHER','ADMIN'], React.createElement(window.TeacherTasksPage));
  if (path === '/teacher/create-task' || path === '/teacher/task-editor') {
    return guard(['TEACHER','ADMIN'], React.createElement(window.TaskEditorPage, { isEdit:false }));
  }
  m = window.matchRoute(path, '/teacher/tasks/:id/edit');
  if (m) return guard(['TEACHER','ADMIN'], React.createElement(window.TaskEditorPage, { taskId:m.id, isEdit:true }));
  m = window.matchRoute(path, '/teacher/assignments/:id/edit');
  if (m) return guard(['TEACHER','ADMIN'], React.createElement(window.TaskEditorPage, { taskId:m.id, isEdit:true }));
  m = window.matchRoute(path, '/teacher/catalogs/:catalogId');
  if (m) return guard(['TEACHER','ADMIN'], React.createElement(window.TeacherCatalogPage, { catalogId:m.catalogId }));
  m = window.matchRoute(path, '/teacher/code-assembly/:taskId/edit');
  if (m) return guard(['TEACHER','ADMIN'], React.createElement(window.TeacherEditCodeAssemblyPage, { taskId:m.taskId }));

  // admin
  if (path === '/admin')                  return guard(['ADMIN'], React.createElement(window.AdminOverviewPage));
  if (path === '/admin/users')            return guard(['ADMIN'], React.createElement(window.AdminUsersPage));
  m = window.matchRoute(path, '/admin/users/:userId');
  if (m) return guard(['ADMIN'], React.createElement(window.AdminUserDetailPage, { userId:m.userId }));
  if (path === '/admin/teacher-requests') return guard(['ADMIN'], React.createElement(window.AdminTeacherRequestsPage));
  if (path === '/admin/assignments')      return guard(['ADMIN'], React.createElement(window.AdminAssignmentsPage));
  if (path === '/admin/statistics')       return guard(['ADMIN'], React.createElement(window.AdminStatisticsPage));
  if (path === '/admin/create-teacher')   return guard(['ADMIN'], React.createElement(window.AdminCreateTeacherPage));

  // settings
  if (path === '/settings' || path === '/settings/')
    return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.SettingsLayout, { tab:'profile' },
      React.createElement(window.ProfileTab)));
  if (path === '/settings/profile')
    return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.SettingsLayout, { tab:'profile' }, React.createElement(window.ProfileTab)));
  if (path === '/settings/security')
    return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.SettingsLayout, { tab:'security' }, React.createElement(window.SecurityTab)));
  if (path === '/settings/learning')
    return guard(['STUDENT','TEACHER','ADMIN'], React.createElement(window.SettingsLayout, { tab:'learning' }, React.createElement(window.LearningTab)));
  if (path === '/settings/teacher')
    return guard(['TEACHER','ADMIN'], React.createElement(window.SettingsLayout, { tab:'teacher' }, React.createElement(window.TeacherSettingsTab)));

  // 404
  return React.createElement(NotFoundPage, { path });
}

function guard(allow, node) {
  return React.createElement(window.ProtectedRoute, { allow }, node);
}

function NotFoundPage({ path }) {
  const { user } = window.useAuth();
  const { navigate } = window.useRouter();
  return React.createElement('div', { style:{minHeight:'100vh', display:'grid', placeItems:'center', textAlign:'center', padding:40} },
    React.createElement('div', null,
      React.createElement('div', { style:{fontSize:84, fontWeight:800, letterSpacing:-3, lineHeight:1} },
        React.createElement('span', { style:{color:'var(--lime)'} }, '4'),
        React.createElement('span', { style:{fontFamily:'var(--serif)', fontStyle:'italic', color:'var(--purple)'} }, '0'),
        React.createElement('span', { style:{color:'var(--lime)'} }, '4'),
      ),
      React.createElement('h2', { style:{fontSize:22, margin:'14px 0 6px'} }, 'Страница потерялась'),
      React.createElement('p', { className:'muted mono', style:{fontSize:14, margin:'0 0 22px'} }, `${path || '/unknown'}`),
      React.createElement('div', { className:'wrap', style:{justifyContent:'center'} },
        React.createElement('button', { className:'btn btn-ghost', onClick:()=>history.back() }, '← Назад'),
        React.createElement('button', { className:'btn btn-primary', onClick:()=>navigate(user ? window.roleHome(user.role) : '/login') }, 'На главную'),
      )
    )
  );
}

/* ===== Root mount ===== */
function Root() {
  // expose auth helpers globally for the sidebar logout shortcut
  const auth = window.useAuth();
  React.useEffect(() => { window.__auth = auth; }, [auth]);
  return React.createElement(React.Fragment, null,
    React.createElement(window.VerifyEmailBanner),
    React.createElement(App),
    React.createElement(window.RoleSwitcher)
  );
}

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(
  React.createElement(window.RouterProvider, null,
    React.createElement(window.AuthProvider, null,
      React.createElement(window.ToastProvider, null,
        React.createElement(Root)
      )
    )
  )
);
