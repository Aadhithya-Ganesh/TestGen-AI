import { NavLink } from "react-router-dom";
import { GalleryHorizontalEnd, Home, LayoutDashboard } from "lucide-react";

function Navigation() {
  const navItems = [
    { icon: Home, label: "Home", path: "/" },
    { icon: GalleryHorizontalEnd, label: "Jobs", path: "/jobs" },
  ];

  return (
    <ul className="text-muted-foreground flex gap-2">
      {navItems.map((item, index) => (
        <NavLink
          to={item.path}
          key={index}
          className={({ isActive }) =>
            `mx-2 rounded-lg p-2 px-3 ${
              isActive ? "bg-sidebar-accent" : "hover:bg-sidebar-accent"
            }`
          }
        >
          <li className="text-muted-foreground flex items-center gap-3">
            <item.icon size={20} />
            <p className="font-bold">{item.label}</p>
          </li>
        </NavLink>
      ))}
    </ul>
  );
}

export default Navigation;
