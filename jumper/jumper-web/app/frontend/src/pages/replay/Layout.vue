<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row"></div>
            <div class="ui row">
                <div class="ten wide column">
                    <div class="ui large breadcrumb">
                        <router-link class="section" :to="{path: '/replay'}">Videos</router-link>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
                <div class="right aligned six wide column">
                    <pagination :num=login_history.num_results :current=login_history.page :switchpage="switchPage"></pagination>
                </div>
            </div>
            <div class="ui row" v-if="admin_role.indexOf(my_info.role) != -1">
                <div class="right aligned fifteen wide column">
                    <router-link  :to="{ path: '/user_replay'}" style="color: darkorange; font-size: small; text-decoration:underline">点击查看某用户的所有历史记录</router-link>
                </div>
            </div>
        </div><br>
        <div>
            <table class="ui celled table" style="text-align: center">
                <thead>
                    <tr>
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
                        <td>{{ info.host_name }}</td>
                        <td>{{ info.remote_port }}</td>
                        <td>{{ info.remote_ip }}</td>
                        <td>
                            <router-link v-if="info.logout_time"
                                    :to="{ path: '/replay/' + info.id + '?user=' + _self.my_info.login_name
                                            + '&host=' + info.host_name + '&uuid=' + info.login_uuid + '&channel_id=' + info.channel_id
                                            + '&start=' + Date.parse(info.login_time) + '&end=' + Date.parse(info.logout_time)}" target="_blank">
                                回放</router-link>
                            <router-link v-else
                                    :to="{ path: '/replay/' + info.id + '?user=' + _self.my_info.login_name
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
    import Pagination from '../../components/lib/Pagination.vue'

    export default{
        components: {
            Pagination,
        },
        data(){
            return {
                currentPage: 1,
                loading: true,
                my_info: {},
                login_history: {'page': 1, 'num_results': 1, 'objects':[]},
                admin_role: ['op', 'sa', 'sre']
            }
        },
        methods: {
            switchPage (page){
                this.currentPage = page;
                this.getLoginHistory(this.currentPage)
            },
            getMyInfo() {
                // 获取登录用户账号信息
                let _self = this;
                _self.my_info = store.getters.getMyInfo;
                if (JSON.stringify(_self.my_info) == '{}') {
                    api.user_my.get().then(
                    function(response){
                        _self.my_info = response.data.result;
                        _self.getLoginHistory(1)
                    });
                }
                else {_self.getLoginHistory(1)}
            },
            getLoginHistory(page) {
                let _self = this;
                _self.loading = true;
                api.get_all_history.get({user_uid: _self.my_info.uid, page: page}).then(
                    function (response) {
                        _self.login_history = response.data.result;
                        _self.loading = false;
                    },
                    function(response){
                    }
                )
            }
        },
        mounted(){
            this.getMyInfo();
        },
        watch: {
            $route() {
                this.getLoginHistory(1);
            }
        }

    }
</script>

<style>
    #hostList .ui.list>.item a {
        color: #a7b1c2 !important;
        /*color: #EEEEEE !important;*/
    }

    #hostList .ui.list > .item >div .selected {
        color: #19aa8d !important;
    }

    #hostList .ui.list>.item a:hover {
        color: #CD5C5C !important;
        /*background: #EEEEEE;*/
    }

    #hostList .ui.list>.item.selected {
        /*color: #1C5792 !important;*/
        /*color: #000000 !important;*/
        /*background: #EEEEEE;*/
        color: #19aa8d !important;
    }
</style>
