<template>
    <div class="ui basic segment">
        <table class="ui very basic table">
            <thead>
            <tr>
                <th colspan="7">
                    <select-user
                            :name="'service'"
                            :selectfunc="search"
                            :result="selected_project">
                            <!--@select-service="getService">-->
                    </select-user>
                </th>
            </tr>
            <tr>
                <th>
                    <label class="ui mini label" @click="allSelected()" v-if="host_list.length" style="cursor: pointer">全选</label>
                   <span v-if="!host_list.length">主机名</span><i class="sort icon" @click="sort.reverse = sort.reverse * -1, sort.predicate='hostname'"></i>
                </th>
                <th>IP <i class="sort icon" @click="sort.reverse = sort.reverse * -1, sort.predicate='private_ip' "></i></th>
                <th>环境 <i class="sort icon" @click="sort.reverse = sort.reverse * -1, sort.predicate='env' "></i></th>
                <th>类型 <i class="sort icon" @click="sort.reverse = sort.reverse * -1, sort.predicate='ci_type' "></i></th>
                <th>状态 <i class="sort icon" @click="sort.reverse = sort.reverse * -1, sort.predicate='status' "></i></th>
                <th>上线时间 <i class="sort icon" @click="sort.reverse = sort.reverse * -1, sort.predicate='online_time' "></i></th>

            </tr>
            </thead>
            <tbody>
            <tr v-for="host in host_list">
                <!--{{host|json}}-->
                <td>
                    <div class="ui checkbox">
                        <input type="checkbox" v-model="selected" :id="host.ip" :value="host.private_ip.join()">
                        <label :for="host.ip">{{ host.hostname }}</label>
                    </div>
                </td>
                <td>{{ host.private_ip.join() }}</td>
                <td>{{ host.env }}</td>
                <td>{{ host.ci_type }}</td>
                <td>{{ host.status }}</td>
                <td>{{ host.online_time }}</td>
            </tr>
            </tbody>
            <tfoot>
            <tr>
                <th colspan="5">
                    共选择 {{ selected.length }} 台
                </th>
            </tr>
            </tfoot>
        </table>
    </div>
</template>
<script>
    import SelectUser from './SelectUser.vue'
    export default{
        data(){
            return{
                selected_project: '',
                host_list: [],
                sort: {
                    predicate: 'env',
                    reverse: 1,
                },
                selected: [],
                myResult: this.result,
                all:false
            }
        },
        props:{
            result: {},
        },
        components:{
            'select-user': SelectUser
        },
        methods:{
//            getService(val) {
//                this.selected_project = val;
//                console.log('get: '+ this.selected_project)
//            },
            search (service_name){
                if(!service_name){
                    return ;
                }
                let _self = this;
                _self.selected_project = service_name;
                api.cmdb.get({name: service_name, type: 'app_host_list'}).then(function(response){
                    _self.host_list = response.data.result.devices;
                    _self.selected = [];
                });
            },
            allSelected(){
                let _self = this;
                _self.all = !_self.all;
                if(_self.all){
                    _self.host_list.forEach(function(host) {
                        if(_self.selected.indexOf(host.private_ip.join())==-1) {
                            _self.selected.push(host.private_ip.join())
                        }
                    });
                }
                else{
                    _self.selected = [];
                }
            },
            Init() {
                if(this.myResult && JSON.stringify(this.myResult) != '[]' && !(this.myResult instanceof Array)){
                    let _self = this;
                    if (this.myResult.app_name) {
                        _self.selected_project = _self.myResult.app_name;
                        _self.search(_self.myResult.app_name)
                    }else {
                        _self.selected_project = JSON.parse(_self.myResult).app_name;
                        _self.search(JSON.parse(_self.myResult).app_name)
                    }
                }
            }
        },
        mounted() {
            this.Init();
        },
        watch:{
            result(val) {
                this.myResult = val;
            },
            selected(newV){
                let _self = this;
//                this.item$dispatch('child-msg', newV)

                _self.myResult = {
                    app_name: _self.selected_project,
                };
                _self.myResult.host_list = [];
                _self.host_list.forEach(function(host){
                    if(_self.selected.indexOf(host.private_ip.join())!=-1){
                        _self.myResult.host_list.push(host.private_ip)
                    }
                });
                this.$emit("select-hosts", _self.myResult, _self.host_list.length)
            },
        }
    }
</script>