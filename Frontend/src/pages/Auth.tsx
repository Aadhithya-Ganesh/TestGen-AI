import { redirect } from "react-router-dom";
import { apiFetch } from "../utils/Fetch";
import { toast } from "sonner";

const getToken = () => {
  return localStorage.getItem("token");
};

export const authLoader = async () => {
  const token = getToken();

  if (!token) {
    throw redirect("/");
  }

  try {
    const res = await apiFetch("/auth/me");
    return await res.json();
  } catch {
    localStorage.removeItem("token");
    toast.info("Session Timed out");
    throw redirect("/");
  }
};

export const optionalAuthLoader = async ({ request }: { request: Request }) => {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  let token = getToken();
  
  if (!token && code) {
    const res = await apiFetch(`/auth/login?code=${code}`, { method: "POST" });
    const data = await res.json();

    localStorage.setItem("token", data.access_token);
    toast.success("Logged in successfully");
    throw redirect(url.pathname);
  }

  if (token) {
    try {
      const res = await apiFetch("/auth/me");
      return await res.json();
    } catch {
      localStorage.removeItem("token");
      toast.info("Session Timed out");
      return null;
    }
  }

  return null;
};
