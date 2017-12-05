<template>
    <div class="ui search">
        <div class="ui icon input">
            <input class="prompt" type="text" placeholder="请输入账号查询"
                   v-model="myResult"
                   @focus="focus"
                   @blur="blur"
                   v-on:keyup.13="options.length ? select(options[0]) : null"
            >
            <i class="search icon"></i>
        </div>
        <div class="results transition"
             v-bind:class="{hidden: !open, visible: open}"
        >
            <a class="result" v-for="option in options" @mousedown="select(option)">
                <div class="content">
                    <div class="title">{{ option.login_name }}</div>
                </div>
            </a>
            <div class="message" v-if="!options.length">没有结果</div>
        </div>
    </div>

</template>
<script>
    export default {
        data() {
            return {
                open: false,
                options: [],
                getResponse: [],
                myResult: this.result,
                myIndex: this.index,
                inputActive: false,
            }
        },
        components: {},
        props: {
            result: '',
            index: {
                type: Number,
                default: 0
            },
        },
        methods: {
            focus() {
                this.inputActive = true;
                this.getResults(this.myResult);
            },
            blur() {
                this.inputActive = false;
                this.closeResults();
            },
            openResults() {
                if (!this.inputActive) {
//                    console.log('input 没有激活');
                    return;
                }
                if (!this.options) {
//                    console.log('results 没有内容');
                    return;
                }
                this.open = true;
            },
            closeResults() {
                this.open = false;
            },
            select(option) {
                this.myResult = option.login_name;
                this.$emit("select-user", this.myResult, this.myIndex, option.uid);
                this.myResult = ''; // 选择后清空记录
                this.blur();
            },
            getResults(val) {
                let _self = this;
                if (!val) {
                    return;
                }
                api.user.get({'@login_name': val}).then(function (response) {
                    _self.options = response.data.result.objects;
                    _self.openResults();
                }, function (response) {
                })
            },
        },
        watch: {
            result(val) {
                this.myResult = val;
            },
            index(val) {
                this.myIndex = val;
            },
            myResult: function (val) {
                if (!val) {
                    this.options = [];
                    return;
                }
                this.getResults(val);
            }
        }
    }
</script>
