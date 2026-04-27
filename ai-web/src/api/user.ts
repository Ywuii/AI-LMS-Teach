import { http } from "@/utils/http";

export interface LoginResponse {
  success: boolean;
  message: string;
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
}

/** 登录 */
export const getLogin = (data: { username: string; password: string }) => {
  return http.request<LoginResponse>("post", "/api/auth/login/", { data });
};

/** 退出登录 */
export const logoutApi = () => {
  return http.request<{ success: boolean; message: string }>(
    "post",
    "/api/auth/logout/"
  );
};