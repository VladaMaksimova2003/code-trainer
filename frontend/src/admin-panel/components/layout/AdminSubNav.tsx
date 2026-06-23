import { NavLink, useLocation } from "react-router-dom"
import { ADMIN_SECTIONS } from "@/admin-panel/config/adminSections"
import { isSuperUser } from "@/shared/utils/superUser"

export { ADMIN_SECTIONS } from "@/admin-panel/config/adminSections"

export default function AdminSubNav({ user }) {
  const { pathname } = useLocation()
  const sections = ADMIN_SECTIONS.filter(
    (item) => item.to !== "/admin/create-admin" || isSuperUser(user)
  )

  return (
    <nav className="ap-subnav tabbar" aria-label="Разделы панели управления">
      {sections.map((item) => {
        const active = item.match(pathname)
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={() => `ap-subnav-link${active ? " active on pp" : ""}`}
          >
            {item.label}
          </NavLink>
        )
      })}
    </nav>
  )
}
