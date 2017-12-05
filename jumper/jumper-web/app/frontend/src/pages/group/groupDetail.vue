<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="fourteen wide column">
                    <div class="ui large breadcrumb">
                        <router-link class="section" :to="{path: '/group'}">Groups</router-link>
                        <i class="right angle icon divider"></i>
                        <div class="active section">{{ group_name }}</div>
                        <i class="right angle icon divider"></i>
                        <div v-if="admin_role.indexOf(my_info.role) != -1" class="ui very basic green button"
                             @click="show.del=true,show.add_member=false,show.del_member=false">删除分组
                        </div>
                    </div>
                </div>
            </div>

            <!--删除分组提示-->
            <div class="ui grid" v-if="show.del && !show.add_member">
                <div class="ui row">
                    <div class="six wide column"></div>
                    <div class="nine wide column"><h3><i class="red warning sign icon"></i>确定删除分组 {{ group_name }} ?
                    </h3></div>
                </div>
                <div class="ui row">
                    <div class="seven wide column"></div>
                    <div class="four wide column">
                        <div class="ui very basic blue button" @click="show.del=false, delGroup()">确认</div>
                    </div>
                    <div class="four wide column">
                        <div class="ui very basic grey button" @click="show.del=false">取消</div>
                    </div>
                </div>
            </div>
        </div>

        <!--选择要添加的组成员-->
        <div class="ui grid" v-if="show.add_member">
            <div class="ui row">
                <div class="ui header">
                    <div class="ui teal tag label">批量添加成员</div>
                </div>
            </div>
            <div class="ui row">
                <div class="ui input">
                    <select-user
                            :result="user_name"
                            :index="1"
                            @select-user="setUser">
                    </select-user>
                </div>
            </div>
            <div class="ui row" v-show="add_members.length !== 0">
                <a class="ui label" v-for="(user, index) in add_members"
                   style="margin-bottom: 5px">
                    <i class="user icon"></i>
                    {{ user.user_name }}
                    <i class="delete icon" @click="popUser(index)"></i>
                </a>
            </div>

            <div class="ui form row">
                <div class="six wide field">
                    <button class="ui blue button"
                            :class="{'loading': show.loading}"
                            @click="addMembers()">提交
                    </button>
                    <button class="ui button" @click="show.add_member=false, add_members=[]">取消
                    </button>
                </div>
            </div>
        </div>

        <!--批量删除成员-->
        <div class="ui basic segment" v-if="show.del_member">
            <div class="ui divider"></div>
            <div class="ui header">
                <div class="ui teal tag label">批量删除成员</div>
            </div>
            <div>
                <h5 class="ui sub header">已选择成员 {{ del_members.length }} 个:</h5>
                <a class="ui label" v-for="(user, index) in del_members" style="margin-bottom: 5px">
                    <i class="user icon"></i>
                    {{ user.name }}
                    <i class="delete icon" @click="del_members.splice(index, 1)"></i>
                </a>
            </div>
            <br>
            <div>
                <div class="ui form">
                    <div class="six wide field">
                        <button class="ui blue button"
                                :class="{'loading': show.loading}"
                                @click="delMembers()">提交
                        </button>
                        <button class="ui button" @click="show.del_member=false, del_members=[]">取消</button>
                    </div>
                </div>
            </div>
        </div>

        <!--成员列表-->
        <div v-if="!show.del">
            <br/>
            <div>
                <h4 class="ui horizontal divider header"><i class="green tag icon"></i> 所有成员 </h4>
                <table class="ui celled green table" style="text-align: center">
                    <thead>
                    <tr>
                        <th>用户名</th>
                        <th>中文名</th>
                        <th>所属部门</th>
                        <th>最近登录时间</th>
                        <th>账号状态</th>
                        <th v-if="admin_role.indexOf(my_info.role) != -1">
                            <a @click="show.add_member=!show.add_member"><i
                                    class="circular plus link icon"></i></a>
                            <a @click="show.del_member=!show.del_member, del_members=[]"><i
                                    class="circular minus link icon"></i></a>
                            <label class="ui mini label" @click="allSelected()" v-if="show.del_member"
                                   style="cursor: pointer">全选</label>
                        </th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="(user, index) in user_list" :class="{'negative': del_members.indexOf(user) != -1}"
                        @click="show.del_member && del_members.indexOf(user) == -1 ? del_members.push(user): del_members.splice(del_members.indexOf(user), 1) ">
                        <td>
                            <router-link :to="{ path: '/user/' + user.login_name}">{{ user.login_name }}</router-link>
                        </td>
                        <td>
                            {{ user.name }}
                        </td>
                        <td>
                            {{ user.organization }}
                        </td>
                        <td>
                            {{ user.login_time }}
                        </td>
                        <td>
                            <a class="ui green small label" v-if="user.enable === 1">正常</a>
                            <a class="ui red label" v-else="">禁用</a>
                        </td>
                        <!--<td><div class="ui mini icon basic button" style="text-decoration:underline">移除</div></td>-->
                        <td v-if="!show.del_member && admin_role.indexOf(my_info.role) != -1"></td>
                        <td v-if="show.del_member && del_members.indexOf(user) == -1 && admin_role.indexOf(my_info.role) != -1">
                            <a><i class="radio icon"></i></a></td>
                        <td v-if="show.del_member && del_members.indexOf(user) != -1 && admin_role.indexOf(my_info.role) != -1">
                            <a><i class="checkmark icon"></i></a></td>
                    </tr>
                    </tbody>
                </table>
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
    import Alert from '../../components/lib/Alert.vue'
    import SelectUser from '../../components/lib/SelectUser.vue'

    export default {
        components: {
            'alert': Alert,
            'select-user': SelectUser
        },
        data() {
            return {
                user_name: "",
                my_info: {},
                group_name: '',
                user_list: [],
                admin_role: ['op', 'sa', 'sre'],
                add_members: [],
                del_members: [],
                show: {
                    add_member: false,
                    del_member: false,
                    del: false,
                    all_member: false,
                    alert: false,
                    message: 'e',
                    alert_type: 'warning',
                    loading: false
                }
            }
        },
        methods: {
            popUser(index) {
                this.add_members.splice(index, 1);
            },
            getShow(val) {
                this.show.alert = val;
            },

            setUser(val, index, uid) {
                if (this.add_members.indexOf(val) !== -1) {
                    return
                }
                this.add_members.push({user_name: val, uid: uid});
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
            getGroup() {
                //获取组成员
                let self = this;
                api.member_detail.get({id: self.group_name}).then(
                    function (response) {
                        self.user_list = response.data.result;
                    },
                    function (response) {
                    }
                )
            },
            allSelected() {
                let self = this;
                self.show.all_member = !self.show.all_member;
                if (self.show.all_member) {
                    self.user_list.forEach(function (user) {
                        if (self.del_members.indexOf(user.name)) {
                            self.del_members.push(user.name)
                        }
                    });
                }
                else {
                    self.del_members = [];
                }
            },
            addMembers() {
                let self = this;
                let user_list = [];
                self.show.loading = true;
                self.add_members.forEach(function (dict) {
                    if (dict['user_name'] !== '') {
                        user_list.push(dict['user_name']);
                    }
                });
                if (self.add_members.length === 0) {
                    self.show.alert_type = 'warning';
                    self.show.alert = true;
                    self.show.message = '请选择至少一个用户～';
                    self.show.loading = false;
                }
                else {
                    api.group.update({'group_name': self.group_name, 'user_list': user_list}).then(
                        function (response) {
                            self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                            self.show.alert = true;
                            self.show.message = response.data.msg;
                            if (response.data.code === 200) {
                                self.show.add_member = false;
                                self.show.loading = false;
                                self.add_members = [];
                                self.getGroup()
                            }
                            else {
                                self.show.loading = false;
                            }
                        },
                        function (response) {
                            self.show.loading = false;
                            self.show.alert_type = 'warning';
                            self.show.alert = true;
                            self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                            // error callback
                        }
                    )
                }
            },
            delMembers() {
                let self = this;
                self.show.loading = true;
                let user_list = [];
                self.del_members.forEach(function (dict) {
                    if (dict['login_name'] !== '') {
                        user_list.push(dict['login_name']);
                    }
                });
                if (self.del_members.length === 0) {
                    self.show.alert_type = 'warning';
                    self.show.alert = true;
                    self.show.message = '请选择至少一个用户～';
                    self.show.loading = false;
                }
                else {
                    api.group.delete({}, {'group_name': self.group_name, 'user_list': user_list}).then(
                        function (response) {
                            self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                            self.show.alert = true;
                            self.show.message = response.data.msg;
                            if (response.data.code === 200) {
                                self.show.del_member = false;
                                self.show.loading = false;
                                self.del_members = [];
                                self.getGroup();
                            }
                            else {
                                self.show.loading = false;
                            }
                        },
                        function (response) {
                            self.show.loading = false;
                            self.show.alert_type = 'warning';
                            self.show.alert = true;
                            self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                            // error callback
                        }
                    );
                }
            },
            delGroup() {
                //删除分组
                let self = this;
                api.group.delete({}, {'group_name': self.group_name}).then(
                    function (response) {
                        if (response.data.code === 200) {
                            self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                            self.show.alert = true;
                            self.show.message = response.data.msg;
                            setTimeout(function () {
                                self.show.alert = false;
                                self.$router.push({path: '/group'})
                            }, 1000);
                        }
                        else {
                            self.show.loading = false;
                        }
                    },
                    function (response) {
                        self.show.loading = false;
                        self.show.alert_type = 'warning';
                        self.show.alert = true;
                        self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                    }
                )
            },
        },
        mounted() {
            this.group_name = this.$route.params.id;
            this.getGroup();
            this.getMyInfo();
        },
    }
</script>
