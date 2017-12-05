import Vue from 'vue'
import Vuex from 'vuex'
import Router from 'vue-router'
import Resource from 'vue-resource'
import ECharts from 'vue-echarts/components/Echarts.vue'
import 'echarts/lib/chart/bar'
import 'echarts/lib/chart/pie'
import 'echarts/lib/chart/line'
import 'echarts/lib/component/tooltip'
Vue.component('chart', ECharts)
Vue.use(Vuex);
Vue.use(Router);
Vue.use(Resource);
global.api = require('./api.js');

//
import store from './vuex/store.js'

// menu 组件
import Index from './pages/Index.vue'
import User from './pages/user/User.vue'
import UserDetail from './pages/user/UserDetail.vue'
import Sudo from './pages/sudo/Sudo.vue'
import Help from './pages/help/Help.vue'
import Group from './pages/group/Group.vue'
import Advice from './pages/advice/Advice.vue'
import Danger from './pages/danger/Danger.vue'
import Record from './pages/record/Record.vue'
import History from './pages/history/History.vue'
import Dashboard from './pages/dashboard/Dashboard.vue'
import Permission from './pages/permission/Permission.vue'
// import test from './pages/test.vue'


import My from './pages/user/My.vue'
import WorkFlow from './pages/workflow/Workflow.vue'
import SudoDetail from './pages/sudo/sudoDetail.vue'
import SudoUserDetail from './pages/sudo/sudoUserDetail.vue'
import GroupDetail from './pages/group/groupDetail.vue'
import GroupAdd from './pages/group/groupAdd.vue'
import UserReplay from './pages/replay/UserReplay.vue'


// 按需加载: '/terminal'
const Terminal = resolve => require(['./pages/terminal/Layout.vue'], resolve);
const Video = resolve => require(['./pages/replay/Video.vue'], resolve);
// const File = resolve => require(['./pages/file/File.vue'], resolve);


// 路由配置
const routes = [
    // {
    //     path: '/test',
    //     component: test,
    // },
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/dashboard',
        component: Dashboard,
        meta: {
            active: 'dashboard'
        }
    },
    {
        path: '/user',
        component: User,
        meta: {
            active: 'user'
        }
    },
    {
        path: '/user/:user_name',
        component: UserDetail
    },
    {
        path: '/group/add',
        component: GroupAdd,
    },
    {
        path: '/group',
        component: Group,
        meta: {
            active: 'group'
        }
    },
    {
        path: '/group/:id',
        component: GroupDetail,
        meta: {
            active: 'GroupAdmin'
        }
    },
    {
        path: '/permission',
        component: Permission,
        meta: {
            active: 'permission'
        }
    },
    {
        path: '/sudo',
        component: Sudo,
        meta: {
            active: 'sudo'
        }
    },
    {
        path: '/terminal',
        component: Terminal,
        meta: {
            active: 'terminal',
            keepAlive: true     //开启缓存
        }
    },
    {
        path: '/danger',
        component: Danger,
        meta: {
            active: 'danger'
        }
    },
    {
        path: '/history',
        component: History,
        meta: {
            active: 'history'
        }
    },
    {
        path: '/record',
        component: Record,
        meta: {
            active: 'record'
        }
    },
    {
        path: '/help',
        component: Help,
        meta: {
            active: 'help'
        }
    },
    {
        path: '/advice',
        component: Advice,
        meta: {
            active: 'advice'
        }
    },
    {
        path: '/my',
        component: My,
        meta: {
            active: 'myInfo',
        }
    },

    {
        path: '/sudo/:id',
        component: SudoDetail,
        meta: {
            active: 'SudoAdmin'
        }
    },
    {
        path: '/sudo_user',
        component: SudoUserDetail,
        meta: {
            active: 'SudoAdmin'
        }
    },

    {
        path: '/user_replay',
        component: UserReplay,
        meta: {
            active: 'replay'
        }
    },

];

const router = new Router({
    routes // （缩写）相当于 routes: routes
});

// 入口
new Vue({
    store,
    router,
    render: h => h(Index)
}).$mount('#app');

