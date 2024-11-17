import { createRouter, createWebHistory } from "vue-router";

const routes = Object.entries(import.meta.glob('../pages/**/*.vue')).map(([path, component]) => {
    const p = path.replace("/pages", "").replace("/index", "").slice(2, -4);
    const routePath = p === '/home' ? '/' : p;
    return {
        path: routePath,
        component: component
    };
});

routes.push({
    path: '/cdetail/:id',
    component: () => import('../pages/cdetail/index.vue'),
});

routes.push({
    path: '/community/course/:id',
    // @ts-ignore
    component: () => import('../pages/community/course/index.vue'),
});

routes.push({
    path: '/community/teacher/:id',
    // @ts-ignore
    component: () => import('../pages/community/teacher/index.vue'),
});
console.log(routes);

export const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});
