export class ApiError extends Error {
  constructor(public status: number, public body: string) {
    super(`API ${status}: ${body}`);
  }
}

function getInitData(): string {
  if (typeof window !== "undefined") {
    return window.Telegram?.WebApp?.initData || "";
  }
  return "";
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://myapi26.share.zrok.io/api";

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const initData = getInitData();

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(initData && { "Authorization": `TelegramInitData ${initData}` }),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(res.status, body);
  }

  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  return (data && typeof data === "object" && "results" in data ? data.results : data) as T;
}
