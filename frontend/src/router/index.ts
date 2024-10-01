import { createRouter, createWebHistory } from "vue-router";

const routes = Object.entries(import.meta.glob('../pages/**/*.vue')).map(([path, component]) => {
    const routePath = path.replace("/pages", "").replace("/index", "").slice(2, -4);
    return {
        path: routePath,
        component: component
    };
});

routes.push({
    path: '/cdetail/:id',
    component: () => import('../pages/cdetail/index.vue'),
});

console.log(routes);

export const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});
