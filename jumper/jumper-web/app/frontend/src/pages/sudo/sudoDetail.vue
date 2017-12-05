<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ui row">
                <div class="fourteen wide column">
                    <div class="ui large breadcrumb">
                        <router-link class="section" :to="{path: '/sudo'}">Sudo Records</router-link>
                        <i class="right angle icon divider"></i>
                        <div class="active section">Id: {{ id }}</div>
                        <i class="right angle icon divider"></i>
                        <div  class="ui very basic grey button" @click="show.del=true">删除此条权限</div>
                    </div>
                </div>
            </div>
            <div  class="ui grid" v-if="show.del">
                <div class="ui row">
                    <div class="six wide column"></div>
                    <div class="nine wide column"><h3><i class="red warning sign icon"></i>确定删除此条记录？id: {{ id }}</h3></div>
                </div>
                <div class="ui row">
                    <div class="seven wide column"></div>
                    <div class="four wide column">
                        <div  class="ui very basic blue button" @click="show.del=false, delSudo()">确认</div>
                    </div>
                    <div class="four wide column">
                        <div  class="ui very basic grey button" @click="show.del=false">取消</div>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="!show.del">
            <br/>
            <div class="ui grid"><div class="row"></div></div>
            <div class="ui form " id="Form">
                <div class="ui raised segment">
                    <div class="ui teal ribbon label"><h4>基本信息</h4></div>
                    <p></p><p></p>
                    <div class="seven fields">
                        <div class="inline field">
                            <label>id:</label><span>{{ sudo_info.id }}</span></div>
                    </div>
                    <div class="required four fields">
                        <div class="inline field">
                            <label><span>对象类型</span></label><input type="text" v-model="sudo_info.role"></div>
                         <div class="inline field">
                            <label>节点类型</label><input type="text" v-model="sudo_info.label" placeholder="Null"></div>
                    </div>
                    <div class="required four fields">
                        <div class="inline field">
                            <label>对 象</label><div class="ui fluid input"><input type="text" v-model="sudo_info.role_name" placeholder="Null"></div></div>
                        <div class="inline field">
                            <label>节 点</label><div class="ui fluid input"><input type="text" v-model="sudo_info.label_key" placeholder="Null"></div></div>
                    </div>
                    <div class="required four fields">
                        <div class="inline field">
                            <label>commands</label><div class="ui fluid input"><input type="text" v-model="sudo_info.commands" placeholder="Null"></div></div>
                        <div class="inline field">
                            <label>hosts</label><div class="ui fluid input"><input type="text" v-model="sudo_info.hosts"></div></div>
                        <div class="inline field">
                            <label>password_option</label><div class="ui fluid input"><input type="text" v-model="sudo_info.password_option"></div></div>
                        <div class="inline field">
                            <label>users</label><div class="ui fluid input"><input type="text" v-model="sudo_info.users" placeholder="Null"></div></div>
                    </div>
                    <div class="inline field"><label></label></div>
                    <div class="inline field">
                        <label>有效期:</label>
                        <div class="ui input">
                            <input type="datetime" v-model="life_cycle.time" placeholder="00:00:00">
                            <datepicker v-model="life_cycle.date" style="min-width: 140px"></datepicker>
                            <div style="font-size: smaller; color: red">
                                &nbsp;&nbsp;&nbsp;**均为空, 则表示永久有效**</div>
                        </div>
                        <!--<div v-else><div class="ui blue label">永久有效</div><a @click="">更改</a></div>-->
                    </div>
                    <div class="inline field"><label></label></div>
                    <div class="five fields">
                        <div class="inline field"><label></label></div>
                        <div class="inline field"><label></label></div>
                        <div class="inline field">
                            <div class="ui large light orange  button" @click="updateSudo()" v-if="admin_role.indexOf(my_info.role) != -1">提交</div>
                            <div class="ui large light grey button" v-else>提交</div>
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
    import datepicker from 'vue-date'
    import store from '../../vuex/store'
    import Alert from '../../components/lib/Alert.vue'
    export default {
        components: {
            datepicker,
            'alert': Alert
        },
        data (){
            return{
                id: '',
                my_info: {},
                sudo_info: {},
                admin_role: ['op', 'sa', 'sre'],
                life_cycle: {
                    'date': '',
                    'time': ''
                },
                // 可修改字段
                writableKeys: ['role', 'role_name', 'label', 'label_key', 'hosts',
                               'users', 'password_option', 'commands', 'life_cycle'],
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
            getShow(val) {
                this.show.alert = val;
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
            getSudo () {
                let _self = this;
                _self.id = _self.$route.params.id;
                api.sudo.get({id: _self.id}).then(
                    function (response) {
                        _self.sudo_info = response.data.result.objects[0];
                        if (_self.sudo_info.life_cycle) {
                            _self.life_cycle.date = _self.sudo_info.life_cycle.split(' ')[0];
                            _self.life_cycle.time = _self.sudo_info.life_cycle.split(' ')[1];
                        }
                    },
                    function (response) {}
                )
            },
            updateSudo() {
                let _self = this;
                _self.show.loading = true;
                let post_data = {};
                let Key = '';
                if (_self.life_cycle.time == '' && _self.life_cycle.date != '') {
                    _self.life_cycle.time = new Date().toTimeString().split(' ')[0]
                }
                _self.sudo_info.life_cycle = _self.life_cycle.date + ' ' + _self.life_cycle.time;
                for ( Key in _self.writableKeys)
                {
                    post_data[_self.writableKeys[Key]] = _self.sudo_info[_self.writableKeys[Key]];
                }
                api.sudo_admin.update({id: _self.id}, post_data).then(
                    function (response) {
                        _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                        _self.show.alert = true;
                        _self.show.message = response.data.msg;
                        if (response.data.code == 200) {
                            _self.sudo_info = response.data.result;
                            if (_self.sudo_info.life_cycle) {
                                _self.life_cycle.date = _self.sudo_info.life_cycle.split(' ')[0];
                                _self.life_cycle.time = _self.sudo_info.life_cycle.split(' ')[1];
                            }
                            else {
                                _self.life_cycle = {'date': '', 'time':''}
                            }
                            _self.show.loading = false;
                        }
                        else {
                            _self.show.loading = false;
                        }

                    },
                    function (response) {
                        _self.show.loading = false;
                        _self.show.alert_type = 'warning';
                        _self.show.alert = true;
                        _self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                        // error callback
                    }
                );
            },
            delSudo() {
                let _self = this;
                api.sudo_admin.delete({id: _self.id}).then(
                    function (response) {
                        if (response.data.code == 200) {
                            _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                            _self.show.alert = true;
                            _self.show.message = response.data.msg;
                            setTimeout(function(){_self.show.alert = false; _self.$router.push({ path: '/sudo'})}, 1000);
                        }
                        else {
                            _self.show.loading = false;
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
            },
        },
        watch: {
            $route() {
                this.getSudo();
            }
        },
        mounted(){
            this.getSudo();
            this.getMyInfo();
        },
    }
</script>

<style>
    #Form {

    }
</style>