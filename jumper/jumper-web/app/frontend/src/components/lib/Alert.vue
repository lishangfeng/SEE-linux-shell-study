<template>
    <div
            v-show="myShow"
            class="ui message icon"
            v-bind:class="{
      'success':(type == 'success'),
      'warning':(type == 'warning'),
      'info':	(type == 'info'),
      'top': 			(placement === 'top'),
      'top-right': 	(placement === 'top-right')
    }"
            transition="fade"
            v-bind:style="{width:width}"
            :show="myShow"
            :duration="3000"
            width="350px"
            placement="top-right"
            dismissable
    >
        <i v-show="dismissable" type="button" class="close icon"
                @click="myShow = false">
        </i>
        <i class="small icon"
           v-bind:class="{ 'check':(type == 'success'), 'remove':(type == 'warning'), 'checkmark':	(type == 'info')}"
        ></i>
            <div class="content">
                <p>{{ message }}</p>
            </div>
    </div>

</template>


<script>
//    import coerceBoolean from './utils/coerceBoolean.js'

    export default {
        data (){
            return {
                myShow:this.show
            }
        },
        props: {
            type: {
                type: String,
                default: 'info'
            },
            dismissable: {
                type: Boolean,
//                coerce: coerceBoolean,
                default: false,
            },
            show: {
                type: Boolean,
//                coerce: coerceBoolean,
                default: true,
                twoWay: true
            },
            duration: {
                type: Number,
                default: '3000'
            },
            width: {
                type: String,
                default: '350px'
            },
            placement: {
                type: String,
                default: 'top-right'
            },
            message: {
                type: String,
                default: 'message'
            }
        },
        watch: {
            show(val) {
                this.myShow = val;
            },
            myShow(val) {
                if (this._timeout) clearTimeout(this._timeout);
                if (val && Boolean(this.duration)) {
                    this._timeout = setTimeout(()=> this.myShow = false, this.duration);
                }
                this.$emit("get-show", this.myShow);

            }
        }
    }
</script>

<style>
    .fade-transition {
        transition: opacity .3s ease;
    }
    .fade-enter,
    .fade-leave {
        height: 0;
        opacity: 0;
    }
    .ui.message.top {
        position: fixed;
        top: 30px;
        margin: 0 auto;
        left: 0;
        right: 0;
        z-index: 2;
    }
    .ui.message.top-right {
        position: fixed;
        top: 40px;
        right: 50px;
        z-index: 2;
    }
</style>