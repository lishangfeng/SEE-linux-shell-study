<template>
    <div class="container">
        <div style="color: red; top: 40px; position: fixed;left: 400px">
            ***注意：终端空闲10分钟，将自动断开连接！***（需重连,请刷新页面）<span style="color: grey; font-size: small">&nbsp;&nbsp;ps：点左边绿色竖栏，隐藏／显示侧边栏</span>
        </div>
        <div class="ui basic segment" id="term"></div>
        <div class="ui icon button" id="winShow" data-tooltip="修改窗口大小"
             data-position="bottom right" data-inverted=""><i class="maximize icon"></i></div>
        <p></p>
        <div class="termChangBar">
            <div class="ui labeled input">
                <div class="ui label">width</div>
                <input type="number" min=120 value="120" placeholder="120" id="term-col" style="width:80px"/></div>
            <div class="ui button" style="color: black" id="col-row" >修改<span><p style="font-size: xx-small; font-weight: 100">(默认120)</p></span></div>
        </div>
    </div>
</template>

<script>
    import './jquery-2.1.1.js'
    import './term.js'
    import './webTerminal.js'
    export default {
        data (){
            return{
                show: false
            }
        }
    }

</script>

<style>
    .container {
        /*padding-bottom: 70px;*/
        min-height: 630px;
        /*padding-left: 15%;*/
    }
    #winShow {
        top: 40px;
        right: 0;
        background-color: darkcyan;
        font-size: 3px;
        position: fixed;
    }
    .termChangBar {
        margin-top: 30px;
        /*width: 150px;*/
        /*line-height: 9;*/
        /*border: 1px solid #ffffff;*/
        background-color: #ffffff;
        position: fixed;
        right: 6%;
        top:0
    }
</style>