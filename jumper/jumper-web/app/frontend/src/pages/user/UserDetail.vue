<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="eight wide column">
                    <div class="ui large breadcrumb">
                        <router-link class="section" :to="{path: '/user'}">Users</router-link>
                        <i class="right angle icon divider"></i>
                        <div class="ui very basic green button"
                             @click="resetPassword()">重置密码
                        </div>
                        <div class="ui very basic green button"
                             @click="unlockUser()">账号解锁
                        </div>
                        <!--<test></test>-->
                        <!--<div class="ui right floated menu">-->
                        <!--<div class="ui right floated search">-->
                        <!--<div class="ui icon input">-->
                        <!--<input class="prompt" type="text" placeholder="输入域账号查询用户">-->
                        <!--<i class="search icon"></i>-->
                        <!--</div>-->
                        <!--<div class="results"></div>-->
                        <!--</div>-->
                        <!--</div>-->

                    </div>
                </div>
                <div class="eight wide right aligned column">
                    <div class="ui very basic green button" v-if="admin_role.indexOf(my_info.role) != -1"
                         @click="disableUser()">禁用用户
                    </div>
                    <div class="ui very basic red button" v-if="admin_role.indexOf(my_info.role) != -1"
                         @click="deleteUser()">删除用户
                    </div>
                </div>
            </div>
        </div>
        <div class="ui grid">
            <div class="ui row">
                <div class="eight wide column">
                    <div class="ui form " id="Form">
                        <div class="ui segment">
                            <a class="ui large green ribbon label">个人信息</a>
                            <button class="ui very small red button" v-if="user_info.enable === 0">已离职</button>
                            <div class="ui right floated main menu">
                                <a class="github popup icon item" data-content="View project on GitHub"
                                   title="校准账号信息"
                                   v-on:click="syncUser()">
                                    <i class="alternate refresh icon"></i>
                                </a>
                            </div>
                            <table class="ui very basic table">
                                <thead>
                                </thead>
                                <tbody>
                                <tr>
                                    <td>账号 :</td>
                                    <td>{{ user_info.login_name }}</td>
                                </tr>
                                <tr>
                                    <td>中文名 :</td>
                                    <td>{{ user_info.name }}</td>
                                </tr>
                                <tr>
                                    <td>是否锁定 :</td>
                                    <td>
                                        <div v-if="user_info.lock_times >= 6">
                                            <i class="red lock large icon"></i>
                                            <span style="font-size: 10px; color: grey;"> (30分钟内密码连续输入错误超过6次)</span>
                                        </div>
                                        <div v-else>
                                            <i class="green unlock large icon"></i>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td>角色 :</td>
                                    <td>{{ user_info.role }}</td>
                                </tr>
                                <tr>
                                    <td>区域 :</td>
                                    <td>
                                        <div v-if="user_info.source=='DP'">上海</div>
                                        <div v-else>北京</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td>mobile :</td>
                                    <td>
                                        <div v-if="!show.edit">{{ user_info.mobile }}</div>
                                        <div class="ui input" v-else><input type="tel" v-model="user_info.mobile">
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td>email :</td>
                                    <td>
                                        <div v-if="!show.edit">{{ user_info.email }}</div>
                                        <div class="ui fluid input" v-else><input type="email"
                                                                                  v-model="user_info.email"></div>
                                    </td>
                                </tr>

                                <tr>
                                    <td>uid :</td>
                                    <td>{{ user_info.uid }}</td>
                                </tr>
                                <tr>
                                    <td>shell :</td>
                                    <td>
                                        {{ user_info.shell }}
                                    </td>
                                </tr>
                                <tr>
                                    <td>家目录 :</td>
                                    <td>
                                        {{ user_info.home_dir }}
                                    </td>
                                </tr>
                                <tr>
                                    <td>所属部门 :</td>
                                    <td>
                                        <div v-if="!show.edit">{{ user_info.organization }}</div>
                                        <div class="ui fluid input" v-else><input type="text"
                                                                                  v-model="user_info.organization">
                                            <div class="ui small blue icon button" style="font-size:8px"
                                                 data-tooltip="（例）'集团/广告平台/联盟广告业务部/网盟技术组'－－－－填'网盟技术组' 即可"
                                                 data-position="bottom center" data-inverted=""><i
                                                    class="big help icon"></i></div>
                                        </div>
                                    </td>
                                </tr>

                                <tr>
                                    <td>账号注册时间 :</td>
                                    <td>{{ user_info.register_time }}</td>
                                </tr>
                                <tr>
                                    <td>最近登录时间 :</td>
                                    <td>{{ user_info.login_time }}</td>
                                </tr>
                                <tr>
                                    <td>密码修改时间 :</td>
                                    <td>{{ user_info.password_mtime }}</td>
                                </tr>
                                </tbody>
                            </table>
                            <div class="right floated author" style="text-align: right" v-if="show.edit">
                                <button class="ui orange button" @click="updateMe()">Save</button>
                                <button class="ui button" @click="show.edit=false, getMyInfo('')">Cancel</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="eight wide column">
                    <div class="ui grid">
                        <div class="ui row">
                            <div class="column">
                                <div class="ui raised segment">
                                    <!--<div class="ui right floated menu">-->
                                    <!--<div class="ui right floated search">-->
                                    <!--<div class="ui icon input">-->
                                    <!--<input class="prompt" type="text" placeholder="搜索组加入">-->
                                    <!--<i class="search icon"></i>-->
                                    <!--</div>-->
                                    <!--<div class="results"></div>-->
                                    <!--</div>-->
                                    <!--</div>-->
                                    <div class="ui primary blue ribbon label">用户所在组</div>

                                    <table class="ui green table">
                                        <thead>
                                        <tr>
                                            <th>组id</th>
                                            <th>组名</th>
                                            <th>组类型</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        <tr v-for="group in user_relate.group">
                                            <td>{{ group.gid }}</td>
                                            <td>{{ group.group_name }}</td>
                                            <td>{{ group.group_type }}</td>
                                        </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="ui row">
                            <div class="column">
                                <div class="ui raised segment">
                                    <a class="ui blue ribbon label">登录授权</a>
                                    <table class="ui green table">
                                        <thead>
                                        <tr>
                                            <th>机器所属</th>
                                            <th>授权类型</th>
                                            <th>授权节点</th>
                                            <th>有效期</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        <tr v-for="auth in user_relate.auth">
                                            <td>{{ auth.location }}</td>
                                            <td>{{ auth.label }}</td>
                                            <td>{{ auth.label_key }}</td>
                                            <td>{{ auth.expire }}</td>
                                        </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="ui row">
                            <div class="column">
                                <div class="ui raised segment">
                                    <a class="ui blue ribbon label">sudo授权</a>
                                    <table class="ui green table">
                                        <thead>
                                        <tr>
                                            <th>机器所属</th>
                                            <th>授权类型</th>
                                            <th>授权节点</th>
                                            <th>有效期</th>
                                            <th>sudo配置</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        <tr v-for="sudo in user_relate.sudo">
                                            <td>{{ sudo.location }}</td>
                                            <td>{{ sudo.label }}</td>
                                            <td>{{ sudo.label_key }}</td>
                                            <td>{{ sudo.expire }}</td>
                                            <td>{{ sudo.content }}</td>
                                        </tr>
                                        </tbody>

                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
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
    import datepicker from 'vue-date'
    import Alert from '../../components/lib/Alert.vue'
    import SearchUser from './SearchUser.vue'
    import Test from '../../components/test.vue'

    export default {
        components: {
            datepicker,
            'test': Test,

            'alert': Alert,
            'search-user': SearchUser
        },
        data() {
            return {
                open: false,
                options: [],
                value: '',
                type: 'app',

                my_info: {},
                user_info: {},
                user_relate: {},
                admin_role: ['op', 'sa', 'sre'],
                show: {
                    del: false,
                    alert: false,
                    message: 'e',
                    alert_type: 'warning',
                    loading: false
                }
            }
        },
        methods: {
            disableUser() {
                let self = this;
                api.updateUser.update({id: self.user_info.uid}, {enable: 0}).then((response) => {
                        // lambda success callback
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            self.getUser();
                        }
                        else {
                            self.show.loading = false;
                        }
                    }, (response) => {
                        // lambda error callback
                        self.show.loading = false;
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                )
            },
            deleteUser() {
                let self = this
                api.delUser.delete({}, {user_list: [self.user_info.uid]}).then((response) => {
                        // lambda success callback
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            self.user_info = response.data.result;
                        }
                        else {
                            self.show.loading = false;
                        }
                    }, (response) => {
                        // lambda error callback
                        self.show.loading = false;
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                )
            },
            syncUser() {
                let self = this;
                api.syncUser.update({user_name: self.user_info.login_name}).then((response) => {
                        // lambda success callback
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            self.getUser()
                        }
                        else {
                            self.show.loading = false;
                        }
                    }, (response) => {
                        // lambda error callback
                        self.show.loading = false;
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                );
            },
            unlockUser() {
                let self = this;
                api.unlockUser.update({user_name: self.user_info.login_name}).then((response) => {
                        // lambda success callback
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            self.getUser()
                        }
                        else {
                            self.show.loading = false;
                        }
                    }, (response) => {
                        // lambda error callback
                        self.show.loading = false;
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                );
            },
            resetPassword() {
                let self = this;
                api.resetPassword.save({user_name: self.user_info.login_name}).then((response) => {
                        // lambda success callback
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            self.getUser()
                        }
                        else {
                            self.show.loading = false;
                        }
                    }, (response) => {
                        // lambda error callback
                        self.show.loading = false;
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                );
            },
            userRelate() {
                let self = this;
                api.userRelate.get({uid: self.user_info.uid}).then((response) => {
                        if (response.data.code === 200) {
                            self.user_relate = response.data.result
                        }
                    }, (response) => {
                    }
                )
            },
            getShow(val) {
                this.show.alert = val;
            },
            getMyInfo() {
                // 获取登录用户账号信息
                let self = this;
                self.my_info = store.getters.getMyInfo;
                if (JSON.stringify(self.my_info) === '{}') {
                    api.user_my.get().then(
                        function (response) {
                            self.my_info = response.data.result;
                        });
                }
            },
            getUser() {
                let self = this;
                if (self.$route.params.user_name === "myself") {
                    if (JSON.stringify(self.my_info) === '{}') {
                        api.user_my.get().then(
                            function (response) {
                                self.user_info = response.data.result;
                                self.userRelate()
                            });
                    } else {
                        self.user_info = self.my_info;
                        self.userRelate()
                    }
                } else {
                    api.getUser.get({login_name: self.$route.params.user_name}).then((response) => {
                            self.user_info = response.data.result.objects[0];
                            self.userRelate()
                        }, (response) => {
                        }
                    )
                }
            },
        },
        watch: {
            $route() {
                this.getUser();
//                this.userRelate();
            }
        },
        mounted() {
            this.getMyInfo();
            this.getUser();
//            this.userRelate();
        },
    }
</script>
