import Logo from "./Logo.tsx";
import Navigation from "./../components/Navigation.tsx";
import { FaGithub } from "react-icons/fa";
import { LogOut, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useRef, useState } from "react";
import DropdownMenu from "./ui/DropdownMenu.tsx";
import DropdownItem from "./ui/DropdownItem.tsx";
import { toast } from "sonner";

function Navbar({ user }: { user: any }) {
  const navigate = useNavigate();

  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const triggerRef = useRef(null);

  const handleLogin = () => {
    window.location.assign(
      `https://github.com/login/oauth/authorize?client_id=${import.meta.env.VITE_GITHUB_CLIENT_ID}&scope=repo`,
    );
  };

  const token = localStorage.getItem("token");

  return (
    <div className="bg-background border-border sticky top-0 z-100 flex w-full items-center justify-between border-b px-30 py-5">
      <div>
        <Logo />
      </div>
      {token && <Navigation />}
      {!token && (
        <div className="cursor-pointer" onClick={handleLogin}>
          <FaGithub className="size-10" />
        </div>
      )}
      {token && (
        <div className="relative hidden md:block">
          <button
            ref={triggerRef}
            onClick={() => setUserMenuOpen((prev) => !prev)}
            className="hover:bg-accent text-foreground flex h-11 w-11 cursor-pointer items-center justify-center rounded-lg transition-colors"
          >
            <img
              src={user.avatar_url}
              className="hover:border-primary rounded-full border-4 border-black/10 transition-colors"
            ></img>
          </button>

          <DropdownMenu
            open={userMenuOpen}
            onClose={() => setUserMenuOpen(false)}
            triggerRef={triggerRef}
          >
            <div className="px-4 py-3">
              <div className="flex items-center gap-3">
                {/* Avatar */}
                <div className="bg-primary/10 text-primary flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold">
                  {user?.username?.[0]?.toUpperCase()}
                </div>

                {/* Name */}
                <div className="min-w-0">
                  <p className="text-foreground truncate text-sm font-semibold">
                    {user?.username}
                  </p>
                  <p className="text-muted-foreground text-xs">Account</p>
                </div>
              </div>
            </div>

            <div className="border-border my-1 border-t" />

            <DropdownItem
              icon={LogOut}
              label="Logout"
              danger
              onClick={() => {
                localStorage.removeItem("token");
                setUserMenuOpen(false);
                toast.success("Logged out");
                navigate("/");
              }}
            />
          </DropdownMenu>
        </div>
      )}
    </div>
  );
}

export default Navbar;
