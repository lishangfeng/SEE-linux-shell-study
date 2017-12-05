<template>
    <div>
        <div><h4 style="color: darkgrey; line-height: 30px">我的关注&nbsp;&nbsp;&nbsp;&nbsp;<i class="red heartbeat icon"></i></h4></div>
        <div class="ui divider"></div>
        <div style="font-weight: 100; color: darkgray">(轻戳主机名，可快速登录^.^)</div>
        <p></p>
        <!--<div style="font-weight: 300; font-size: small; color: darkgray">*** 注：此关注来自 ttt.dp/</div>-->
        <div v-if="!result.length">
            <div>还木有收藏的应用哦~ </div>
        </div>
        <div class="ui list" v-else>
            <div class="item" v-for="prj in sortPrj">
                <div style="cursor:pointer;" @click="selected_prj=prj.name, show.loading=true, getDevices(), showDev[prj.name]=!showDev[prj.name]">
                    <i class="icon" v-bind:class= "showDev[prj.name] && selected_prj==prj.name ? 'dropdown' : 'right triangle'"></i>
                    {{ prj.name }}
                </div>
                <div class="ui list" v-if="selected_prj==prj.name && !show.loading && showDev[prj.name]">
                    <div class="item" v-for="device in prj_devices[selected_prj]" style="cursor:pointer;">
                        <a @click="getUUID(device)">&nbsp;&nbsp;&nbsp;&nbsp;- &nbsp;{{ device }}</a>
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
    import store from '../../vuex/store.js'
    import Alert from '../../components/lib/Alert.vue'

    export default{
        data(){
            return{
                my_info: {},
                uuid: '',
                selected_prj: '',
                result: {},
                showDev: {},
                prj_devices: {},
                show: {
                    'loading': true,
                    alert: false,
                    message: 'e',
                    alert_type: 'warning'
                }
            }
        },
        components: {
            'alert': Alert,
        },
        methods: {
            getShow(val) {
                this.show.alert = val;
            },
            getMark() {
                let _self = this;
                api.my_mark.get().then(
                    function(response){
                        _self.result = response.data.result.result.objects;
                    }
                )
            },
            getUUID(host_name) {
                let _self = this;
                api.get_uuid.save({'user_name': _self.my_info.login_name, 'origin': 'jumper',
                                                                                        'host_name': host_name}).then(
                    function(response) {
                        if (response.data.code === 200){
                            _self.uuid = response.data.result['uuid'];
                            let url = location.origin + '/#/terminal?host_name=' + host_name + '&uuid=' + _self.uuid;
                            window.open(url, '_blank');
                        }
                        else {
                            _self.show.alert_type = 'warning';
                            _self.show.alert = true;
                            _self.show.message = response.data.msg;
                        }
                    },
                    function(response){
                        _self.show.alert_type = 'warning';
                        _self.show.alert = true;
                        _self.show.message = '[ 服务器返回' + response.status + '] ' + response.data;
                        // error callback
                    }
                )
            },
            getDevices() {
                let _self = this;

                // store分发未完成时，避免导致get_uuid失败
                if (JSON.stringify(_self.my_info) === '{}') {
                    api.user_my.get().then(
                    function(response){
                        _self.my_info = response.data.result;
                    })
                }

                if (!(_self.selected_prj in _self.prj_devices)){
                    if (!(_self.selected_prj in _self.showDev)){
                        _self.showDev[_self.selected_prj] = false
                    }
                    api.cmdb.get({name: _self.selected_prj, type: 'app_host_list'}).then(
                        function(response){
                            if (response.data.code === 200){
                                let result = response.data.result.devices;
                                let host_list = [];
                                result.forEach(function(host) {
                                    host_list.push(host.hostname)
                                });
                                _self.prj_devices[_self.selected_prj] = host_list;
                                _self.show.loading = false
                            }
                    });
                }
                else {
                    _self.show.loading = false
                }
                for (var key in _self.showDev) {
                    if (key !== _self.selected_prj) {
                        _self.showDev[key] = false
                    }
                }
            }
        },
        mounted(){
            this.my_info = store.getters.getMyInfo;
            this.getMark();
        },
        computed: {
            sortPrj: function () {
                return this.result.sort(function (x, y) {
                    return x.name.localeCompare(y.name);
                });
            }
        }
    }
</script>