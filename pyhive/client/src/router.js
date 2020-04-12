import Vue from 'vue'
import Router from 'vue-router'
import Layout from './layout/Index.vue'
import store from './store'

Vue.use(Router);

const router = new Router({
	routes: [
		{
			path: '/login',
			name: 'login',
			component: () => import('./views/login/Login.vue'),
		},
		{
			path: '/',
			redirect: '/home',
			name: 'layout',
			component: Layout,
			children: [
				{
					path: '/home',
					name: 'home',
					component: () => import('./views/home/Index.vue')
				},
				{
					path: '/client',
					name: 'clientIndex',
					component: () => import('./views/client/Index.vue')
				},
				{
					path: '/client/create',
					name: 'clientCreate',
					component: () => import('./views/client/Create.vue')
				},
				{
					path: '/client/:id/edit',
					name: 'clientEdit',
					component: () => import('./views/client/Edit.vue')
				},
				{
					path: '/client/:id/schedule',
					name: 'clientSchedule',
					component: () => import('./views/client/Schedule.vue')
				},
				{
					path: '/project',
					name: 'projectIndex',
					component: () => import('./views/project/Index.vue')
				},
				{
					path: '/project/:name/edit',
					name: 'projectEdit',
					component: () => import('./views/project/Edit.vue')
				},
				{
					path: '/spider/:id/monitor',
					name: 'SpiderMonitor',
					component: () => import('./views/spider/Monitor.vue')
				}
			]
		},
	],
	scrollBehavior(to, from, savedPosition) {
		if (savedPosition) {
			return savedPosition
		} else {
			return {x: 0, y: 0}
		}
	}
});

const whiteList = ['/login'];

router.beforeEach((to, from, next) => {
	let token = store.getters.token;
	if (token) {
		if (to.path === '/login') {
			// if has login before, redirect to index page
			next({path: '/'})
		}
		else {
			next()
		}
	} else {
		if (whiteList.indexOf(to.path) !== -1) {
			next()
		} else {
			next({path: `/login`})
		}
	}
});

// Clear scheduled tasks
router.afterEach(() => {
	router.app.$store.commit('clearIntervals');
	router.app.$store.commit('clearTimeout');
});

export default router