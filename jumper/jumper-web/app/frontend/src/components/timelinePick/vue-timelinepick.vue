<template>
    <div class="v-timeline" :style="wrapStyle">
        <div class="vtime-type">
            <span id="second"></span>
        </div>
        <div class="vtimeContainer" >
        </div>
    </div>
</template>
<script>
import Timelinepick from "./timelinepick"
export default {
    props:{
        option:{
            type:Object,
            require:true,
            default:function(){
              return {
              }
            }
        },
        width:{
            type:Number,
            required: false,
            default:200
        },
        height:{
            type :Number,
            required: false,
            default:50
        },
        handler:{
            required: false
        }
    },
    data(){
        return {
            wrapStyle:{
                width : this.width +"px",
                height : this.height +"px"
            }
        }
    },
    methods :{
        init(){
             this.itemMagicHover(this.$el.querySelector("#second"));
             this.option.el = this.$el.querySelector(".vtimeContainer");
             this.option.parent = this.option.el.parentNode ;
             this.option.callback = this.handler;
             this.wrapStyle.width =  this.width +"px" ;
             this.timelinepick = new Timelinepick(this.option)
        },
        itemMagicHover(target){
            TweenMax.to(target, 0.2, {alpha : 1, scaleX : 1.5, scaleY : 1.5});
        },
        itemMagicOver(target){
            TweenMax.to(target, 0.2, {alpha : 0.5, scaleX : 1, scaleY : 1});
        }
    },
    filters:{
    },
    mounted() {
        this.init()
    }
}
</script>

<style scoped>
.v-timeline{
   }

.vtime-type{
    width: 100%;
    text-align: left;
}
.vtime-type img{
    margin-left: 25px;
    margin-top: 5px;
    width : 35px;
    height : 30px;
    cursor: pointer;
}
</style>