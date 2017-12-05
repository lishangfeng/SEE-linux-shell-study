<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class = "ui row" >
                <div class="ten wide column">
                    <div class="ui large breadcrumb">
                        <br>
                        <router-link class="section" :to="{path: '/group'}">Groups</router-link>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
                <div class="right aligned six wide column">
                    <pagination :num=group_list.num_results :current=group_list.page :switchpage="switchPage"></pagination>
                </div>
            </div>
            <div class = "ui row">
                <div class="four wide column">
                    <div class="ui labeled input">
                        <div class="ui green label">分组名 </div>
                        <input v-model="filter['@group_name']" icon="close"  @click="dealFilter('@group_name')" placeholder="">
                    </div>
                </div>
                <div class="ten wide column"></div>
                <div class="two wide column" v-if="admin_role.indexOf(my_info.role) != -1">
                    <router-link class="ui very basic green button" :to="{ path: '/group/add'}">新增分组</router-link>
                </div>
            </div>
        </div>
        <div class="ui divider"></div>
        <div>
            <table class="ui celled table" style="text-align: center">
                <thead>
                    <tr>
                        <th> GID </th>
                        <th> 分组名 </th>
                        <th> 描述 </th>
                        <th v-if="admin_role.indexOf(my_info.role) != -1"> 操作 </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(info , index) in group_list.objects">
                        <td>{{ info.gid }}</td>
                        <td>
                            <router-link  :to="{ path: 'group/'+info.group_name}">{{ info.group_name }}</router-link>
                        </td>
                        <td>{{ info.desc }}</td>
                        <td v-if="admin_role.indexOf(my_info.role) != -1">
                            <router-link class="ui mini icon basic button" :to="{ path: 'group/'+info.group_name}" style="text-decoration:underline">详情</router-link>
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
    import Pagination from '../../components/lib/Pagination.vue'
    export default{
        components: {
            Pagination,
            'alert': Alert
        },
        data (){
            return{
                group_list: [],
                my_info: {},
                currentPage: 1,
                admin_role: ['op', 'sa', 'sre'],
                filter: {
                    '@group_name': ''
                },
                loading: true,
                tag: true,
                show: {
                    alert: false,
                    message: 'e',
                    alert_type: 'warning'
                }
            }
        },
        watch: {
            filter: {
                handler (val, oldv){
                    this.getGroup();
                },
                deep: true
            },
            $route() {
                this.getGroup(1);
            }
        },
        methods: {
            getShow(val) {
                this.show.alert = val;
            },
            switchPage (page){
                this.currentPage = page;
                this.getGroup(this.currentPage)
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
            getGroup (page) {
                let _self = this;
                _self.loading = true;
                let d = {};
                d['page'] = page;
                Object.keys(this.filter).forEach(k => {
                    if (this.filter[k]!='') {
                    d[k] = this.filter[k];
                    }
                });
                api.group.get(d).then(
                    function(response){
                        _self.group_list = response.data.result;
                        _self.loading = false;
                    },
                    function(response){
                    }
                )
            },
            dealFilter(key) {
                this.filter[key] = '';
            }
        },
        mounted(){
            this.getGroup(1);
            this.getMyInfo();
        }
    }
</script>
