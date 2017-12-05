<template>
    <form class="ui form">
        <div class="field">
            <div class="ui search">
                <div class="ui icon input">
                    <input class="prompt" type="text" placeholder="搜索 应用/IP/主机名"
                           @focus="focus"
                           v-on:keyup.13="options.length ? select0(options[0]):null"
                           v-model="value">
                    <!--v-on:keyup.13="select(options[0])"-->

                    <i class="search icon" v-if="!value"></i>
                    <i class="remove link icon" @click="remove()" v-else></i>
                </div>
                <div class="results transition"
                     v-bind:class="{hidden: !open, visible: open}"
                     v-if="options.length!=0"
                >
                    <!--<div class="category" v-for="option in options" @click="select(option)">-->
                    <!--<div class="name">#应用</div>-->
                    <a class="result" v-for="option in options" @click="select(option)">
                        <div class="content">
                            <div class="title">
                                {{ option }}
                            </div>
                            <div class="description" v-if="type!='app'">
                                <span v-if="type=='ip'">IP : </span>
                                <span v-if="type=='hostname'">主机名 : </span>
                                {{ value }}
                            </div>
                        </div>
                    </a>
                    <!--<div class="message" v-if="!options.length">没有结果</div>-->
                    <!--</div>-->
                </div>
            </div>
        </div>
    </form>
</template>
<script>
    export default {
        data() {
            return {
                open: false,
                options: [],
                value: '',
                type: 'app'
            }
        },
        components: {},
        methods: {
            focus() {
                this.open = true
            },
            blur() {
                this.open = false
            },
            select0(option) {
//                this.value = option;
                this.open = false;
                if (this.options.indexOf(this.value) != -1) {
                    option = this.value
                }
                this.selectCallback(option);
            },
            select(option) {
//                this.value = option;
                this.open = false;
                this.selectCallback(option);
            },
            searchVal(val) {
                val = val.trim();
                if (val.length < 2) {
                    this.type = 'app'
                    return true
                }
                if (/^[0-9.]+$/.test(val) && val.length <= 7) {
                    return true
                }
                let data = {'type': 'search', 'name': val};
//                如果以数字开头
                if (/^[a-z0-9A-Z\-]+$/.test(val)) {
                    this.type = 'app'
                }
                else if (/^[0-9.]+$/.test(val) && val.length > 7) {
                    data['type'] = 'search_ip';
                    this.type = 'ip'
                }
                else if (/^[a-zA-Z0-9.-]+$/.test(val)) {
                    this.type = 'hostname'
                    data['type'] = 'search_hostname';
                }
                else {
                    this.type = 'app'
                }
                this.getOptions(data);
            },
            getOptions(data) {
                let _self = this;
                api.cmdb.get(data).then(function (response) {
                    _self.options = response.data.result;
                    _self.open = true
                }, function (response) {
                    // error callback
                })
            },
            selectCallback(option) {
                let _path = '/tree/service/' + option
                if (this.type == 'app') {
                    if (this.$route.serviceTab) {
                        _path = _path + '/' + this.$route.serviceTab
                    }
                }
                else {
                    _path = _path + '/device?' + this.type + '=' + this.value.trim()
                }
                this.$route.router.go({path: _path})
            },
            remove() {
                this.value = '';
                this.open = false;
            }
        },
        watch: {
            value: function (val) {
                let _self = this;
                if (!val) {
                    _self.options = [];
                    return
                }
                this.searchVal(val);
            }
        }
    }
</script>