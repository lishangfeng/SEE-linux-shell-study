<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row"></div>
            <div class="ui row">
                <div class="fourteen wide column">
                    <div class="ui large breadcrumb">
                        <router-link class="section" :to="{path: '/group'}">Groups</router-link>
                        <i class="right angle icon divider"></i>
                        <div class="active section">新增分组</div>
                        <i class="right angle icon divider"></i>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <br/>
            <div class="ui grid">
                <div class="row"></div>
            </div>
            <div class="ui grid">
                <div class="ui row">
                    <div class="three wide column"></div>
                    <div class="ten wide column">
                        <div class="ui tiny header">
                            组名
                        </div>
                        <div class="ui fluid input"><input type="text" v-model="group_info.group_name"
                                                           placeholder="输入合法的组名，如 stree.meituan.sre">
                        </div>

                        <div class="ui tiny header">
                            组描述信息
                        </div>
                        <div class="ui fluid input"><input type="text" v-model="group_info.desc"
                                                           placeholder="输入组的相关描述，如sre专用组">
                        </div>

                        <div class="ui tiny header">
                            添加组成员
                        </div>
                        <div class="ui tiny header">
                        </div>
                        <div class="ui input">
                            <select-user
                                    :result="user_name"
                                    :index="1"
                                    @select-user="setUser">
                            </select-user>
                        </div>
                        <button class="circular ui icon button">
                            <i class="icon trash" @click="emptySelect()"></i>
                        </button>
                        <div class="ui image large label" v-for="(user, index) in selected_user">
                            <i class="ui user icon"></i>
                            {{ user }}
                            <i class="delete icon" @click="popUser(index)"></i>
                        </div>
                        <div class="ui header"></div>
                        <div class="ui right floated buttons">
                            <button class="ui button" @click="goBack()">取消</button>
                            <div class="or"></div>
                            <button class="ui positive button" @click="commit()">提交</button>
                        </div>
                    </div>
                    <div class="three wide column"></div>
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
    import SelectUser from '../../components/lib/SelectUser.vue'


    export default {
        components: {
            datepicker,
            'alert': Alert,
            'select-user': SelectUser,
        },
        data() {
            return {
                user_name: "",
                selected_user: [],
                my_info: {},
                group_info: {'group_name': '', 'desc': ''},
                show: {
                    alert: false,
                    message: 'e',
                    alert_type: 'warning',
                    loading: false
                }
            }
        },
        methods: {
            goBack() {
                this.$router.push({path:'/group'})
            },
            setUser(val, index, uid) {
                if (this.selected_user.indexOf(val) !== -1) {
                    return
                }
                this.selected_user.push(val)
                console.log(this.selected_user)
            },
            emptySelect(){
              this.selected_user = []
            },
            popUser(index) {
                this.selected_user.splice(index, 1);
                console.log(this.selected_user)
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
            commit() {
                let self = this;
                self.show.loading = true;
                self.group_info.user_list = self.selected_user;
                api.group.save(self.group_info).then(
                    function (response) {
                        self.show.alert_type = (response.data.code === 200 ? 'info' : 'warning');
                        self.show.alert = true;
                        self.show.message = response.data.msg;
                        if (response.data.code === 200) {
                            setTimeout(function () {
                                self.show.alert = false;
                                self.$router.push({path: '/group'})
                            }, 1000);
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
        mounted() {
            this.getMyInfo();
        },
    }
</script>
