<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ten wide column">
                <div class="ui large breadcrumb">
                    <br>
                    <a class="active section"> Account Operation </a>
                    <i class="right angle inverted icon divider"></i>
                </div>
            </div>
        </div>
        <div class="ui divider"></div><br>
        <!--<div class="ui raised segment">-->
            <!--<div class="ui teal tag label">选择操作</div>-->
            <!--<div class="ui teal tag label">填写数据</div>-->
        <!--<div class="ui mini basic button"-->
             <!--:class="{'black': operation_type == 'user_add'}" @click="operation_type = 'user_add'">账号申请 </div>-->
        <!--<div class="ui mini basic button"-->
             <!--:class="{'black': operation_type == 'reset'}" @click="operation_type = 'reset'">密码重置 </div>-->
        <!--<div class="ui mini basic button"-->
             <!--:class="{'black': operation_type == 'sudo_add'}" @click="operation_type = 'sudo_add'">sudo权限申请 </div>-->

        <div class="ui secondary pointing orange menu">
            <a class="item"  v-bind:class="{'active': operation_type == 'user_add'}" @click="operation_type = 'user_add'">
                账号申请 </a>
            <a class="item" v-bind:class="{'active': operation_type == 'reset'}" @click="operation_type = 'reset'">
                密码重置 </a>
            <!--<a class="item" v-bind:class="{'active': operation_type == 'sudo_add'}" @click="operation_type = 'sudo_add'">-->
                <!--sudo权限申请 </a>-->
        </div>
        <div class="ui bottom attached segment">
            <!--账号申请-->
            <div class="segment" v-if="operation_type=='user_add'">
                <p></p>
                <div class="ui labeled input" v-if="my_info.uid && my_info.role== admin_role">
                    <div class="ui label">域账号</div>
                    <input type="text" placeholder="" v-model="user_name">
                </div>
                <h4 v-else>&nbsp;&nbsp;&nbsp;申请账号：<div class="ui input"><input type="text" readonly="" v-model="user_name"></div></h4>
                <br>
                <div v-if="my_info.uid && my_info.role != admin_role">
                    <br>
                    <h3 style="text-indent: 45px; font-style: oblique; font-weight: 300; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif">
                        您已经有 jumper 跳板机账号咯～<i class="orange large hand peace icon" style="text-indent: 0"></i></h3>
                    <p style="text-indent: 70px; font-size: 10px; color: darkgrey">(只有管理员才能申请非本人账号)</p>
                </div>
                <div v-else>
                    <br>
                    <h4><i class="middle red alarm  icon"></i>注意：</h4>
                    <p style="text-indent: 45px">1）账号申请成功后，<span style="font-weight: 800">'运维服务中心'&nbsp;</span>公众号会立马发给你&nbsp;<span style="font-weight: 800">'初始密码'</span>！请注意查看大象消息～</p>
                    <p style="text-indent: 45px">2）用户信息下发最长需要&nbsp;&nbsp;<span style="font-weight: 800">20分钟&nbsp;</span>, 期间如无法登录目标机器, 请耐心等待～</p>
                    <br>
                    <div class="ui large light blue button" @click="AddUser()">一键申请</div>
                </div>
            </div>

            <!--密码重置-->
            <div class="segment" v-if="operation_type=='reset'">
                <p></p>
                <div v-if="!my_info.uid">
                    <br><br><br>
                    <h3 style="text-indent: 45px; font-weight:200; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif">
                        <i class="orange frown icon" style="text-indent: 0"></i>您还没有 jumper 跳板机账号？<p></p>
                        <p style="text-indent: 80px; font-size: 15px">快戳左上方 "账号申请"<i class="blue pointing up icon" style="text-indent: 0"></i></p>
                    </h3>
                </div>
                <div v-else>
                    <div class="ui labeled input" v-if="my_info.uid && my_info.role == admin_role">
                        <div class="ui label">域账号 </div>
                        <input type="text" placeholder="" v-model="user_name">
                    </div>
                    <h4 v-else>&nbsp;&nbsp;&nbsp;密码重置账号：
                        <div class="ui input"><input type="text" readonly="" v-model="user_name"></div>
                    </h4>
                    <br><br>
                    <h4><i class="middle red alarm  icon"></i>注意：</h4>
                    <p style="text-indent: 45px">密码重置成功后,&nbsp;&nbsp;
                        <span style="font-weight: 800">'运维服务中心'&nbsp;</span>公众号会发给你重置后的新密码哦！请注意查看大象消息～
                    </p>
                    <br>
                    <div class="ui  light red  button" @click="Reset()">密码重置</div>
                </div>
            </div>

            <!--sudo权限申请-->
            <!--<div class="segment" v-if="operation_type=='sudo_add'">-->
                <!--<p></p>-->
                <!--<div v-if="!my_info.uid">-->
                    <!--<br><br><br>-->
                    <!--<h3 style="text-indent: 45px; font-weight:200; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif">-->
                        <!--<i class="orange frown icon" style="text-indent: 0"></i>您还没有 jumper 跳板机账号？<p></p>-->
                        <!--<p style="text-indent: 80px; font-size: 15px">快戳左上方 "账号申请"<i class="blue pointing up icon" style="text-indent: 0"></i></p>-->
                    <!--</h3>-->
                <!--</div>-->
                <!--<div v-else>-->
                    <!--<h4>&nbsp;&nbsp;&nbsp;申请账号：<div class="ui input"><input type="text" readonly="" v-model="user_name"></div></h4>-->
                    <!--<h4><i class="middle red alarm  icon"></i>注意：</h4>-->
                    <!--<p style="text-indent: 45px; font-weight: 800"> sudo权限有效期为24小时 ！ </p>-->
                    <!--<p style="text-indent: 45px; font-size: 10px"> (权限申请成功后，退出跳板机重新登陆即可生效)</p>-->
                    <!--<p></p>-->
                    <!--<h4><i class="blue idea icon"></i>输入应用名搜主机：</h4>-->
                    <!--<select-host class="ui search dropdown"-->
                              <!--:result="host_list"-->
                              <!--@select-hosts="getHost">-->
                    <!--</select-host>-->
                    <!--<p></p>-->
                    <!--<div class="ui large light blue button" @click="AddSudo()">申请Sudo</div>-->
                <!--</div>-->
            <!--</div>-->
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
    import SelectHost from '../../components/lib/SelectHost.vue'
    export default{
        components: {
            'alert': Alert,
            'select-host': SelectHost
        },
        data (){
            return{
                user_info : {},
                my_info : {},
                admin_role: 'op',
                user_name : '',
                selected_project: '',
                host_list: [],
                all_selected: false,
                sudo_err_msg : '',
                operation_type: 'reset',
                show: {
                    alert: false,
                    message: 'e',
                    alert_type: 'warning',
                    loading: false
                }
            }
        },
        methods: {
            getHost(val, len) {
                let _self = this;
                _self.selected_project = val.app_name;
                _self.host_list = val.host_list;
                _self.all_selected = (_self.host_list.length == len);
            },
            getShow(val) {
                this.show.alert = val;
            },
            getMyInfo() {
                // 获取登录用户账号信息
                let _self = this;
                _self.my_info = store.getters.getMyInfo;
                _self.user_name = _self.my_info.login_name;
                if (JSON.stringify(_self.my_info) == '{}') {
                    api.user_my.get().then(
                    function(response){
                        _self.my_info = response.data.result;
                        _self.user_name = _self.my_info.login_name;
                    });
                }
            },
            Reset() {
                let _self = this;
                api.reset.save({user_name: _self.user_name}).then(
                    function(response){
                        _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                        _self.show.alert = true;
                        _self.show.message = response.data.msg;
                        if(response.data.code == 200){
                        }
                        else {
                        }
                    },
                    function(response){
                        _self.show.loading = false;
                        _self.show.alert_type = 'warning';
                        _self.show.alert = true;
                        _self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                        // error callback
                    }
                )
            },
            AddUser() {
                let _self = this;
                api.user.save({user_name: _self.user_name}).then(
                    function(response){
                        _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                        _self.show.alert = true;
                        _self.show.message = response.data.msg;
                        if(response.data.code == 200){
                            _self.my_info = response.data.result.objects[0];
                        }
                        else {
                        }
                    },
                    function(response){
                        _self.show.loading = false;
                        _self.show.alert_type = 'warning';
                        _self.show.alert = true;
                        _self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                        // error callback
                    }
                )
            },
            AddSudo() {
                let _self = this;
                let sudo_type =  '';
                let post_data = [];
                if (!_self.all_selected) {
                    sudo_type = 'host';
                    post_data = _self.host_list;
                }
                else {
                    sudo_type = 'project';
                    post_data.push(_self.selected_project);
                }
                if (post_data.length == 0) {
                    _self.show.alert_type = 'warning';
                    _self.show.alert = true;
                    _self.show.message = '请选择至少一台主机～';
                }
                else {
                    api.sh_add_sudo.save({user_name: _self.user_info.login_name, sudo_type: sudo_type, data: post_data
                    }).then(
                        function (response) {
                            _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                            _self.show.alert = true;
                            if (response.data.code == 200) {
                                if (response.data.result.failed_hosts.length != 0){
                                    _self.sudo_err_msg = '申请失败的机器：'+ response.data.result.failed_hosts
                                        + ";失败原因： "+ response.data.msg
                                }
                                _self.show.message = response.data.msg + _self.sudo_err_msg;
                                _self.operation_type = 'reset'
                            }
                            else {
                                _self.show.message = response.data.msg;
                            }
                        },
                        function (response) {
                            _self.show.loading = false;
                            _self.show.alert_type = 'warning';
                            _self.show.alert = true;
                            _self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                            // error callback
                        }
                    )
                }
            }
        },
        mounted(){
            this.getMyInfo();
        },
        watch: {
//            user_name: this.user_info.login_name
            $route() {
                this.operation_type = 'reset'
            }
        }
}
</script>
<style>
    .ui.bottom.attached.segment {
        min-height: 350px;
    }

</style>