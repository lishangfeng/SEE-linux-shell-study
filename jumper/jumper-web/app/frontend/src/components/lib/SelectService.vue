<template>
    <div class="ui search">
        <div class="ui fluid icon input">
            <input class="prompt" type="text" placeholder="输入应用名"
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
                    <div class="title">{{ option.project_name }}</div>
                </div>
            </a>
            <div class="message" v-if="!options.length">没有结果</div>
        </div>
    </div>

</template>
<script>
    export default{
        data(){
            return{
                open: false,
                options: [{'project_name': ''}],
                getResponse: [],
                myResult: this.result,
                inputActive: false,
            }
        },
        components:{
        },
        props: {
            result: '',
            selectfunc:{
                type: Function,
            },
            name: {
                type: String,
                default: 'service'
            },
        },
        methods: {
            focus(){
                this.inputActive = true;
                this.getResults(this.myResult);
            },
            blur(){
                this.inputActive = false;
                this.closeResults();
            },
            openResults(){
                if (! this.inputActive) {
//                    console.log('input 没有激活');
                    return;
                }
                if (! this.options) {
//                    console.log('results 没有内容');
                    return;
                }
                this.open = true;
            },
            closeResults(){
                this.open = false;
            },
            select(option){
                this.myResult = option.project_name;
//                this.$el.find('input').blur()
                this.blur();
                if(this.selectfunc){
                    this.selectfunc(option.project_name);
                }
            },
            getResults(val){
                let _self = this;
                if (!val){
                    return;
                }
                if(_self.name == 'service'){
                    api.cmdb.get({type: 'search',name: val}).then(function(response){
                        _self.options = response.data.result.result;
                        _self.openResults();
                    }, function(response){
                    })
                }
            },
        },
        watch: {
            result(val) {
                this.myResult = val;
            },
            myResult: function(val){
                if (!val){
                    this.options=[];
                    return;
                }
                this.getResults(val);
            }
        }
    }
</script>
