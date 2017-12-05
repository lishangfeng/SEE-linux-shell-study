<template>
    <div class="ui pagination menu">
        <a class="item" @click="current = 1"><i class="angle double left icon"></i></a>
        <a class="item" @click="current == 1 ? null: current--"><i class="angle left icon"></i> </a>
        <a class="item" @click="current == all ? null : current++"><i class="angle right icon"></i></a>
        <a class="item" @click="current = all"><i class="angle double right icon"></i></a>
        <span class="item">
            <small><em>{{current}} / {{ all }} 页 , 共 {{ num }} 项
                <!--, 每页-->
                <!--<div class="ui simple inline dropdown">-->
                    <!--{{ pagesize }}-->
                    <!--<i class="dropdown icon"></i>-->
                    <!--<div class="menu">-->
                        <!--<a class="item" v-click="pagesize = 25"> 25 </a>-->
                        <!--<a class="item" v-click="pagesize = 50"> 50 </a>-->
                        <!--<a class="item" v-click="pagesize = 100"> 100 </a>-->
                    <!--</div>-->
                <!--</div>-->
            </em></small>
        </span>
    </div>
</template>
<script>
    export default{
        data(){
            return{
            }
        },
        props: {
            current: {
                type: Number,
                default: 1,
            },
            pagesize: {
                type: Number,
                default: 25
            },
            num: {
                type: Number,
                default: 1,
            },
            switchpage: {
                type: Function,
            }
        },
        computed: {
            all () {
                return (Math.ceil(this.num/this.pagesize));
            },
        },
        methods: {
        },
        watch: {
            current (newValue , oldValue){
                if (oldValue) {
                    this.switchpage(newValue);
                }
            }
        }

    }
</script>