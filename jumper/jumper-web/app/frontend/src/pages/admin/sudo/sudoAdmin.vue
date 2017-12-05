<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class = "ui row" >
                <div class="ten wide column">
                    <div class="ui large breadcrumb">
                        <br>
                        <router-link class="section" :to="{path: '/sudo'}">Sudo Records</router-link>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
                <div class="right aligned six wide column">
                    <pagination :num=sudo_list.num_results :current=sudo_list.page :switchpage="switchPage"></pagination>
                </div>
            </div>
            <div class = "ui row">
                <div class="four wide column">
                    <div class="ui labeled input">
                        <div class="ui orange label">对象 </div>
                        <input v-model="filter['@role_name']" icon="close" @click="dealFilter('@role_name')" placeholder="用户名 或 组名">
                    </div>
                </div>
                <div class="four wide column">
                    <div class="ui labeled input">
                        <div class="ui orange label">节点 </div>
                        <input v-model="filter['@label_key']" icon="close" @click="dealFilter('@label_key')" placeholder="label">
                    </div>
                </div>
                <div class="three wide column">
                    <myselect class="ui search dropdown"
                              :selected="filter['label']"
                              :options="options.label"
                              :title="'节点类型'"
                                @filter-change="labelChange">
                    </myselect>
                </div>

                <div class="right aligned five wide column">
                    <router-link  :to="{ path: '/sudo_user'}" style="color: darkorange; font-size: small; text-decoration:underline">点击查看某用户的所有继承权限</router-link>
                </div>
            </div>

        </div>
        <div class="ui divider"></div>
        <div>
            <table class="ui celled table" style="text-align: center">
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
                    <tr v-for="(info , index) in sudo_list.objects">
                        <td>{{ info.id }}</td>
                        <td>{{ info.role }}</td>
                        <td>
                            <router-link  :to="{ path: 'user/'+info.role_name}" v-if="['user', 'dp_user'].indexOf(info.role) != -1">{{ info.role_name }}</router-link>
                            <router-link  :to="{ path: 'group/'+info.role_name}" v-else-if="['group', 'dp_group'].indexOf(info.role) != -1">{{ info.role_name }}</router-link>
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
                            <router-link class="ui mini icon basic button" :to="{ path: '/sudo/'+info.id}" style="text-decoration:underline">详情</router-link>
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
    import store from '../../../vuex/store'
    import Alert from '../../../components/lib/Alert.vue'
    import Select from '../../../components/lib/Select.vue'
    import Pagination from '../../../components/lib/Pagination.vue'
    export default{
        components: {
            Pagination,
            'alert': Alert,
            'myselect': Select
        },
        data (){
            return{
                sudo_list: {'page': 1, 'num_results': 1, 'objects':[]},
                my_info: {},
                admin_role: ['op', 'sa', 'sre'],
                currentPage: 1,
                filter: {
                    '@role_name': '',
                    '@label_key': '',
                    'label': '',
                },
                options: {
                    label: [
                        {'label' : 'owt', 'value':'owt'},
                        {'label' : 'pdl', 'value':'pdl'},
                        {'label' : 'srv', 'value':'srv'},
                        {'label' : 'cluster', 'value':'cluster'},
                        {'label' : 'dp_host', 'value':'dp_host'},
                        {'label' : 'dp_project', 'value':'dp_project'}
                    ]
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
                    this.getSudo();
                },
                deep: true
            },
            $route() {
                this.getSudo(1);
            }
        },
        methods: {
            getShow(val) {
                this.show.alert = val;
            },
            labelChange(val) {
                this.filter['label'] = val;
            },
            switchPage (page){
                this.currentPage = page;
                this.getSudo(this.currentPage)
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
            getSudo (page) {
                let _self = this;
                _self.loading = true;
                let d = {};
                d['page'] = page;
                Object.keys(_self.filter).forEach(k => {
                    if (_self.filter[k]!='') {
                        d[k] = _self.filter[k];
                    }
                });
                api.sudo.get(d).then(
                    function(response){
                        _self.sudo_list = response.data.result;
                        _self.loading = false;
                    },
                    function(response){
                    }
                );

            },
            dealFilter(key) {
                this.filter[key] = '';
            }
        },
        mounted(){
            this.getSudo(1);
            this.getMyInfo();
        }
    }
</script>
