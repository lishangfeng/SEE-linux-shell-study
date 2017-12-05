<template>
    <div>
        <header-component id="topMenu"></header-component>
        <div class="view">
            <keep-alive>
                <router-view v-if="$route.meta.keepAlive"></router-view>
            </keep-alive>
            <router-view v-if="!$route.meta.keepAlive"></router-view>
        </div>
        <!--<bottom-component></bottom-component>-->
    </div>
</template>

<script>
    import HeaderComponent from './Header.vue'
    import BottomComponent from './Bottom.vue'
    export default{
        data(){
            return{
                isToggle: true,
            }
        },
        components:{
            'header-component': HeaderComponent,
            'bottom-component': BottomComponent,
        },
        mounted(){
        },
    }
</script>

<style>

    #topMenu {
        /*background: #f1f2f7;*/
        padding-left: 2%;
        padding-right: 2%;
        padding-top:0;
        padding-bottom:1px;
        margin-top: 0px !important;
        margin-bottom: 20px !important;
        height: 0px;
        border: 0;
    }

    .view {
        padding: 15px ;
        padding-left: 2%;
        padding-right: 4%;
    }
</style>