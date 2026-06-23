import { useEffect, useMemo, useState } from "react";

import { useNavigate, useOutletContext, useParams } from "react-router-dom";

import {
  assignAdminUserRole,
  fetchAdminUser,
  patchAdminUserBlocked,
  removeAdminUserRole,
} from "@/admin-panel/api/admin";

import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource";

import { ApSpinner, ApAlert } from "@/admin-panel/components/ui/ApFeedback";

import { ApConfirmDialog } from "@/admin-panel/components/ui/ApModal";

import RoleAvatar from "@/shared/ui/RoleAvatar";

import RoleBadge from "@/shared/ui/RoleBadge";

import Badge from "@/shared/ui/Badge";

import {
  formatLastLogin,
  formatNumber,
  formatRegistrationDate,
} from "@/shared/utils/format";

import {
  isProtectedSuperUserEmail,
  isSuperUser,
} from "@/shared/utils/superUser";

import { requestPasswordReset } from "@/shared/api";

import { toast } from "@/shared/ui/toast";

const ALL_ROLES = [
  { value: "student", label: "Студент" },
  { value: "teacher", label: "Преподаватель" },
  { value: "admin", label: "Админ" },
]

const OPTIONAL_ROLES = ALL_ROLES.filter((role) => role.value !== "student")

function KvRow({ label, value, onClick = null }) {
  const clickable = typeof onClick === "function";

  return (
    <div
      className="between"
      style={{
        padding: "11px 0",

        borderTop: "1px solid var(--border)",

        cursor: clickable ? "pointer" : undefined,
      }}
      onClick={onClick || undefined}
      role={clickable ? "button" : undefined}
      tabIndex={clickable ? 0 : undefined}
      onKeyDown={
        clickable
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();

                onClick();
              }
            }
          : undefined
      }
    >
      <span className="muted" style={{ fontSize: 13 }}>
        {label}
      </span>

      {typeof value === "string" || typeof value === "number" ? (
        <b
          style={{ fontSize: 13, color: clickable ? "var(--lime)" : undefined }}
        >
          {value}
        </b>
      ) : (
        value
      )}
    </div>
  );
}

function userIsTeacher(user) {
  return (user?.roles || []).some((r) => r === "teacher" || r === "admin");
}

function primaryRole(user) {
  const roles = user?.roles || [];

  if (roles.includes("admin")) return "admin";

  if (roles.includes("teacher")) return "teacher";

  return roles[0] || "student";
}

function rolesEqual(a = [], b = []) {
  if (a.length !== b.length) return false;

  const setA = new Set(a);

  return b.every((role) => setA.has(role));
}

function optionalRoleChipClass(role, checked) {
  if (role === "admin") return `${checked ? "on " : ""}adm`.trim()
  if (role === "teacher") return `${checked ? "on " : ""}pp`.trim()
  return checked ? "on" : ""
}

export default function UserDetailPage() {
  const { userId } = useParams();

  const navigate = useNavigate();

  const { currentAdminUser } = useOutletContext() || {};

  const id = Number(userId);

  const viewerIsSuper = isSuperUser(currentAdminUser);

  const [busy, setBusy] = useState(false);

  const [confirm, setConfirm] = useState(null);

  const [pendingOptionalRoles, setPendingOptionalRoles] = useState([])

  const {
    data: user,
    loading,
    error,
    reload,
  } = useAsyncResource(() => fetchAdminUser(id), [id])

  const optionalRoles = useMemo(
    () => (viewerIsSuper ? OPTIONAL_ROLES : OPTIONAL_ROLES.filter((r) => r.value !== "admin")),
    [viewerIsSuper],
  )

  useEffect(() => {
    if (user && isProtectedSuperUserEmail(user.email)) {
      navigate("/admin/users", { replace: true });
    }
  }, [user, navigate]);

  useEffect(() => {
    if (user?.roles) {
      setPendingOptionalRoles(user.roles.filter((role) => role !== "student"))
    }
  }, [user?.id, user?.roles])

  const currentOptionalRoles = useMemo(
    () => (user?.roles || []).filter((role) => role !== "student"),
    [user?.roles],
  )

  const rolesDirty = user ? !rolesEqual(currentOptionalRoles, pendingOptionalRoles) : false

  const run = async (fn, toastTitle, toastBody, afterSuccess) => {
    setBusy(true);

    try {
      await fn();

      toast.push({ kind: "lime", title: toastTitle, body: toastBody });

      if (afterSuccess) {
        afterSuccess();
      } else {
        await reload();
      }
    } catch (err) {
      toast.error(
        "Ошибка",
        err?.response?.data?.detail ||
          err?.message ||
          "Не удалось выполнить действие",
      );
    } finally {
      setBusy(false);

      setConfirm(null);
    }
  };

  const toggleOptionalRole = (role) => {
    if (role === "student") return
    setPendingOptionalRoles((prev) =>
      prev.includes(role) ? prev.filter((item) => item !== role) : [...prev, role],
    )
  }

  const saveRoles = () => {
    if (!user) return

    const current = new Set(currentOptionalRoles)
    const pending = new Set(pendingOptionalRoles)
    const toAdd = [...pending].filter((role) => !current.has(role))
    const toRemove = [...current].filter((role) => !pending.has(role))

    run(
      async () => {
        for (const role of toAdd) {
          await assignAdminUserRole(id, role)
        }
        for (const role of toRemove) {
          await removeAdminUserRole(id, role)
        }
      },
      "Роли обновлены",
      ["Студент", ...pendingOptionalRoles.map((r) => ALL_ROLES.find((item) => item.value === r)?.label || r)]
        .filter(Boolean)
        .join(", "),
    )
  }

  const openTeacherCabinet = (tab) => {
    navigate(`/teacher/cabinet?tab=${tab}&teacherId=${id}`);
  };

  const resetPassword = () => {
    if (!user?.email) return

    run(
      () => requestPasswordReset(user.email),
      "Письмо отправлено",
      "Код для сброса пароля отправлен на email пользователя.",
    )
  };

  const sendInvite = () => {
    toast.push({
      kind: "info",

      title: "Инвайт отправлен",

      body: "Приглашение отправлено на email пользователя.",
    });
  };

  if (loading && !user) return <ApSpinner />;

  if (error && !user) {
    return (
      <>
        <ApAlert message={error} />

        <button
          type="button"
          className="btn btn-ghost btn-sm"
          onClick={() => navigate("/admin/users")}
        >
          ← Все пользователи
        </button>
      </>
    );
  }

  if (!user || isProtectedSuperUserEmail(user.email)) return null;

  const avatarRole = primaryRole(user);

  const teacherProfile = userIsTeacher(user);

  const statusKind = user.is_deleted
    ? "danger"
    : user.is_blocked
      ? "danger"
      : "muted";

  const statusLabel = user.is_deleted
    ? "Удалён"
    : user.is_blocked
      ? "Заблокирован"
      : "Активен";

  const memberGroups = user.member_group_names || [];

  const streakDays = user.streak_days ?? 0;

  return (
    <>
      <button
        type="button"
        className="btn btn-ghost btn-sm"
        style={{ marginBottom: 16 }}
        onClick={() => navigate("/admin/users")}
      >
        ← Все пользователи
      </button>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "300px 1fr",
          gap: 20,
          alignItems: "start",
        }}
      >
        <aside
          className="card card-pad glow-card"
          style={{ textAlign: "center" }}
        >
          <RoleAvatar
            name={user.name}
            role={avatarRole}
            size="lg"
            style={{ margin: "0 auto 12px" }}
          />

          <b style={{ fontSize: 17 }}>{user.name}</b>

          <p
            className="mut3 mono"
            style={{ fontSize: 12.5, margin: "4px 0 12px" }}
          >
            {user.email}
          </p>

          {user.about ? (
            <p
              className="muted"
              style={{
                fontSize: 13,

                lineHeight: 1.5,

                margin: "0 0 12px",

                textAlign: "left",

                whiteSpace: "pre-wrap",
              }}
            >
              {user.about}
            </p>
          ) : null}

          <div
            className="wrap"
            style={{ justifyContent: "center", marginBottom: 18 }}
          >
            {[...new Set(["student", ...(user.roles || [])])].map((role) => (
              <RoleBadge key={role} role={role} />
            ))}

            <Badge kind={statusKind}>
              <span className="dotb" />

              {statusLabel}
            </Badge>
          </div>

          <div className="grid" style={{ gap: 0, textAlign: "left" }}>
            <KvRow
              label="Регистрация"
              value={formatRegistrationDate(user.created_at)}
            />

            <KvRow
              label="Последний вход"
              value={formatLastLogin(user.last_login_at)}
            />

            <KvRow
              label="Решено задач"
              value={
                <b style={{ color: "var(--lime)" }}>
                  {formatNumber(user.solved_tasks_count)}
                </b>
              }
            />

            <KvRow
              label="Серия дней"
              value={
                <b style={{ color: "var(--lime)" }}>
                  {formatNumber(streakDays)}

                  {streakDays > 0 ? " 🔥" : ""}
                </b>
              }
            />

            <KvRow label="Точность" value={`${user.success_rate ?? 0}%`} />

            <KvRow
              label="Группы"
              value={formatNumber(
                user.member_groups_count ?? memberGroups.length,
              )}
            />

            {teacherProfile ? (
              <>
                <KvRow
                  label="Создано задач"
                  value={formatNumber(user.created_tasks_count ?? 0)}
                  onClick={() => openTeacherCabinet("tasks")}
                />

                <KvRow
                  label="Создано каталогов"
                  value={formatNumber(user.created_catalogs_count ?? 0)}
                  onClick={() => openTeacherCabinet("tasks")}
                />

                <KvRow
                  label="Группы (преп.)"
                  value={formatNumber(user.groups_count ?? 0)}
                  onClick={() => openTeacherCabinet("groups")}
                />
              </>
            ) : null}
          </div>
        </aside>

        <div className="grid" style={{ gap: 16 }}>
          <div className="card card-pad">
            <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>
              Управление аккаунтом
            </b>

            <p
              className="muted"
              style={{ fontSize: 12.5, margin: "0 0 14px", lineHeight: 1.45 }}
            >
              {viewerIsSuper
                ? "Студент по умолчанию. Дополнительно: преподаватель, администратор."
                : "Студент по умолчанию. Дополнительно: преподаватель."}
            </p>

            <div className="wrap" style={{ gap: 8, marginBottom: 14 }}>
              <span
                className="chip on"
                style={{ cursor: "default", userSelect: "none", opacity: 0.92 }}
                title="Базовая роль, снять нельзя"
              >
                Студент
              </span>
              {optionalRoles.map(({ value, label }) => {
                const checked = pendingOptionalRoles.includes(value)

                return (
                  <label
                    key={value}
                    className={`chip ${optionalRoleChipClass(value, checked)}`.trim()}
                    style={{ cursor: "pointer", userSelect: "none" }}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleOptionalRole(value)}
                      style={{
                        position: "absolute",
                        opacity: 0,
                        width: 0,
                        height: 0,
                      }}
                    />

                    {label}
                  </label>
                );
              })}
            </div>

            <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={busy || !rolesDirty}
                onClick={saveRoles}
              >
                Сохранить роли
              </button>

              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={resetPassword}
                disabled={busy}
              >
                Сбросить пароль
              </button>

              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={sendInvite}
                disabled={busy}
              >
                Отправить инвайт
              </button>
            </div>
          </div>

          {memberGroups.length > 0 ? (
            <div className="card card-pad">
              <b style={{ fontSize: 14, display: "block", marginBottom: 12 }}>
                Группы пользователя
              </b>

              <div className="wrap">
                {memberGroups.map((groupName) => (
                  <Badge key={groupName} kind="purple">
                    {groupName}
                  </Badge>
                ))}
              </div>
            </div>
          ) : null}

          <div
            className="card card-pad"
            style={{ borderColor: "rgba(255,77,106,.3)" }}
          >
            <div className="between" style={{ flexWrap: "wrap", gap: 12 }}>
              <div>
                <b style={{ fontSize: 14, color: "#ff8198" }}>Опасная зона</b>

                <p
                  className="muted"
                  style={{ fontSize: 13, margin: "4px 0 0" }}
                >
                  Блокировка ограничит доступ пользователя к платформе.
                </p>
              </div>

              {!user.is_deleted ? (
                <button
                  type="button"
                  className="btn btn-danger btn-sm"
                  disabled={busy}
                  onClick={() =>
                    setConfirm({
                      kind: "block",

                      title: user.is_blocked
                        ? "Разблокировать пользователя?"
                        : "Заблокировать пользователя?",

                      body: user.is_blocked
                        ? "Пользователь снова сможет войти в систему."
                        : "Пользователь не сможет войти в систему, пока вы не разблокируете аккаунт.",

                      danger: !user.is_blocked,

                      confirmLabel: user.is_blocked
                        ? "Разблокировать"
                        : "Заблокировать",
                    })
                  }
                >
                  {user.is_blocked ? "Разблокировать" : "Заблокировать"}
                </button>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      <ApConfirmDialog
        open={Boolean(confirm)}
        title={confirm?.title}
        body={confirm?.body}
        danger={confirm?.danger}
        confirmLabel={confirm?.confirmLabel}
        loading={busy}
        onClose={() => setConfirm(null)}
        onConfirm={() => {
          if (confirm?.kind === "block") {
            run(
              () => patchAdminUserBlocked(id, !user.is_blocked),

              user.is_blocked
                ? "Пользователь разблокирован"
                : "Пользователь заблокирован",
            );

            return;
          }
        }}
      />
    </>
  );
}
