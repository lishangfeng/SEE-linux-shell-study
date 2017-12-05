<template>
    <div>
        <div class="ui fixed green borderless inverted menu" id="topNav">
            <router-link :to="'/dashboard'" class="item" :class="{'active': $route.meta.active == 'dashboard'}">
                <i class="home icon"></i>主页
            </router-link>
            <router-link :to="'/user'" class="item" :class="{'active': $route.meta.active == 'user'}">
                <i class="user icon"></i>用户
            </router-link>
            <router-link :to="'/group'" class="item" :class="{'active': $route.meta.active == 'group'}">
                <i class="users icon"></i>用户组
            </router-link>
            <!--<router-link :to="'/permission'" class="item" :class="{'active': $route.meta.active == 'permission'}">-->
                <!--<i class="lock icon"></i>登录权限-->
            <!--</router-link>-->
            <!--<router-link :to="'/sudo'" class="item" :class="{'active': $route.meta.active == 'sudo'}">-->
                <!--<i class="key icon"></i>Sudo权限-->
            <!--</router-link>-->
            <router-link :to="'/terminal'" class="item" :class="{'active': $route.meta.active == 'terminal'}">
                <i class="terminal icon"></i>Terminal
            </router-link>
            <!--<router-link :to="'/danger'" class="item" :class="{'active': $route.meta.active == 'danger'}">-->
                <!--<i class="warning icon"></i>危险命令-->
            <!--</router-link>-->
            <!--<router-link :to="'/history'" class="item" :class="{'active': $route.meta.active == 'history'}">-->
                <!--<i class="text file icon"></i>历史命令-->
            <!--</router-link>-->
            <!--<router-link :to="'/record'" class="item" :class="{'active': $route.meta.active == 'record'}">-->
                <!--<i class="film icon"></i>屏幕录像-->
            <!--</router-link>-->
            <router-link :to="'/help'" class="item" :class="{'active': $route.meta.active == 'help'}">
                <i class="help icon"></i>使用教程
            </router-link>

            <div class="right menu">
                <!--<router-link :to="'/advice'" class="item" :class="{'active': $route.meta.active == 'advice'}">-->
                    <!--<i class="comment outline icon"></i>建议反馈-->
                <!--</router-link>-->
                <div class="item">
                    <div class="ui simple dropdown item">
                        {{ user_info.name }}
                        <i class="dropdown icon"></i>
                        <div class="menu">
                            <a class="item" href="/logout">退出</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
    import store from '../vuex/store.js'
    import '../../node_modules/semantic-ui-css/semantic.min.css'
    export default{
        data (){
            return {
                show: {
                    load: false
                },
                user_info: {},
                admin_role: ['op', 'sa', 'sre'],
                tag: true
            }
        },
        methods: {
            getUser() {
                let _self = this;
                api.user_my.get().then(
                    function (response) {
                        _self.user_info = response.data.result;
                        store.dispatch('updateMyInfo', _self.user_info);
                    },
                    function (response) {
                    }
                )
            }
        },
        mounted(){
            this.getUser();
        },

        reload() {
            let _self = this;
            _self.show.load = true;
            setTimeout(function () {
                _self.show.load = false
            }, 200)
        }
    }

</script>
<style>
    #topNav {
        padding-left: 3%;
        padding-right: 3%;
        height: 10px;
    }
</style>
