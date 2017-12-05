<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="ten wide column">
                    <router-link :to="'/user/myself'">
                        <!--<i class="user icon"></i>-->
                        <a class="ui orange tag label">我的信息</a>
                    </router-link>
                </div>
                <div class="right aligned six wide column">
                    <pagination :num=userList.num_results :current=userList.page :switchpage="switchPage"></pagination>
                </div>
            </div>
            <div class="ui row">
                <div class="three wide column">
                    <div class="ui labeled input">
                        <div class="ui green label">域账号</div>
                        <input v-model="filter['@login_name']" icon="close" @click="dealFilter('@login_name')"
                               placeholder="zhangsan">
                    </div>
                </div>
                <div class="three wide column">
                    <div class="ui labeled input">
                        <div class="ui green label">中文名</div>
                        <input v-model="filter['@name']" icon="close" @click="dealFilter('@name')" placeholder="张三">
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
                <div class="three wide column">
                    <myselect class="ui search dropdown"
                              :selected="filter['source']"
                              :options="options.source"
                              :title="'选择区域'"
                              @filter-change="sourceChange">
                    </myselect>
                </div>
                <div class="four wide right aligned column" v-if="admin_role.indexOf(my_info.role) != -1">
                    <div class="ui green basic grey button"
                         @click="show.del=true">增加用户
                    </div>
                    <div class="ui red basic button"
                         @click="delUser">删除用户
                    </div>
                </div>
            </div>
        </div>
        <div class="ui divider"></div>
        <div>
            <table class="ui celled table" style="text-align: center">
                <thead>
                <tr>
                    <th> 域账号 </th>
                    <th> 中文名</th>
                    <th> 部门 </th>
                    <th> 注册时间 </th>
                    <th> 最近登录 </th>
                    <th> 角色
                        <a @click="show.allRole=true" v-if="!show.allRole && admin_role.indexOf(my_info.role) != -1">
                            <i class="green zoom icon"></i></a>
                        <a @click="show.allRole=false" v-if="show.allRole && admin_role.indexOf(my_info.role) != -1">
                            <i class="green zoom out icon"></i></a>
                    </th>
                    <th> 归属地域
                        <a @click="show.allSource=true"
                           v-if="!show.allSource && admin_role.indexOf(my_info.role) != -1">
                            <i class="green zoom icon"></i></a>
                        <a @click="show.allSource=false"
                           v-if="show.allSource && admin_role.indexOf(my_info.role) != -1">
                            <i class="green zoom out icon"></i></a>
                    </th>
                    <th>账号状态</th>
                    <th>
                        <button class="ui mini button" v-model='checkall' v-if="checkall" v-on:click='checkedAll'>取消
                        </button>
                        <button class="ui mini button" v-model='checkall' v-else="" v-on:click='checkedAll'>全选</button>
                    </th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(user, index) in userList.objects">
                    <td>
                        <router-link :to="{path: 'user/'+user.login_name}">{{ user.login_name }}</router-link>
                    </td>
                    <td>{{ user.name }}</td>
                    <td>{{ user.organization }}</td>
                    <td>{{ user.register_time }}</td>
                    <td>{{ user.login_time }}</td>
                    <td>
                        <div class="ui green label" v-if="!show.allRole">{{ user.role }}</div>
                        <div class="ui mini buttons" v-else>
                            <button class="ui button" v-for="role in options.role"
                                    v-bind:class="{'green': user.role == role.value}"
                                    v-on:click="user.role == role.value || updateUser(index, user.uid, {'role': role.value})">
                                {{ role.value }}
                            </button>
                        </div>
                    </td>
                    <td>
                        <div class="ui green label" v-if="!show.allSource">{{ mapSource(user.source) }}</div>
                        <div class="ui mini buttons" v-else>
                            <button class="ui mini button" v-for="source in options.source"
                                    v-bind:class="{'green': user.source == source.value}"
                                    v-on:click="user.source == source.value || updateUser(index, user.uid, {'source': source.value})">
                                {{ source.label }}
                            </button>
                        </div>
                    </td>
                    <td>
                        <div class="ui toggle checkbox">
                            <input class="green" type="checkbox"
                                   v-on:click="updateUser(index, user.uid, {'enable': userEnable(user.enable)})"
                                   v-model="user.enable" name="public">
                            <label></label>
                        </div>
                    </td>
                    <td>
                        <div class="ui checked checkbox">
                            <input type="checkbox" v-model="checkbox" :value="user.uid">
                            <label></label>
                        </div>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
        <!--<Test></Test>-->
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
    import Test from '../../components/test.vue'
    import Pagination from '../../components/lib/Pagination.vue'

    export default {
        components: {
            Pagination,
            'alert': Alert,
//            'Test': Test,
            'myselect': Select
        },
        data() {
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
                checkbox: [],
                checkall: false,
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
                    ],
                    sourceMap: {
                        'DP': '上海',
                        'MT': '北京'
                    }

                },
                show: {
                    allRole: false,
                    allSource: false,
                    alert: false,
                    message: 'e',
                    alert_type: 'warning'
                }
            }
        },
        watch: {
            filter: {
                handler(val, oldv) {
                    this.getUser();
                },
                deep: true
            },
            $route() {
                this.getUser(1);
            },
            checkbox: {
                handler: function (val, oldVal) {
                    if (this.checkbox.length === this.userList.objects.length) {
                        this.checkall = true;
                    } else {
                        this.checkall = false;
                    }
                },
                deep: true
            }
        },
        methods: {
            checkedAll() {
                var _this = this;
                if (this.checkall) {//实现反选
                    _this.checkbox = [];
                } else {//实现全选
                    _this.checkbox = [];
                    _this.userList.objects.forEach(function (item) {
                        _this.checkbox.push(item.uid);
                    });
                }
            },
            userEnable(enable) {
                if (enable === true) {
                    return 1
                }
                if (enable === false) {
                    return 0
                }
            },
            mapSource(source) {
                if (source === 'DP') {
                    return '上海'
                }
                else {
                    return '北京'
                }
            },
            roleChange(val) {
                this.filter['role'] = val;
            },
            sourceChange(val) {
                this.filter['source'] = val;
            },
            getShow(val) {
                this.show.alert = val;
            },
            switchPage(page) {
                this.currentPage = page;
                this.getUser(this.currentPage)
            },
            getMyInfo() {
                // 获取登录用户账号信息
                let self = this;
                self.my_info = store.getters.getMyInfo;
                if (JSON.stringify(self.my_info) == '{}') {
                    api.user_my.get().then(
                        function (response) {
                            self.my_info = response.data.result;
                        });
                }
            },
            getUser(page) {
                let self = this;
                self.loading = true;
                let d = {};
                d['page'] = page;
                Object.keys(this.filter).forEach(k => {
                    if (this.filter[k] != '') {
                        d[k] = this.filter[k];
                    }
                });
                api.getUser.get(d).then(
                    function (response) {
                        self.userList = response.data.result;
                        self.loading = false;
                    },
                    function (response) {
                    }
                )
            },
            dealFilter(key) {
                this.filter[key] = '';
            },
            delUser() {
                let self = this;
                if (this.checkbox.length === 0) {
                    self.show.alert_type = ('warning');
                    self.show.alert = true;
                    self.show.message = '您未选择需要删除的用户！';
                }
                else {
//                    var user_list =
                    api.delUser.delete({}, {user_list : self.checkbox}).then(
                        function (response) {
                            self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                            self.show.alert = true;
                            self.show.message = response.data.msg;
                            if (response.data.code === 200) {
                                self.getUser(1)
                            }
                            else {
                            }
                        },
                        function (response) {
                            self.show.alert_type = 'warning';
                            self.show.alert = true;
                            self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                        }
                    )
                }
            },
            updateUser(index, uid, data) {
                let self = this;
                api.updateUser.update({id: uid}, data).then(
                    function (response) {
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            self.$set(self.userList.objects, index, response.data.result);
                        }
                        else {
                        }
                    },
                    function (response) {
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                )
            }
        },
        mounted() {
            this.getUser(1);
            this.getMyInfo();
        }
    }
</script>
<style>
    myselect {
        padding: 0px;
    }
</style>