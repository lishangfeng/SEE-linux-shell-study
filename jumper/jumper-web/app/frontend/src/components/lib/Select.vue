<template>
    <div class="ui selection dropdown" @click="open=!open" v-bind:class="{active: open, visible: open}">
        <!--<input v-model="input">-->
        <div class="default text" v-if="! mySelected">{{ myTitle }}</div>
        <div class="text">{{ choice }}</div>
        <div class="menu transition" v-bind:class="{visible: open}" @mouseleave="open ? open=false : null ">
            <div class="item" v-bind:class="{active: option==mySelected}"
                 v-for="option in myOptions" @click="select(option)">
                {{ option.label }}
            </div>
        </div>
        <i class="dropdown icon" v-if="!mySelected"></i>
        <i class="remove link icon" style="float: right" @click="remove()" v-else></i>
    </div>
</template>
<script>
    export default{
        data(){
            return{
                open: false,
                choice: '',
                mySelected: this.selected,
                myOptions: this.options,
                myTitle: this.title
            }
        },
        methods: {
            select(key)   {
                let _self = this;
                _self.choice = key.label;
                _self.mySelected = key.value;
            },
            remove() {
                let _self = this;
                _self.choice = '';
                _self.open = true;
                _self.mySelected = '';
            }
        },
        props:{
            selected: '',
            options: {
                type: Array
            },
            title: {
                type: String,
                default: ''
            }
        },
        watch: {
            selected(val) {
                this.mySelected = val;
            },
            options(val) {
                this.myOptions = val;
            },
            title(val) {
                this.myTitle = val;
            },
            mySelected(val) {
                this.$emit("filter-change", val);
            }
        }
    }
</script>