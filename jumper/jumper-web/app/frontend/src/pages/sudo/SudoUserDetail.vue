<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="fourteen wide column">
                    <div class="ui large breadcrumb"><br>
                        <router-link class="section" :to="{path: '/sudo'}">Sudo Records</router-link>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
            </div>
            <div class = "ui row" ></div>
            <div class = "ui row" >
                <div class="ten wide column">
                    <h4><i class="blue idea icon"></i>输入用户名：
                        <div class="ui input">
                        <select-user
                                :result="user_name"
                                :index="1"
                                @select-user="getUser">
                        </select-user></div></h4>
                </div>


            </div>
        </div>
        <h4 class="ui horizontal divider header"><i class="orange tag icon"></i> 所有Sudo权限 </h4>
        <div><h4>
            <a @click="show.inherit=!show.inherit">
                <i class="plus icon" v-if="!show.inherit"></i>
                <i class="minus icon" v-else></i>
            </a>直接授权
        </h4></div>
        <div class="ui basic segment" v-if="show.inherit">
            <table class="ui padded table" style="border: none"
                   v-if="JSON.stringify(user_sudo_list) != '[]'">
                <thead>
                    <tr>
                        <th> ID </th>
                        <th> 对象类型 </th>
                        <th> 对象 </th>
                        <th> 节点类型 </th>
                        <th> 节点 </th>
                        <th> 有效期截止 </th>
                        <th v-if="admin_role.indexOf(my_info.role) != -1"> 详情 </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="info in user_sudo_list">
                        <td>{{ info.id }}</td>
                        <td>{{ info.role }}</td>
                        <td>
                            <router-link  :to="{ path: 'user/'+info.role_name}" target="_blank" v-if="['user', 'dp_user'].indexOf(info.role) != -1">{{ info.role_name }}</router-link>
                            <router-link  :to="{ path: 'group/'+info.role_name}" target="_blank" v-else-if="['group', 'dp_group'].indexOf(info.role) != -1">{{ info.role_name }}</router-link>
                            <div v-else>{{ info.role_name }}</div>
                        </td>
                        <td>{{ info.label }}</td>
                        <td>{{ info.label_key }}</td>
                        <td>
                            {{info.life_cycle}}
                            <div class="ui gray label" v-if="Date.parse(info.life_cycle) < Date.parse(new Date())">已失效</div>
                            <div class="ui blue label" v-else-if="!info.life_cycle">永久有效</div>
                            <div class="ui green label" v-else>有效</div>
                        </td>
                        <td v-if="admin_role.indexOf(my_info.role) != -1">
                            <router-link class="ui mini icon basic button" :to="{ path: '/sudo/'+info.id}" target="_blank" style="text-decoration:underline">详情</router-link>
                        </td>
                    </tr>
                </tbody>
            </table>
            <h4 style="text-align: center; font-weight:300; font-family:'Open Sans', sans-serif" v-else>（暂无有效记录~）</h4>
        </div>

        <br>
        <div><h4>
            <a @click="show.un_inherit=!show.un_inherit">
                <i class="plus icon" v-if="!show.un_inherit"></i>
                <i class="minus icon" v-else></i>
            </a>继承的授权
        </h4></div>
        <div class="ui basic segment" v-if="show.un_inherit">
            <table class="ui padded table" style="border: none"
                   v-if="JSON.stringify(group_sudo_list) != '[]'">
                <thead>
                    <tr>
                        <th> ID </th>
                        <th> 所继承的组 </th>
                        <th> 节点类型 </th>
                        <th> 节点 </th>
                        <th> 有效期截止 </th>
                        <th v-if="admin_role.indexOf(my_info.role) != -1"> 详情 </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="info in group_sudo_list">
                        <td>{{ info.id }}</td>
                        <td>
                            <router-link  :to="{ path: 'group/'+info.role_name}" target="_blank">{{ info.role_name }}</router-link>
                        </td>
                        <td>{{ info.label }}</td>
                        <td>{{ info.label_key }}</td>
                        <td>
                            {{info.life_cycle}}
                            <div class="ui gray label" v-if="Date.parse(info.life_cycle) < Date.parse(new Date())">已失效</div>
                            <div class="ui blue label" v-else-if="!info.life_cycle">永久有效</div>
                            <div class="ui green label" v-else>有效</div>
                        </td>
                        <td v-if="admin_role.indexOf(my_info.role) != -1">
                            <router-link class="ui mini icon basic button" :to="{ path: '/sudo/'+info.id}" target="_blank" style="text-decoration:underline">详情</router-link>
                        </td>
                    </tr>
                </tbody>
            </table>
            <h4 style="text-align: center; font-weight:300; font-family:'Open Sans', sans-serif" v-else>（暂无有效记录~）</h4>
        </div>
    </div>
</template>

<script>
    import store from '../../vuex/store'
    import SelectUser from '../../components/lib/SelectUser.vue'
    export default{
        components: {
            'select-user': SelectUser
        },
        data (){
            return{
                user_name: '',
                my_info: {},
                group_sudo_list : [],
                user_sudo_list: [],
                admin_role: ['op', 'sa', 'sre'],
                loading: true,
                tag: true,
                show: {
                    inherit: false,
                    un_inherit: false,
                    alert: false,
                    message: 'e',
                    alert_type: 'warning'
                }
            }
        },
        methods: {
            getUser(val, index, uid) {
                this.user_name = val;
                this.show.inherit = true;
                this.show.un_inherit = true;
                this.getSudo()
            },
            getMyInfo() {
                // 获取登录用户账号信息
                let _self = this;
                _self.my_info = store.getters.getMyInfo;
                if (JSON.stringify(_self.my_info) == '{}') {
                    api.user_my.get().then(
                    function(response){
                        _self.my_info = response.data.result;
                    });
                }
            },
            getSudo(){
                let _self = this;
                _self.loading = true;
                // 获取有sudo权限的机器
                if (_self.user_name !== '') {
                    api.get_user_sudo.get({user_name: _self.user_name}).then(
                        function(response){
                            let result = response.data.result;
                            let now = Date.parse(new Date());
                            result.inherit.forEach(function(dict){
                                if (!dict['life_cycle'] || Date.parse(dict['life_cycle']) > now){
                                    _self.group_sudo_list.push(dict)
                                }
                            });
                            result.un_inherit.forEach(function(dict){
                                if (!dict['life_cycle'] || Date.parse(dict['life_cycle']) > now){
                                    _self.user_sudo_list.push(dict)
                                }
                            });
                    })
                }
            }
        },
        mounted(){
            this.getMyInfo()
        }
    }
</script>
