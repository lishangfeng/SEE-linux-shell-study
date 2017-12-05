<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="ten wide column">
                    <div class="ui large breadcrumb"><br>
                        <router-link class="section" :to="{path: '/replay'}">Videos</router-link>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
                <div class="right aligned six wide column">
                    <pagination :num=login_history.num_results :current=login_history.page :switchpage="switchPage"></pagination>
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
        <div class="ui divider"></div>
        <div>
            <table class="ui celled table" style="text-align: center">
                <thead>
                    <tr>
                        <th> 用户名 </th>
                        <th> 主机 </th>
                        <th> 端口 </th>
                        <th> 来源IP </th>
                        <th> 录像 </th>
                        <th> 登录时间 </th>
                        <th> 登出时间 </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(info , index) in login_history.objects">
                        <td>{{ info.user_name }}</td>
                        <td>{{ info.host_name }}</td>
                        <td>{{ info.remote_port }}</td>
                        <td>{{ info.remote_ip }}</td>
                        <td>
                            <router-link v-if="info.logout_time"
                                    :to="{ path: '/replay/' + info.id + '?user=' + info.user_name
                                            + '&host=' + info.host_name + '&uuid=' + info.login_uuid + '&channel_id=' + info.channel_id
                                            + '&start=' + Date.parse(info.login_time) + '&end=' + Date.parse(info.logout_time)}" target="_blank">
                                回放</router-link>
                            <router-link v-else
                                    :to="{ path: '/replay/' + info.id + '?user=' + info.user_name
                                            + '&host=' + info.host_name + '&uuid=' + info.login_uuid + '&channel_id=' + info.channel_id
                                            + '&start=' + Date.parse(info.login_time) + '&end=' + Date.parse(new Date())}" target="_blank">
                                回放</router-link>
                        </td>
                        <td>{{ info.login_time }}</td>
                        <td>{{ info.logout_time }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
    import store from '../../vuex/store'
    import SelectUser from '../../components/lib/SelectUser.vue'
    import Pagination from '../../components/lib/Pagination.vue'
    export default{
        components: {
            Pagination,
            'select-user': SelectUser
        },
        data (){
            return{
                user_name: '',
                uid: 1,
                my_info: {},
                currentPage: 1,
                admin_role: ['op', 'sa', 'sre'],
                login_history: {'page': 1, 'num_results': 1, 'objects':[]},
            }
        },
        methods: {
            getUser(val, index, uid) {
                this.uid = uid;
                this.getLoginHistory(1)
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
            switchPage (page){
                this.currentPage = page;
                this.getLoginHistory(this.currentPage)
            },
            getLoginHistory(page) {
                let _self = this;
                api.get_all_history.get({user_uid: _self.uid, page: page}).then(
                    function (response) {
                        _self.login_history = response.data.result
                    },
                    function(response){
                    }
                )
            },
        },
        mounted(){
            this.getMyInfo()
        }
    }
</script>
