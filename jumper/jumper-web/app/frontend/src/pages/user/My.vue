<template>
    <div class="ui basic segment">
        <div class="ui grid">
            <div class="ten wide column">
                <div class="ui large breadcrumb">
                    <br>
                    <a class="active section"> Me </a>
                    <i class="right angle inverted icon divider"></i>
                </div>
            </div>
        </div>
        <div class="ui divider"></div>


        <div class="ui four column grid">
            <!--个人账号信息-->
            <div class="column">
                <div class="ui raised segment" id="myInfo">
                    <h3><i class="large orange smile icon"></i>ID &nbsp; Card</h3>
                    <div v-if="my_info.uid">
                        <table class="ui very basic table">
                            <thead>
                            </thead>
                            <tbody>
                                <tr><td>uid :</td> <td>{{ my_info.uid }}</td></tr>
                                <tr><td>姓名 :</td> <td>{{ my_info.name }}</td></tr>
                                <tr><td>用户名 :</td> <td>{{ my_info.login_name }}</td></tr>
                                <tr><td>角色 :</td> <td>{{ my_info.role }}</td></tr>
                                <tr><td>mobile :</td>
                                    <td><div v-if="!show.edit">{{ my_info.mobile }}</div>
                                        <div class="ui input" v-else><input type="tel" v-model="my_info.mobile"></div>
                                    </td>
                                </tr>
                                <tr><td>email :</td>
                                    <td><div v-if="!show.edit">{{ my_info.email }}</div>
                                        <div class="ui fluid input" v-else><input type="email" v-model="my_info.email"></div>
                                    </td>
                                </tr>
                                <tr><td>区域 :</td>
                                    <td><div v-if="my_info.source=='DP'">上海</div>
                                        <div v-else>北京</div>
                                    </td>
                                </tr>
                                <tr><td>部门 :<span style="font-size: 8px; color: grey">(30字内)</span></td>
                                    <td><div v-if="!show.edit">{{ my_info.organization }}</div>
                                        <div class="ui fluid input" v-else><input type="text" v-model="my_info.organization">
                                            <div class="ui small blue icon button" style="font-size:8px" data-tooltip="（例）'集团/广告平台/联盟广告业务部/网盟技术组'－－－－填'网盟技术组' 即可" data-position="bottom center" data-inverted=""><i class="big help icon"></i></div>
                                        </div>
                                    </td>
                                </tr>
                                <tr><td>登录时间 :</td> <td>{{ my_info.login_time }}</td></tr>
                                <tr><td>注册时间 :</td> <td>{{ my_info.register_time }}</td></tr>
                                <tr><td>密码修改时间 :</td> <td>{{ my_info.password_mtime }}</td></tr>
                            </tbody>
                        </table>
                        <div class="right floated author" style="text-align: right" v-if="!show.edit">
                            <button class="ui small basic icon button" @click="show.edit=true"><i class="orange large edit icon"></i></button>
                        </div>
                        <div class="right floated author" style="text-align: right" v-if="show.edit">
                            <button class="ui orange button" @click="updateMe()">Save</button>
                            <button class="ui button" @click="show.edit=false, getMyInfo('')">Cancel</button>
                        </div>
                    </div>
                    <h3 style="text-align: center; font-weight:200; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif" v-else>
                        <br><br><br><br><i class="orange frown icon"></i>您还没有jumper跳板机账号哦～
                        <!--<p>请戳<i class="pointing blue right icon"></i>-->
                        <!--<router-link :to="{ path: '/workflow'}" style="color: darkorange;">账号申请</router-link></p>-->
                    </h3>
                </div>
            </div>
            <div class="column" id="Divider">
                <div class="ui large vertical divider"><i class="grey circle notched icon"></i></div>
            </div>

            <div class="column" >
                <div class="ui raised segment" id="SudoList">
                <!--Sudo信息-->
                    <!--<div class="ui left ribbon label">-->
                    <h3><i class="orange linux icon"></i>Sudo &nbsp;&nbsp;List &nbsp;&nbsp;</h3>
                    <!--</div>-->

                    <div class="ui divider"></div>
                    <h4>
                        <a @click="show.inherit=!show.inherit">
                            <i class="plus icon" v-if="!show.inherit"></i>
                            <i class="minus icon" v-else></i>
                        </a>直接授权
                    </h4>
                    <div class="ui basic segment" v-if="show.inherit">
                        <table class="ui small padded table" style="border: none"
                               v-if="my_info.uid && JSON.stringify(user_sudo_list) != '[]'">
                            <thead>
                            <th>应用/主机<i class="sort icon"></i></th>
                            <th>有效期</th>
                            </thead>
                            <tbody>
                                <tr style="line-height:15px" v-for="record in user_sudo_list">
                                    <td style="font-weight: bold">{{ record.label_key }}</td>
                                    <td>
                                        {{ record.life_cycle }}
                                        <div class="ui gray label" v-if="Date.parse(record.life_cycle) < Date.parse(new Date())">已失效</div>
                                        <div class="ui blue label" v-else-if="!record.life_cycle">永久有效</div>
                                        <div class="ui green label" v-else>有效</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <h4 style="text-align: center; font-weight:300; font-family:'Open Sans', sans-serif" v-else>（暂无有效记录~）</h4>
                    </div>

                    <!--<div class="ui divider"></div>-->
                    <div><h4>
                        <a @click="show.un_inherit=!show.un_inherit">
                            <i class="plus icon" v-if="!show.un_inherit"></i>
                            <i class="minus icon" v-else></i>
                        </a>继承的授权
                    </h4></div>
                    <div class="ui basic segment" v-if="show.un_inherit">
                        <table class="ui small padded table" style="border: none"
                               v-if="my_info.uid && JSON.stringify(group_sudo_list) != '[]'">
                            <thead>
                            <th>应用/主机<i class="sort icon"></i></th>
                            <th>所继承的组</th>
                            <th>有效期</th>
                            </thead>
                            <tbody>
                                <tr style="line-height:15px" v-for="record in group_sudo_list">
                                    <td style="font-weight: bold">{{ record.label_key }}</td>
                                    <td>{{ record.role_name }}</td>
                                    <td>
                                        {{ record.life_cycle }}
                                        <div class="ui gray label" v-if="Date.parse(record.life_cycle) < Date.parse(new Date())">已失效</div>
                                        <div class="ui blue label" v-else-if="!record.life_cycle">永久有效</div>
                                        <div class="ui green label" v-else>有效</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <h4 style="text-align: center; font-weight:300; font-family:'Open Sans', sans-serif" v-else>（暂无有效记录~）</h4>
                    </div>
                <!--ssh登录权限列表-->
                    <!--<div class="ui divider"></div>--><br>
                    <h3><i class="orange paw icon"></i> SSH &nbsp;&nbsp;List &nbsp;&nbsp;<span style="font-size: small; color: grey;">(仅指北京机器)</span></h3>
                    <div class="ui divider"></div>
                                        <h4>
                        <a @click="show.ssh_inherit=!show.ssh_inherit">
                            <i class="plus icon" v-if="!show.ssh_inherit"></i>
                            <i class="minus icon" v-else></i>
                        </a>直接授权
                    </h4>
                    <div class="ui basic segment" v-if="show.ssh_inherit">
                        <table class="ui small padded table" style="border: none"
                               v-if="my_info.uid && JSON.stringify(user_auth_list) != '[]'">
                            <thead>
                            <th>节点类型</th>
                            <th>节点<i class="sort icon"></i></th>
                            <th>有效期</th>
                            </thead>
                            <tbody>
                                <tr style="line-height:15px" v-for="record in user_auth_list">
                                    <td>{{ record.label }}</td>
                                    <td style="font-weight: bold">{{ record.label_key }}</td>
                                    <td>
                                        {{ record.life_cycle }}
                                        <div class="ui gray label" v-if="Date.parse(record.life_cycle) < Date.parse(new Date())">已失效</div>
                                        <div class="ui blue label" v-else-if="!record.life_cycle">永久有效</div>
                                        <div class="ui green label" v-else>有效</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <h4 style="text-align: center; font-weight:300; font-family:'Open Sans', sans-serif" v-else>（暂无有效记录~）</h4>
                    </div>

                    <!--<div class="ui divider"></div>-->
                    <div><h4>
                        <a @click="show.un_ssh_inherit=!show.un_ssh_inherit">
                            <i class="plus icon" v-if="!show.un_ssh_inherit"></i>
                            <i class="minus icon" v-else></i>
                        </a>继承的授权
                    </h4></div>
                    <div class="ui basic segment" v-if="show.un_ssh_inherit">
                        <table class="ui small padded table" style="border: none"
                               v-if="my_info.uid && JSON.stringify(group_auth_list) != '[]'">
                            <thead>
                            <th>节点类型</th>
                            <th>节点<i class="sort icon"></i></th>
                            <th>有效期</th>
                            </thead>
                            <tbody>
                                <tr style="line-height:15px" v-for="record in group_auth_list">
                                    <td>{{ record.label }}</td>
                                    <td style="font-weight: bold">{{ record.label_key }}</td>
                                    <td>
                                        {{ record.life_cycle }}
                                        <div class="ui gray label" v-if="Date.parse(record.life_cycle) < Date.parse(new Date())">已失效</div>
                                        <div class="ui blue label" v-else-if="!record.life_cycle">永久有效</div>
                                        <div class="ui green label" v-else>有效</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <h4 style="text-align: center; font-weight:300; font-family:'Open Sans', sans-serif" v-else>（暂无有效记录~）</h4>
                    </div>
                </div>

                <!--<div class="ui raised segment" id="Operation">-->
                    <!--<div class="ui left ribbon label">-->
                        <!--<h3><i class="orange unhide icon"></i>To &nbsp; Do</h3>-->
                    <!--</div>-->
                    <!--<div style="text-align: center">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;敬请期待～-->
                        <!--<i class="arrow right icon"></i>-->
                        <!--<router-link :to="{ path: '/workflow'}" style="color: darkorange;">账号申请</router-link>-->
                    <!--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i class="arrow right icon"></i>-->
                        <!--<router-link :to="{ path: '/workflow'}" style="color: darkorange;">密码重置</router-link>-->
                    <!--&lt;!&ndash;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i class="arrow right icon"></i>&ndash;&gt;-->
                        <!--&lt;!&ndash;<router-link :to="{ path: '/workflow'}" style="color: darkorange;">sudo权限申请</router-link>&ndash;&gt;-->
                    <!--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-->
                        <!--<a class="item" href="http://wiki.sankuai.com/pages/viewpage.action?pageId=656843141" target="_blank">-->
                            <!--更多疑问<i class="help icon"></i></a>-->
                    <!--</div><br>-->
                <!--</div>-->
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
    export default{
        components: {
            'alert': Alert
        },
        data (){
            return{
                my_info : {},
                login_history: [],
                group_sudo_list : [],
                user_sudo_list: [],
                group_auth_list: [],
                user_auth_list: [],
                writableKeys: ['email', 'mobile', 'organization'],  // 可修改字段
                show: {
                    edit: false,
                    alert: false,
                    inherit: false,
                    un_inherit: false,
                    ssh_inherit: false,
                    un_ssh_inherit: false,
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
            getMyInfo(val) {
                // 获取登录用户账号信息
                let _self = this;
                _self.my_info = store.getters.getMyInfo;
                if (JSON.stringify(_self.my_info) == '{}') {
                    api.user_my.get().then(
                    function(response){
                        _self.my_info = response.data.result;
                        if (val) { _self.getInfo() }
                    });
                }
                else {
                    if (val) { _self.getInfo() }
                }
            },
            getInfo() {
                let _self = this;
                // 获取用户登录主机历史
//                api.get_login_history.get({'user_uid': _self.my_info.uid}).then(
//                    function(response){
//                        _self.login_history = response.data.result;
//                    }
//                );

                // 获取有sudo权限的机器
                var now = Date.parse(new Date());
                api.get_user_sudo.get({user_name: _self.my_info.login_name}).then(
                    function(response){
                        var result = response.data.result;
                        _self.group_sudo_list = result.inherit;
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
                    }
                );

                // 获取有ssh权限的机器
                api.get_user_auth.get({uid: _self.my_info.uid}).then(
                    function(response){
                        var result = response.data.result;
                        _self.group_auth_list = result.inherit;
                        result.inherit.forEach(function(dict){
                            if (!dict['life_cycle'] || Date.parse(dict['life_cycle']) > now){
                                _self.group_auth_list.push(dict)
                            }
                        });
                        result.un_inherit.forEach(function(dict){
                            if (!dict['life_cycle'] || Date.parse(dict['life_cycle']) > now){
                                _self.user_auth_list.push(dict)
                            }
                        });
                    }
                )
            },
            updateMe() {
                let _self = this;
                _self.show.loading = true;
                let Key = '';
                let post_data = {};
                if (_self.my_info['organization'].length > 30) {
                        _self.show.alert_type = 'warning';
                        _self.show.alert = true;
                        _self.show.message = '部门字段最长为30个字！请您重新输入...'
                    }
                else {
                    for ( Key in _self.writableKeys)
                    {
                        post_data[_self.writableKeys[Key]] = _self.my_info[_self.writableKeys[Key]];
                    }
                    api.web_user.update({id: _self.my_info['uid']}, post_data).then(
                        function(response){
                            _self.show.alert_type = (response.data.code == 200 ? 'info' : 'warning');
                            _self.show.alert = true;
                            _self.show.message = response.data.msg;
                            if(response.data.code == 200){
                                _self.my_info = response.data.result;
                                _self.show.edit = false;
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
                }
            }
        },
        mounted(){
            this.getMyInfo(true);
        }
}
</script>
<style>
    .ui.basic.segment {
        /*!*min-height: 700px;*!*/
        /*height: 20%;*/
        /*margin-bottom: 20%;*/
        /*padding-bottom: -20%;*/
    }
    #myInfo {
        /*position: fixed;*/
        /*margin-top: 8px;*/
        /*margin-right: 2%;*/
        width: 450px;
        min-height: 560px;
        border: 1px solid darkgray;
        /*background-color: #0e90d2;*/
        /*height: 605px;*/
        /*overflow-y: scroll;*/

    }
    #SudoList {
        /*position: fixed;*/
        /*margin-top: 8px;*/
        margin-left: 75px;
        width: 620px;
        min-height: 400px;
        height: 590px;
        overflow-y: scroll;
        border-top: 3px solid lightgray
        /*!*-webkit-transition: all 0.5s ease;*!*/
        /*!*-moz-transition: all 0.5s ease;*!*/
        /*!*-o-transition: all 0.5s ease;*!*/
        /*!*transition: all 0.5s ease;*!*/
    }
    #loginHistory {
        /*position: fixed;*/
        /*margin-top: 8px;*/
        margin-left: 22%;
        width: 310px;
        /*min-height: 400px;*/
        height: 600px;
        overflow-y: scroll;
        border-top: 3px solid lightgray
        /*!*-webkit-transition: all 0.5s ease;*!*/
        /*!*-moz-transition: all 0.5s ease;*!*/
        /*!*-o-transition: all 0.5s ease;*!*/
        /*!*transition: all 0.5s ease;*!*/
    }
    #Operation {
        /*position: fixed;*/
        /*margin-top: 420px;*/
        margin-left: 75px;
        width: 620px;
        min-height: 45px;
        border-top: 3px solid lightgray
        /*height: 20%;*/
        /*overflow-y: scroll;*/
        /*!*-webkit-transition: all 0.5s ease;*!*/
        /*!*-moz-transition: all 0.5s ease;*!*/
        /*!*-o-transition: all 0.5s ease;*!*/
        /*!*transition: all 0.5s ease;*!*/
    }
    #Divider {
        /*position: fixed;*/
        /*margin-top: 60px;*/
        margin-left: 200px;
        width: 10px;
        /*min-height: 40px;*/
        height: 620px;
        /*!*-webkit-transition: all 0.5s ease;*!*/
        /*!*-moz-transition: all 0.5s ease;*!*/
        /*!*-o-transition: all 0.5s ease;*!*/
        /*!*transition: all 0.5s ease;*!*/
    }
    /*.description {*/
        /*min-height:10px;*/
        /*height: 90%;*/
    /*}*/
</style>