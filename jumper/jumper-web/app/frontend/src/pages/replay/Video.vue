<template>
    <div class="container">
        <div class="ui basic segment" id="term"></div>
        <!--<div>-->
            <timelinepick id="timeLine"
                    :option="options" :width="width" :height="height" :handler="changeAction">
            </timelinepick>
        <!--</div>-->
        <div class="ui raised segment" id="rightBar">
            <div style="text-align: center;">
                <!--<div class="ui basic icon button" @click="rate = rate > 1 ? rate-1 : 1" id="playBackwardRate" data-tooltip="减速-1" data-position="bottom right" data-inverted="">-->
                    <!--<i class="large blue step backward icon"></i>-->
                <!--</div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-->
                <div class="ui basic icon button" @click="play=!play" id="Play">
                    <i class="large blue play icon" v-if="play"></i>
                    <i class="large red pause icon" v-else></i>
                </div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <!--<div class="ui basic icon button" @click="rate = rate < 10 ? rate+1 : 10" id="playForwardRate" data-tooltip="快进x1（max:10）" data-position="bottom left" data-inverted="">-->
                    <!--<i class="large blue fast forward icon"></i>-->
                <!--</div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-->
            </div><br>
            <div class="ui orange small basic icon button" id="Skip" data-tooltip="当录像中提示可［跳过］等待时，方可点击生效"
                 style="float: right;" data-position="bottom right" data-inverted="">
                    跳过
                </div>
            <div class="ui very basic table">
                <table class="ui very basic table">
                    <thead>
                    </thead>
                    <tbody>
                        <tr><td>总时长 :</td> <td>{{ total }}</td></tr>
                        <!--<tr><td>播放速度 :</td> <td>{{ rate }}x</td></tr>-->
                        <tr><td>选择播放时段 :</td> <td style="color: darkorange;"><div><input id="startTime" v-model="new_start_time" disabled=""></div>-
                            <div><input id="endTime" v-model="new_end_time" disabled=""></div></td></tr>
                        <tr><td>开始时间 :</td>
                            <td>{{start.date + ' ' + start.time}}
                            </td>
                        </tr>
                        <tr><td>结束时间 :</td>
                            <td>{{end.date + ' ' + end.time}}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </div>
</template>

<script>
    import timelinepick from "../../components/timelinePick/vue-timelinepick.vue"
    import '../../components/lib/utils/createjs'
    import '../../components/lib/utils/TweenMax'
    import './../terminal/jquery-2.1.1.js'
    import './../terminal/term.js'
    import './video.js'


    export default {
        components: {
            timelinepick
        },
        data (){
            return{
                width: 800,
                height: 30,
                options : {
                    "threshold": parseInt(this.$route.query.end),
                    "number": 100,
                    "spanMinNumber": 2,
                    "isFixedDrag" : false,
                    "spanIndex": {start: 0, end: 100},
                    "type": this.$route.query.type ? this.$route.query.type : 'second',
                    "dateFormat" : 'yyyy-MM-dd hh:mm:ss',
                    // 箭头颜色
                     "arrowColor": "#00b1fe",
                    // 滑块颜色
                    "spanColor": "#a2993e",
                    // 滑块按钮颜色
                    "buttonColor" : "#ff8251",
                    "interval": (parseInt(this.$route.query.end) - parseInt(this.$route.query.start)) / 100
                },
                new_start_time: 0,
                new_end_time: 0,
                play: true,
                start: {'date': '', 'time': '00:00:00'},
                end: {'date': '', 'time': '00:00:00'},
                total: 0,
                rate: 1
            }
        },
        methods: {
            getTime() {
                let _self = this;
                if (_self.$route.query.start) {
                    let start_date = new Date(parseInt(_self.$route.query.start));
                    _self.start.date = start_date.getFullYear() + '-' +
                        (start_date.getMonth()+1 < 10 ? '0'+(start_date.getMonth()+1) : start_date.getMonth()+1) + '-'
                         + (start_date.getDate() < 10 ? '0'+start_date.getDate() : start_date.getDate());
                    _self.start.time = start_date.toTimeString().split(' ')[0];
                    _self.new_start_time = _self.start.date + ' ' + _self.start.time
                }
                if (_self.$route.query.end) {
                    let end_date = new Date(parseInt(_self.$route.query.end));
                    _self.end.date = end_date.getFullYear() + '-' +
                        (end_date.getMonth()+1 < 10 ? '0'+(end_date.getMonth()+1) : end_date.getMonth()+1) + '-'
                         + (end_date.getDate() < 10 ? '0'+end_date.getDate() : end_date.getDate());
                    _self.end.time = end_date.toTimeString().split(' ')[0];
                    _self.new_end_time = _self.end.date + ' ' + _self.end.time
                }
                this.time_format((Date.parse(_self.new_end_time) - Date.parse(_self.new_start_time)) / 1000)
            },
            time_format(seconds) {
                let d = parseInt(seconds / (3600 * 24));
                let h = parseInt((seconds - d * 24 * 3600) / 3600);
                let m = parseInt((seconds - d * 24 * 3600 - h * 3600) / 60);
                let ss = seconds - d * 24 * 3600 - h * 3600 - m * 60;
                if (d) {
                    this.total = d + ' 天 ' + h + ' 时 ' + m + ' 分 ' + ss + ' 秒'
                } else {
                    this.total = h + ' 时 ' + m + ' 分 ' + ss + ' 秒'
                }
            },
            changeAction(e){
                this.new_start_time = e.startTime;
                this.new_end_time = e.endTime;
                this.time_format((Date.parse(this.new_end_time) - Date.parse(this.new_start_time)) / 1000)
            }
        },
        mounted() {
            this.getTime()
        }
    }

</script>

<style>
    .container {
        /*padding-bottom: 70px;*/
        min-height: 630px;
        /*padding-left: 15%;*/
    }
    #timeLine {
        margin-top: 465px;
        position: absolute;
    }
    #rightBar {
        right: 5px;
        min-width: 350px;
        top: 130px;
        border: none;
        position: fixed;
    }
    #term {
        /*padding-bottom: 20px;*/
    }
</style>