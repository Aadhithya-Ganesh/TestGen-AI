import { redirect } from "react-router-dom";

type ApiFetchOptions = RequestInit & {
  params?: Record<string, string | number | boolean>;
};

export async function apiFetch(
  route: string,
  options: ApiFetchOptions = {},
): Promise<Response> {
  const baseUrl = `http://${import.meta.env.VITE_BACKEND_HOST}:${import.meta.env.VITE_BACKEND_PORT}${route}`;
  const token = localStorage.getItem("token");

  const { params, ...fetchOptions } = options;

  let url = baseUrl;

  if (params) {
    const query = new URLSearchParams(
      Object.entries(params).map(([key, value]) => [key, String(value)]),
    ).toString();

    if (query) url += `?${query}`;
  }

  const headers: Record<string, string> = {
    ...((fetchOptions.headers as Record<string, string>) || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const isJsonBody =
    fetchOptions.body &&
    typeof fetchOptions.body === "object" &&
    !(fetchOptions.body instanceof FormData) &&
    !(fetchOptions.body instanceof URLSearchParams);

  if (isJsonBody) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
    body: isJsonBody
      ? JSON.stringify(fetchOptions.body)
      : (fetchOptions.body as BodyInit | null),
  });

  if (response.status === 401 && token) {
    localStorage.removeItem("token");
    throw redirect("/");
  }

  if (!response.ok) {
    let errorBody: any = {};

    try {
      errorBody = await response.json();
    } catch {}

    throw new Response(
      JSON.stringify({
        message: errorBody.detail || errorBody.message || "Request failed",
      }),
      {
        status: response.status,
        headers: { "Content-Type": "application/json" },
      },
    );
  }

  return response;
}
