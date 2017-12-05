<template>
    <div>
        <div class="ui basic segment" id="hostList" v-if="showBar">
            <a class="ui right green corner label" @click="is_tree = 'recent_list'" v-show="is_tree == 'mark_list'">
                <i class="exchange icon" style="cursor: pointer"></i>
            </a>
            <a class="ui right green corner label" @click="is_tree = 'mark_list'" v-show="is_tree == 'recent_list'">
                <i class="exchange icon" style="cursor: pointer;"></i>
            </a>
            <recent-list :active="$route.params" v-if="is_tree == 'recent_list'"></recent-list>
            <mark-list v-if="is_tree == 'mark_list'"></mark-list>
        </div>
        <div style="cursor: pointer; width: 12px; background-color: #19aa8d; position: fixed; margin-left: 226px; min-height: 700px;"
             @click="showBar=false" v-if="showBar">
            </div>
        <div class="ui basic segment" id="leftBar" @click="showBar=true" v-else></div>
        <!--<div style="position: fixed; margin-left: 16.5%; margin-top: 10px" @click="showBar=false" v-if="showBar">-->
            <!--<i class="orange large lock icon"></i>-->
        <!--</div>-->
        <!--<div  style="position: fixed; margin-left: -0.3%; margin-top: 10px" @click="showBar=true" v-if="!showBar">-->
            <!--<i class="orange unlock icon"></i>-->
        <!--</div>-->
        <div :style="{ 'padding-left': !showBar ? '10px' : '228px' }">
            <terminal-frame></terminal-frame>
        </div>
    </div>
</template>

<script>
    import Terminal from './Terminal.vue'
    import RecentList from '../../components/terminal/RecentList.vue'
    import MarkList from '../../components/terminal/MarkList.vue'
    export default{
        components: {
            'terminal-frame': Terminal,
            'recent-list': RecentList,
            'mark-list': MarkList
        },
        data(){
            return {
                showBar: true,
                my_info: {},
                is_tree: 'mark_list'
            }
        }
    }
</script>

<style>
    #leftBar {
        cursor: pointer;
        border-left: 15px solid #19aa8d;
        width: 1px;
        /*background-color: #19aa8d;*/
        position: fixed;
        margin-left: 0.38%;
        min-height: 700px;
    }
    #hostList {
        /*border-left: 4px solid #19aa8d;*/
        /*border-right: 2px solid #19aa8d;*/
        position: fixed;
        /*margin-top: -5px;*/
        padding-bottom: 20%;
        margin-left: -2%;
        width: 250px;
        min-height:600px;
        height: 100%;
        overflow-y: scroll;
        /*background: #203846;*/
        background: darkslategrey;
        /*color: #EEEEEE;*/
        color: #a7b1c2;
        /*-webkit-transition: all 0.5s ease;*/
        /*-moz-transition: all 0.5s ease;*/
        /*-o-transition: all 0.5s ease;*/
        /*transition: all 0.5s ease;*/
    }

    #hostList .ui.list>.item a {
        color: #a7b1c2 !important;
        /*color: #EEEEEE !important;*/
    }

    #hostList .ui.list > .item >div .selected {
        color: #19aa8d !important;
    }

    #hostList .ui.list>.item a:hover {
        color: #CD5C5C !important;
        /*background: #EEEEEE;*/
    }

    #hostList .ui.list>.item.selected {
        /*color: #1C5792 !important;*/
        /*color: #000000 !important;*/
        /*background: #EEEEEE;*/
        color: #19aa8d !important;
    }
</style>
