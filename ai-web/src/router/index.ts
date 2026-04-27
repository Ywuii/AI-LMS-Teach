// import "@/utils/sso";
import Cookies from "js-cookie";
import { getConfig } from "@/config";
import NProgress from "@/utils/progress";
import { buildHierarchyTree } from "@/utils/tree";
import remainingRouter from "./modules/remaining";
import { useMultiTagsStoreHook } from "@/store/modules/multiTags";
import { usePermissionStoreHook } from "@/store/modules/permission";
import { isUrl, openLink, cloneDeep, isAllEmpty, storageLocal } from "@pureadmin/utils";
import { ascending, getTopMenu, initRouter, isOneOfArray, getHistoryMode, findRouteByPath, handleAliveRoute, formatTwoStageRoutes, formatFlatteningRoutes } from "./utils";
import { type Router, type RouteRecordRaw, type RouteComponent, createRouter } from "vue-router";
import { type DataInfo, userKey, removeToken, multipleTabsKey } from "@/utils/auth";

/** 自动导入全部静态路由，无需再手动引入！匹配 src/router/modules 目录（任何嵌套级别）中具有 .ts 扩展名的所有文件，除了 remaining.ts 文件
 * 如何匹配所有文件请看：https://github.com/mrmlnc/fast-glob#basic-syntax
 * 如何排除文件请看：https://cn.vitejs.dev/guide/features.html#negative-patterns
 */

// const modules: Record<string, any> = import.meta.glob(["./modules/**/*.ts", "!./modules/**/remaining.ts", "!./modules/system.ts"], {
//   eager: true
// });

const modules: Record<string, any> = import.meta.glob(["./modules/**/*.ts", "!./modules/**/remaining.ts"], {
  eager: true
});

/** 原始静态路由（未做任何处理） */
const routes = [];

Object.keys(modules).forEach(key => {
  routes.push(modules[key].default);
});

/** 导出处理后的静态路由（三级及以上的路由全部拍成二级） */
export const constantRoutes: Array<RouteRecordRaw> = formatTwoStageRoutes(formatFlatteningRoutes(buildHierarchyTree(ascending(routes.flat(Infinity)))));

/** 初始的静态路由，用于退出登录时重置路由 */
const initConstantRoutes: Array<RouteRecordRaw> = cloneDeep(constantRoutes);

/** 用于渲染菜单，保持原始层级 */
export const constantMenus: Array<RouteComponent> = ascending(routes.flat(Infinity)).concat(...remainingRouter);

/** 不参与菜单的路由 */
export const remainingPaths = Object.keys(remainingRouter).map(v => {
  return remainingRouter[v].path;
});

/** 创建路由实例 */
export const router: Router = createRouter({
  history: getHistoryMode(import.meta.env.VITE_ROUTER_HISTORY),
  routes: constantRoutes.concat(...(remainingRouter as any)),
  strict: true,
  scrollBehavior(to, from, savedPosition) {
    return new Promise(resolve => {
      if (savedPosition) {
        return savedPosition;
      } else {
        if (from.meta.saveSrollTop) {
          const top: number = document.documentElement.scrollTop || document.body.scrollTop;
          resolve({ left: 0, top });
        }
      }
    });
  }
});

/** 重置路由 */
export function resetRouter() {
  router.clearRoutes();
  for (const route of initConstantRoutes.concat(...(remainingRouter as any))) {
    router.addRoute(route);
  }
  router.options.routes = formatTwoStageRoutes(formatFlatteningRoutes(buildHierarchyTree(ascending(routes.flat(Infinity)))));
  usePermissionStoreHook().clearAllCachePage();
}

/** 路由白名单 */
const whiteList = ["/login"];

const { VITE_HIDE_HOME } = import.meta.env;

router.beforeEach((to, _from, next) => {
  const userInfo = storageLocal().getItem(userKey);
  const multiTabs = Cookies.get(multipleTabsKey);

  console.log("🔵 beforeEach 触发");
  console.log("➡️ to.path:", to.path);
  console.log("⬅️ from.path:", _from.path);
  console.log("🧾 userInfo:", !!userInfo);
  console.log("🧾 multipleTabsKey:", multiTabs);

  if (to.meta?.keepAlive) {
    handleAliveRoute(to, "add");
    if (_from.name === undefined || _from.name === "Redirect") {
      handleAliveRoute(to);
    }
  }

  NProgress.start();

  const externalLink = isUrl(to?.name as string);
  if (!externalLink) {
    to.matched.some(item => {
      if (!item.meta.title) return "";
      const Title = getConfig().Title;
      if (Title) document.title = `${item.meta.title} | ${Title}`;
      else document.title = item.meta.title as string;
    });
  }

  function toCorrectRoute() {
    console.log("✅ toCorrectRoute 执行");
    whiteList.includes(to.fullPath) ? next(_from.fullPath) : next();
  }

  // ✅ 关键判断
  if (multiTabs && userInfo) {
    console.log("✅ 命中【已登录】分支");

    if (to.meta?.roles && !isOneOfArray(to.meta?.roles, userInfo?.roles)) {
      console.log("❌ 无权限 → 403");
      next({ path: "/error/403" });
      return;
    }

    if (VITE_HIDE_HOME === "true" && to.fullPath === "/welcome") {
      console.log("❌ 隐藏首页 → 404");
      next({ path: "/error/404" });
      return;
    }

    if (_from?.name) {
      if (externalLink) {
        console.log("🔗 外部链接");
        openLink(to?.name as string);
        NProgress.done();
      } else {
        console.log("✅ 正常跳转");
        toCorrectRoute();
      }
    } else {
      console.log("🔄 刷新页面逻辑");
      if (usePermissionStoreHook().wholeMenus.length === 0 && to.path !== "/login") {
        initRouter().then((router: Router) => {
          if (!useMultiTagsStoreHook().getMultiTagsCache) {
            const { path } = to;
            const route = findRouteByPath(path, router.options.routes[0].children);
            getTopMenu(true);
            if (route && route.meta?.title) {
              if (isAllEmpty(route.parentId) && route.meta?.backstage) {
                const { path, name, meta } = route.children[0];
                useMultiTagsStoreHook().handleTags("push", { path, name, meta });
              } else {
                const { path, name, meta } = route;
                useMultiTagsStoreHook().handleTags("push", { path, name, meta });
              }
            }
          }
          if (isAllEmpty(to.name)) router.push(to.fullPath);
        });
      }
      toCorrectRoute();
    }
  } else {
    console.log("❌ 命中【未登录】分支");

    if (to.path !== "/login") {
      if (whiteList.indexOf(to.path) !== -1) {
        console.log("✅ 白名单放行");
        next();
      } else {
        console.log("❌ 非白名单 → 回 login");
        removeToken();
        next({ path: "/login" });
      }
    } else {
      console.log("✅ 已在 login");
      next();
    }
  }
});

router.afterEach(() => {
  NProgress.done();
});

export default router;
