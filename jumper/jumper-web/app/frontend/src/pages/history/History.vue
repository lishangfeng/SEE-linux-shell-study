<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="ten wide column">
                    <div class="ui large breadcrumb">
                        <br>
                        <router-link class="section" :to="{path: '/user'}">Users</router-link>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
                <div class="right aligned six wide column">
                    <pagination :num=userList.num_results :current=userList.page :switchpage="switchPage"></pagination>
                </div>
            </div>
            <div class="ui row">
                <div class="four wide column">
                    <div class="ui labeled input">
                        <div class="ui green label">域账号 </div>
                        <input v-model="filter['@login_name']" icon="close" @click="dealFilter('@login_name')"
                               placeholder="">
                    </div>
                </div>
                <div class="four wide column">
                    <div class="ui labeled input">
                        <div class="ui green label">姓名 </div>
                        <input v-model="filter['@name']" icon="close" @click="dealFilter('@name')" placeholder="">
                    </div>
                </div>
                <div class="three wide column">
                    <myselect class="ui search dropdown"
                              :selected="filter['role']"
                              :options="options.role"
                              :title="'选择角色'"
                              @filter-change="roleChange">
                    </myselect>
                </div>
                <div class="one wide column">
                    <myselect class="ui search dropdown"
                              :selected="filter['source']"
                              :options="options.source"
                              :title="'选择区域'"
                              @filter-change="sourceChange">
                    </myselect>
                </div>
            </div>
        </div>
        <div class="ui divider"></div>
        <div>
            <table class="ui celled table" style="text-align: center">
                <thead>
                <tr>
                    <th> UID </th>
                    <th> 域账号 </th>
                    <th> 姓名 </th>
                    <th> 部门 </th>
                    <th> 注册时间 </th>
                    <th> 角色
                        <a @click="show.allRole=true" v-if="!show.allRole && admin_role.indexOf(my_info.role) != -1"><i
                                class="green zoom icon"></i></a>
                        <a @click="show.allRole=false" v-if="show.allRole && admin_role.indexOf(my_info.role) != -1"><i
                                class="green zoom out icon"></i></a>
                    </th>
                    <th> 地域 </th>
                    <th v-if="admin_role.indexOf(my_info.role) != -1"> 操作 </th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(info , index) in userList.objects">
                    <td>{{ info.uid }}</td>
                    <td>{{ info.login_name }}</td>
                    <td>{{ info.name }}</td>
                    <td>{{ info.organization }}</td>
                    <td>{{ info.register_time }}</td>
                    <td>
                        <div class="ui green label" v-if="!show.allRole">{{ info.role }}</div>
                        <div class="ui mini buttons" v-else>
                            <button class="ui button" v-bind:class="{'green': info.role == 'sa'}"
                                    v-on:click="updateUser(index, info.uid, {'role':'sa'})">sa
                            </button>
                            <button class="ui button" v-bind:class="{'green': info.role == 'op'}"
                                    v-on:click="updateUser(index, info.uid, {'role':'op'})">op
                            </button>
                            <button class="ui button" v-bind:class="{'green': info.role == 'sre'}"
                                    v-on:click="updateUser(index, info.uid, {'role':'sre'})">sre
                            </button>
                            <button class="ui button" v-bind:class="{'green': info.role == 'rd'}"
                                    v-on:click="updateUser(index, info.uid, {'role':'rd'})">rd
                            </button>
                            <button class="ui button" v-bind:class="{'green': info.role == 'qa'}"
                                    v-on:click="updateUser(index, info.uid, {'role':'qa'})">qa
                            </button>
                        </div>
                    </td>
                    <td>
                        <div class="ui green label" v-if="admin_role.indexOf(my_info.role) == -1">{{ info.source }}
                        </div>
                        <div class="ui mini buttons" v-else="">
                            <button class="ui button" v-bind:class="{'green': info.source == 'DP'}"
                                    v-on:click="updateUser(index, info.uid, {'source':'DP'})">上海
                            </button>
                            <button class="ui button" v-bind:class="{'green': info.source == 'MT'}"
                                    v-on:click="updateUser(index, info.uid, {'source':'MT'})">北京
                            </button>
                        </div>
                    </td>
                    <td v-if="admin_role.indexOf(my_info.role) != -1">
                        <router-link class="ui mini icon basic button" :to="{ path: 'user/'+info.login_name}"
                                     style="text-decoration:underline">详情
                        </router-link>

                    </td>
                </tr>
                </tbody>
            </table>
        </div>
        <alert
                :show="show.alert"
                :duration="3000"
                :header="show.header"
                :message="show.message"
                :type="show.alert_type"
                @get-show="getShow"
                dismissable>
        </alert>
    </div>
</template>

<script>
    import store from '../../vuex/store'
    import Alert from '../../components/lib/Alert.vue'
    import Select from '../../components/lib/Select.vue'
    import Pagination from '../../components/lib/Pagination.vue'
    export default{
        components: {
            Pagination,
            'alert': Alert,
            'myselect': Select
        },
        data (){
            return {
                userList: {},
                my_info: {},
                admin_role: ['op', 'sa', 'sre'],
                currentPage: 1,
                filter: {
                    '@login_name': '',
                    '@name': '',
                    'role': '',
                    'source': ''
                },
                loading: true,
                tag: true,
                selected: {
                    'info': false
                },
                options: {
                    role: [
                        {'label': 'sa', 'value': 'sa'},
                        {'label': 'op', 'value': 'op'},
                        {'label': 'sre', 'value': 'sre'},
                        {'label': 'qa', 'value': 'qa'},
                        {'label': 'rd', 'value': 'rd'}
                    ],
                    source: [
                        {'label': '上海', 'value': 'DP'},
                        {'label': '北京', 'value': 'MT'}
                    ]
                },
                show: {
                    allRole: false,
                    alert: false,
                    message: 'e',
                    alert_type: 'warning'
                }
            }
        },
        watch: {
            filter: {
                handler (val, oldv){
                    this.getUser();
                },
                deep: true
            },
            $route() {
                this.getUser(1);
            }
        },
        methods: {
            roleChange(val) {
                this.filter['role'] = val;
            },
            sourceChange(val) {
                this.filter['source'] = val;
            },
            getShow(val) {
                this.show.alert = val;
            },
            switchPage (page){
                this.currentPage = page;
                this.getUser(this.currentPage)
            },
            getMyInfo() {
                // 获取登录用户账号信息
                let _self = this;
                _self.my_info = store.getters.getMyInfo;
                if (JSON.stringify(_self.my_info) == '{}') {
                    api.user_my.get().then(
                        function (response) {
                            _self.my_info = response.data.result;
                        });
                }
            },
            getUser (page) {
                let _self = this;
                _self.loading = true;
                let d = {};
                d['page'] = page;
                Object.keys(this.filter).forEach(k => {
                    if (this.filter[k] != '') {
                        d[k] = this.filter[k];
                    }
                });
                api.user.get(d).then(
                    function (response) {
                        _self.userList = response.data.result;
                        _self.loading = false;
                    },
                    function (response) {
                    }
                )
            },
            dealFilter(key) {
                this.filter[key] = '';
            },
            updateUser(index, uid, data) {
                let _self = this;
                api.user_one.update({id: uid}, data).then(
                    function (response) {
                        _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                        _self.show.alert = true;
                        _self.show.message = response.data.msg;
                        if (response.data.code == 200) {
                            _self.$set(_self.userList.objects, index, response.data.result);
                        }
                        else {
                        }
                    },
                    function (response) {
                        _self.show.alert_type = 'warning';
                        _self.show.alert = true;
                        _self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                )
            }
        },
        mounted(){
            this.getUser(1);
            this.getMyInfo();
        }
    }
</script>
