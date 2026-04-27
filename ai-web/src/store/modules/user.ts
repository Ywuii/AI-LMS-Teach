import { defineStore } from "pinia";
import { type userType, store, router, resetRouter, routerArrays, storageLocal } from "../utils";
import { type UserResult, type RefreshTokenResult, getLogin, refreshTokenApi, LoginResponse } from "@/api/user";
import { useMultiTagsStoreHook } from "./multiTags";
import { type DataInfo, setToken, removeToken, userKey } from "@/utils/auth";
import { message } from "@/utils/message";

export const useUserStore = defineStore("pure-user", {
  state: (): userType => ({
    // 头像
    // avatar: storageLocal().getItem<DataInfo<number>>(userKey)?.avatar ?? "",
    // 邮箱
    email: storageLocal().getItem<DataInfo<number>>(userKey)?.email ?? "",
    // 用户名
    username: storageLocal().getItem<DataInfo<number>>(userKey)?.username ?? "",
    // 昵称
    // nickname: storageLocal().getItem<DataInfo<number>>(userKey)?.nickname ?? "",
    // 页面级别权限
    // roles: storageLocal().getItem<DataInfo<number>>(userKey)?.roles ?? [],
    // 按钮级别权限
    // permissions: storageLocal().getItem<DataInfo<number>>(userKey)?.permissions ?? [],
    // 是否勾选了登录页的免登录
    isRemembered: false,
    // 登录页的免登录存储几天，默认7天
    loginDay: 7
  }),
  actions: {
    /** 存储头像 */
    // SET_AVATAR(avatar: string) {
    //   this.avatar = avatar;
    // },
    /** 存储邮箱 */
    SET_EMAIL(email: string) {
      this.email = email;
    },
    /** 存储用户名 */
    SET_USERNAME(username: string) {
      this.username = username;
    },
    /** 存储昵称 */
    // SET_NICKNAME(nickname: string) {
    //   this.nickname = nickname;
    // },
    /** 存储角色 */
    SET_ROLES(roles: Array<string>) {
      this.roles = roles;
    },
    /** 存储按钮级别权限 */
    // SET_PERMS(permissions: Array<string>) {
    //   this.permissions = permissions;
    // },
    /** 存储是否勾选了登录页的免登录 */
    SET_ISREMEMBERED(bool: boolean) {
      this.isRemembered = bool;
    },
    /** 设置登录页的免登录存储几天 */
    SET_LOGINDAY(value: number) {
      this.loginDay = Number(value);
    },
    /** 登入 */
    async loginByUsername(data) {
      return new Promise<LoginResponse>((resolve, reject) => {
        getLogin(data)
          .then(res => {
            console.log("后端返回",res)
            if (res.success) {
              setToken(res.token);              // ✅
              storageLocal().setItem(userKey, res.user);
              this.email = res.user.username;       // ✅
              this.username = res.user.username;
              resolve(res);
            } else {
              message(res.message, { type: "error" });
              reject(res);
            }
          })
          .catch(err => {
            message("登录失败", { type: "error" });
            reject(err);
          });
      });
    },
    /** 前端登出（不调用接口） */
    logOut() {
      console.log("登出")
      this.email = "";
      this.username = "";
      this.roles = [];
      this.permissions = [];
      removeToken();
      useMultiTagsStoreHook().handleTags("equal", [...routerArrays]);
      resetRouter();
      router.push("/login");
    },
  }
});

export function useUserStoreHook() {
  return useUserStore(store);
}
