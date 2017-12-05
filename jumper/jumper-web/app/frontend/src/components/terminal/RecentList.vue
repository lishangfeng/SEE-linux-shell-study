<template>
    <div>
        <div><h4 style="color: darkgrey; line-height: 30px">我的登录历史&nbsp;&nbsp;&nbsp;&nbsp;<i class="red hourglass end icon"></i></h4></div>
        <div class="ui divider"></div>
        <div style="font-weight: 100; color: darkgray">(轻戳主机名，可快速登录^.^)</div>
        <div v-if="JSON.stringify(login_history) == '{}'">
            <div><br>还木有登录历史哦~ </div>
        </div>
        <div class="ui list" v-else>
            <div class="item" v-for="record in sortLetter"
                 style="cursor: pointer">
                <a @click="getUUID(record.host_name)">- {{ record.host_name }}</a>
            </div>
        </div>
        <br>
    </div>

</template>
<script>
    import store from '../../vuex/store.js'
    export default{
        data(){
            return{
                my_info: {},
                uuid: '',
                login_history: {}
            }
        },
        methods: {
            getUUID(host_name) {
                let _self = this;
                api.get_uuid.save({'user_name': _self.my_info.login_name, 'origin': 'jumper',
                                                                                        'host_name': host_name}).then(
                    function(response) {
                        if (response.data.code == 200){
                            _self.uuid = response.data.result['uuid'];
                            let url = location.origin + '/#/terminal?host_name=' + host_name + '&uuid=' + _self.uuid;
                            window.open(url, '_blank');
                        }
                    },
                    function(response){
                    }
                )
            },
            getRecentHost() {
                let _self = this;
                api.get_login_history.get({'user_uid': _self.my_info.uid}).then(
                    function(response){
                        _self.login_history = response.data.result;
                    }
                )
            }
        },
        mounted() {
            this.my_info = store.getters.getMyInfo;
            this.getRecentHost();
        },
        computed: {
            sortLetter: function () {
                return this.login_history.sort(function (x, y) {
                    return x.host_name.localeCompare(y.host_name);
                });
            }
        }
    }
</script>