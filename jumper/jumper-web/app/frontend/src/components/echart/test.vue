<template>
    <div>
        <div class="ui three column grid" style="margin: 10px;">
            <div class="stretched row">
                <div class="column">
                    <div class="ui segment">
                        <chart :options="polar"></chart>
                    </div>
                </div>
                <div class="column">
                    <div class="ui raised segment">
                        <div class="ui link selection list">
                            <div class="item">
                                <div class="content">
                                    <div class="header">
                                        统计数据
                                    </div>
                                    <div class="ui statistics">

                                        <div class="teal statistic">
                                            <div class="value">
                                                5402
                                            </div>
                                            <div class="item">
                                                用户总数
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                402
                                            </div>
                                            <div class="item">
                                                用户组总数
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                81923
                                            </div>
                                            <div class="item">
                                                机器总数
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <p></p>
                        <div class="ui link selection list">
                            <div class="item">
                                <div class="content">
                                    <div class="header">
                                        权限数据
                                    </div>
                                    <div class="ui statistics">
                                        <div class="teal statistic">
                                            <div class="value">
                                                1230
                                            </div>
                                            <div class="item">
                                                登录授权数
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                1390
                                            </div>
                                            <div class="item">
                                                Sudo授权数
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="column">
                    <div class="ui raised segment">
                        <a class="ui red ribbon label">一周排行榜</a>
                        <span>登录次数</span>
                        <div class="ui link selection list">
                            <div class="item">
                                <div class="content">
                                    <div class="ui statistics">
                                        <div class="teal statistic">
                                            <div class="value">
                                                245
                                            </div>
                                            <div class="label">
                                                张三
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                200
                                            </div>
                                            <div class="label">
                                                李四
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                100
                                            </div>
                                            <div class="label">
                                                王五
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>


                        <a class="ui red ribbon label">一周深夜排行榜</a>
                        <span>凌晨登录次数</span>
                        <div class="ui link selection list">
                            <div class="item">
                                <div class="content">
                                    <div class="ui statistics">
                                        <div class="teal statistic">
                                            <div class="value">
                                                245
                                            </div>
                                            <div class="label">
                                                张三
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                200
                                            </div>
                                            <div class="label">
                                                李四
                                            </div>
                                        </div>
                                        <div class="teal statistic">
                                            <div class="value">
                                                100
                                            </div>
                                            <div class="label">
                                                王五
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
    .echarts {
        height: 450px;
        width: 400px;
        margin: 0;
        padding: 0;
    }
</style>

<script>
    export default {

        data: function () {
            return {
                polar: {
                    title: {
                        text: '某站点用户访问来源',
                        subtext: '纯属虚构',
                        x: 'center'
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c} ({d}%)"
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'left',
                        data: ['直接访问', '邮件营销', '联盟广告', '视频广告', '搜索引擎']
                    },
                    series: [
                        {
                            name: '访问来源',
                            type: 'pie',
                            radius: '55%',
                            center: ['50%', '60%'],
                            data: [
                                {value: 335, name: '直接访问'},
                                {value: 310, name: '邮件营销'},
                                {value: 234, name: '联盟广告'},
                                {value: 135, name: '视频广告'},
                                {value: 1548, name: '搜索引擎'}
                            ],
                            itemStyle: {
                                emphasis: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
</script>