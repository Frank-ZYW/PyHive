import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersist from 'vuex-persist'
import {en, zh} from './langs/index'
import zhLocale from 'element-ui/lib/locale/lang/zh-CN'
import enLocale from 'element-ui/lib/locale/lang/en'
import locale from 'element-ui/lib/locale'

Vue.use(Vuex);

const vuexPersist = new VuexPersist({
  key: 'gerapy',
  storage: localStorage
});

export default new Vuex.Store({
  state: {
    lang: 'zh',
    i18n: {
      zh: zh,
      en: en
    },
    auth: {
      user: null,
      token: null
    },
    color: {
      primary: '#35CBAA',
      success: '#35CBAA',
      warning: '#F6B93D',
      danger: '#EF6372',
      error: '#EF6372',
      info: '#60BCFE'
    },
    timeout: null,
    intervals: [],
    dateFormat: 'yyyy-MM-dd HH:mm:ss',
    url: {
      user: {
        auth: 'api/user/auth'
      },
      home: {
        status: '/api/index/status'
      },
      project: {
        index: '/api/project/index/?keyword={keyword}',
        create: '/api/project/create',
        upload: '/api/project/upload',
        withdraw: '/api/project/{name}/withdraw',
        remove: '/api/project/{name}/remove',
        build: '/api/project/{name}/build',
        tree: '/api/project/{name}/tree',
        fileRead: '/api/project/file/read',
        fileUpdate: '/api/project/file/update',
        fileDelete: '/api/project/file/delete',
        fileRename: '/api/project/file/rename',
        fileCreate: '/api/project/file/create',
      },
      client: {
        index: '/api/client',
        show: '/api/client/{id}',
        status: '/api/client/{id}/status',
        update: '/api/client/{id}/update',
        remove: '/api/client/{id}/remove',
        create: '/api/client/create',
        listSpiders: '/api/client/{id}/spiders/?keyword={keyword}',
        projectDeploy: '/api/client/{id}/project/{name}/deploy'
      },
      spider: {
        status: '/api/spider/{id}/status',
        update: '/api/spider/{id}/update',
        start: '/api/spider/{id}/start',
        cancelJob: '/api/spider/{id}/cancel',
        listJobs: '/api/spider/{id}/jobs',
        getLog: '/api/spider/{id}/job/{job}/log',
        getMonitor: '/api/spider/{id}/monitor'
      },
      util: {
        render: '/api/render'
      }
    }
  },
  mutations: {
    setLang(state, lang) {
      state.lang = lang;
      if (lang === 'zh') {
        locale.use(zhLocale)
      }
      if (lang === 'en') {
        locale.use(enLocale)
      }
    },
    // auth
    setToken(state, token) {
      state.auth.token = token
    },
    clearToken(state) {
      state.auth.token = null
    },
    // user
    setUser(state, user) {
      state.auth.user = user
    },
    clearUser(state) {
      state.auth.user = null
    },
    // timeout
    setTimeout: (state, timeout) => {
      if (state.timeout) {
        clearTimeout(state.timeout)
      }
      state.timeout = timeout
    },
    clearTimeout: (state) => {
      clearTimeout(state.timeout)
    },
    addInterval: (state, interval) => {
      state.intervals.push(interval)
    },
    clearIntervals: (state) => {
      state.intervals.forEach(interval => {
        clearInterval(interval)
      });
      state.intervals = []
    },
  },
  getters: {
    $lang: state => {
      return state.i18n[state.lang]
    },
    token: state => {
      return state.auth.token
    },
    user: state => {
      return state.auth.user
    }
  },
  plugins: [vuexPersist.plugin]
})