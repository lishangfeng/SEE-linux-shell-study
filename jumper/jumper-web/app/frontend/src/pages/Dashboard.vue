<template>
    <div class="ui basic segment">
        <!--<div class="ui grid">-->
            <!--&lt;!&ndash;<div class="ten wide column">&ndash;&gt;-->
                <!--&lt;!&ndash;<br>&ndash;&gt;-->
                <!--&lt;!&ndash;<div class="ui large breadcrumb">&ndash;&gt;-->
                    <!--&lt;!&ndash;<a class="active section"> Home </a>&ndash;&gt;-->
                    <!--&lt;!&ndash;<i class="right angle icon divider"></i>&ndash;&gt;-->
                    <!--&lt;!&ndash;&lt;!&ndash;<span class="divider">/</span>&ndash;&gt;&ndash;&gt;-->
                <!--&lt;!&ndash;</div>&ndash;&gt;-->
            <!--&lt;!&ndash;</div>&ndash;&gt;-->
        <!--</div>-->
        <!--<div class="ui divider"></div><br>-->
        <div class="ui cards" id="CountCard">
            <div class="ui raised card">
                <div class="content">
                    <div class="ui  header">用户总数<div class="ui blue label" style="float: right;font-size: 7px">User</div></div>
                    <div class="ui divider"></div>
                    <router-link class="countNum" :to="{ path: '/user'}">{{ top_info.user_num }}</router-link><p class="countDesc">All Users</p>
                </div>
            </div>
            <div class="ui raised card">
                <div class="content">
                    <div class="ui  header">机器总数<div class="ui green label" style="float: right;font-size: 7px">Host</div></div>
                    <div class="ui divider"></div>
                    <a class="countNum">{{ top_info.host_num }}</a><p class="countDesc">All Hosts</p>
                </div>
            </div>
            <div class="ui raised card">
                <div class="content">
                    <div class="ui  header">在线用户<div class="ui teal label" style="float: right;font-size: 7px">Online</div></div>
                    <div class="ui divider"></div>
                    <a class="countNum">{{ monitor_info.dp_user_online + monitor_info.mt_user_online }}</a><p class="countDesc">Online Users</p>
                </div>
            </div>
            <div class="ui raised card">
                <div class="content">
                    <div class="ui  header">已连后端机器<div class="ui red label" style="float: right;font-size: 7px">Connected</div></div>
                    <div class="ui divider"></div>
                    <a class="countNum">{{ monitor_info.backend_online }}</a><p class="countDesc">Connected Hosts</p>
                </div>
            </div>
        </div>
        <div class="ui cards">
            <div class="ui  card" id="UserCard">
                <div class="content">
                    <div class="ui  header"><h3 class="topHeader">Top Users
                        <div class="ui icon button" style="font-size:8px" data-tooltip="本周登录服务器次数排行" data-position="bottom center" data-inverted=""><i class="help icon"></i></div>
                    </h3></div>
                    <!--<div class="ui middle aligned divided list">-->
                        <!--&lt;!&ndash;<p>1.user1</p>&ndash;&gt;-->
                        <!--<div class="item" v-for="(user, index) in top_info.top_user" v-show="index<10">-->
                            <!--<div class="right floated content"></div>-->
                            <!--<div class="content">-->
                                <!--<div class="ui circular label" :class="{'teal': index<3}">{{ index+1 }}</div>-->
                                <!--&nbsp;&nbsp;{{ user[0] }}-->
                                <!--<span style="float: right;">{{ user[1] }}</span>-->
                            <!--</div>-->
                        <!--</div>-->
                    <!--</div>-->
                    <!--<div v-echarts="top_users_bar" theme="green" style="width: 260px; height: 120px"></div>-->
                    <user-bar :label="top_user" :data="top_num" :width="150" :height="150" v-if="show.bar"></user-bar>
                    <!--<div class="ui red progress">-->
                        <!--<div class="bar" style="min-width: 50px"><div class="progress">54%</div></div>-->
                    <!--</div>-->
                </div>
            </div>
            <div class="ui  card" id="Chart">
                <div class="content">
                    <div class="ui header"
                         style="text-align: center; color: darkslategrey; font-family: 'Open Sans', sans-serif;font-size: 18px">
                        Two Weeks Report</div>
                    <report-chart :width="180" :height="450" :data="top_info.chart_data" v-if="show.chart"></report-chart>
                </div>
            </div>
            <!--<div class="ui  card" id="RecordCard">-->
                <!--<div class="content">-->
                    <!--&lt;!&ndash;<div class="ui header"><h3 class="topHeader"><i class="middle orange student icon"></i>Top Records</h3></div>&ndash;&gt;-->
                    <!--<div class="ui header"><h3 class="topHeader">Top Records-->
                        <!--<div class="ui icon button" style="font-size:8px" data-tooltip="最近10次登录" data-position="bottom center" data-inverted=""><i class="help icon"></i></div>-->
                    <!--</h3></div>-->
                    <!--<div class="ui middle aligned divided list">-->
                        <!--<div class="item" v-for="(record, index) in top_info.top_record" v-show="index<10">-->
                            <!--<div class="right floated content"></div>-->
                            <!--<div class="content">-->
                                <!--<div class="ui circular label" :class="{'teal': index<3}">{{ index+1 }}</div>-->
                                <!--&nbsp;&nbsp;{{ record.user_name }}-->
                                <!--<span style="float: right;color:gray;font-size: 6px"> {{ record.login_time }}</span>-->
                                <!--<span style="float: right;">登录&nbsp;&nbsp;&nbsp;{{ record.host_name }}</span>-->
                            <!--</div>-->
                        <!--</div>-->
                    <!--</div>-->
                <!--</div>-->
            <!--</div>-->
        </div>
    </div>
</template>

<script>
    import store from '../vuex/store'
    import TopUserBar from '../components/vueChart/TopUser.js'
    import MonthlyReport from '../components/vueChart/MonthlyReport.js'
    export default{
        components: {
            'user-bar': TopUserBar,
            'report-chart': MonthlyReport,
        },
        data(){
            return {
                show: {
                    'bar': false,
                    'chart': false
                },
                my_info: {},
                login_history: {},
                top_info: {},
                top_user: [],
                top_num: [],
                monitor_info: {},
                tag: true
            }
        },
        methods: {
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
            getLoginHistory() {
                let _self = this;
//                api.get_login_history.get({'user_uid': _self.my_info.uid}).then(
//                    function(response){
//                        _self.login_history = response.data.result;
//                    },
//                    function(response){
//                    }
//                );
                api.get_top_users.get().then(
                    function(response) {
                        _self.top_info = response.data.result;

                        // Top Users Data
                        _self.top_info.top_user.forEach(function(user){
                            _self.top_user.push(user[0]);
                            _self.top_num.push(user[1]);
                        });
                        _self.show.bar = true;
                        _self.show.chart = true;
                    },
                    function(response){}
                );
//                api.monitor.get().then(
//                    function(response) {
//                        _self.monitor_info = response.data.result;
//                    },
//                    function(response){}
//                );
            },

        },
        mounted(){
            this.getMyInfo();
            this.getLoginHistory();
        }
    }
</script>
<style>
    #UserCard {
        min-width: 470px;
        border: 0;
        min-height: 500px;
        /*height: 52%;*/
        /*overflow-y: scroll;*/
    }
    #Chart {
        min-width: 740px;
        min-height: 400px;
        /*background-color: black;*/
    }
    #RecordCard {
        min-width: 300px;
    }
    #CountCard {
        padding-left: 40px;
        /*align-content: center;*/
        width:100%
    }
    #CountCard > .ui.raised.card {
        max-width: 250px;
        border-top: 3px solid lightgray
    }
    #CountCard > .ui.raised.card > .content > .ui.header {
        color: darkslategrey;
        font-family: 'Open Sans', sans-serif;
        font-size: 15px
    }
    #CountCard > .ui.raised.card > .content > .countNum {
        color: darkcyan;
        font-size: 28px;
        font-weight:100;
        line-height: 40px;
        font-family: 'Open Sans', sans-serif
    }
    #CountCard > .ui.raised.card > .content > .countDesc {
        color: darkgray;
        font-size: 8px
    }
    .topHeader {
        color: gray;
        font-size: 28px;
        font-weight:100;
        font-family: "Droid Sans", sans-serif;
    }
</style>