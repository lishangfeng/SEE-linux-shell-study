<template>
    <div  style="min-height: 800px">
        <br>
        <div class="ui orange left fixed vertical menu" style="top: 50px; color: grey;">
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G1'] && scrollTop < ids['#G2'] || scrollTop == 0}"
                 @click="goAnchor('#G1')">账号申请</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G2'] && scrollTop < ids['#G3']}"
                 @click="goAnchor('#G2')">修改密码</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G3'] && scrollTop < ids['#G4']}"
                 @click="goAnchor('#G3')">密码重置</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G4'] && scrollTop < ids['#G5']}"
                 @click="goAnchor('#G4')">ssh连接复用</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G5'] && scrollTop < ids['#G6']}"
                 @click="goAnchor('#G5')">登录跳板机</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G6'] && scrollTop < ids['#G7']}"
                 @click="goAnchor('#G6')">跳板机使用</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G7'] && scrollTop < ids['#G8']}"
                 @click=" goAnchor('#G7')">sftp文件中转</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G8'] && scrollTop < ids['#G9']}"
                 @click="goAnchor('#G8')">登录机器</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G9'] && scrollTop < ids['#G10']}"
                 @click="goAnchor('#G9')">sudo权限</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G10'] && scrollTop < ids['#G11']}"
                 @click="goAnchor('#G10')">windows SecureCRT设置</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G11'] && scrollTop < ids['#G12']}"
                 @click="goAnchor('#G11')">常见问题及解决方法</a>
              <a href="javascript:void(0)" class="item"
                 v-bind:class="{'active': scrollTop >= ids['#G12']}"
                 @click="goAnchor('#G12')">意见反馈</a>
        </div>

        <div class="ui basic segment" id="Content">
             <div style="text-align: right; color: darkblue; ">（暂时主要针对上海侧~）</div>
            <div class="item" id="G1">
                <h2>账号申请</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    新入职的同事需申请新跳板机账号。
                    <p>账号自助流程：<span><a href="http://ttt.dp/?#!/start/32" target="_blank">http://ttt.dp/?#!/start/32</a></span>  流程自动完成，
                    无需审批，"运维服务中心" 在大象上发给你初始密码。账号申请成功后，最晚20分钟后可用。</p>
                </div>
            </div>
            <br><br>
            <div class="item" id="G2">
                <h2>修改密码</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>'p' 命令修改密码。</p>
                    <p style="color: darkred;;"><i class="red info circle icon"></i> 新密码要求：</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;1）密码长度限制：8～16位；</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;2）密码必须至少包括其中三种: 数字, 大写字母, 小写字母, 特殊字符(^ $ . ? ! @ = + - % * &)；</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;3）不能为最近三次使用过的密码；</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;4）有效期为两个月。</p>
                </div>
                <p class="bottom-imgWrap"><img src='../assets/pwd.gif' alt="" style="width:38rem; height: 28rem;"></p>
            </div>
            <br><br><br>
            <div class="item" id="G3">
                <h2>密码重置</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>忘记密码时，可走密码重置自助流程：<span><a href="http://ttt.dp/?#!/start/32" target="_blank">http://ttt.dp/?#!/start/32</a></span>
                        流程自动完成，无需审批，"运维服务中心" 在大象上发给你重置后的 " 初始密码 "。
                    </p>
                </div>
                <p class="bottom-imgWrap"><img src='../assets/pwd-reset.gif' alt=""></p>
            </div>
            <br><br><br>
            <div class="item" id="G4">
                <h2>ssh连接复用</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>ssh协议支持连接复用 , 功能支持同一主机的多个 SSH 会话共享单一 TCP 连接进行通讯，一旦第一个连接建立，后续连接就不再需要凭证，
                        从而消除了每次连接同一机器都需要键入密码的麻烦并且大幅度节省了服务器端的资源。</p>
                    <p>在客户端节点如下配置<span style="color: blue;"> /etc/ssh_config </span> （或 <span style="color: blue;">~/.ssh/config </span> ）就可以直接开启ssh multiplexing功能</p>
                    <div style="background-color: lightyellow ; color: black">
                        <p>&nbsp;Host &nbsp;&nbsp; jumper.dper.com</p>
                        <p>&nbsp;ControlPersist&nbsp;&nbsp;  yes</p>
                        <p>&nbsp;ControlMaster &nbsp;&nbsp; auto</p>
                        <p>&nbsp;ControlPath &nbsp;&nbsp; ~/.ssh/master-%r@%h:%p</p>
                    </div>
                </div>
                <p class="bottom-imgWrap"><img src='../assets/multiplexing.gif' alt=""></p>
            </div>
            <br><br><br>
            <div class="item" id="G5">
                <h2>登录跳板机</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>在办公网环境下，输入命令：ssh  域账号@jumper.dper.com.&nbsp;&nbsp;&nbsp;若当前用户和域账号一致，也可直接输入命令：ssh  jumper.dper.com 登陆.</p>
                    <p style="color: darkred;;"><i class="red info circle icon"></i> 账号密码详情：</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1）<span style="color: black"> 密码：</span>自己最近设置的密码。（<span style="color: red"> 是 jumper 密码！！！不是 大象密码！</span>）</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2）<span style="color: black"> 动态口令：</span>支持两种动态码（输入一种即可）：1.大象app上的动态口令；2.每次登录jumper，都会在大象上收到如下图的验证码：</p>
                    <img src='../assets/code.png' style="width:30rem; height: 6rem;margin-left: 60px;">
                </div>
                <p class="bottom-imgWrap"><img src='../assets/ssh-jumper.gif' alt="" style="width:30rem; height: 22.5rem;"></p>
            </div>
            <br><br><br>
            <div class="item" id="G6">
                <h2>跳板机使用</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>成功登陆 jumper 后，会看到 jumper 的自定义终端，只允许输入固定的命令（如 'h' 命令显示帮助信息、'ssh'命令登陆目标机器等）</p>
                    <p style="color: darkred;"><i class="red info circle icon"></i> 快捷键／常用命令：</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1）<span style="font-weight: 800"> ctrl+B、ctrl+F 快捷键。</span>终端左右移动光标</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2）<span style="font-weight: 800"> Tab</span> 快捷键。自动补全命令、自动匹配查找主机名（仅限历史登陆过的机器）</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3）<span style="font-weight: 800"> ping</span> 命令。按ctrl+c中止。</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4）<span style="font-weight: 800"> history</span> 命令。输入 ' history ' ,查看历史命令。也可用 "向上/下  方向键" 调出历史命令。</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;v5）支持 <span style="font-weight: 800"> expect</span> 交互。</p>

                    <p style="color: darkred;;"><i class="red info circle icon"></i> 技能介绍：</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1）<span style="font-weight: 800"> getapp：</span>&nbsp;&nbsp;&nbsp;得到某应用的（线上）机器列表。命令输入：getapp 应用名 [ 例：getapp  op-duty  ]</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2）<span style="font-weight: 800"> pssh：</span> &nbsp;&nbsp;&nbsp;某个应用，所有线上机器，批量执行命令。命令输入：pssh 应用名 命令 [ 例：pssh op-duty uptime |awk '{print $1}'</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3）<span style="font-weight: 800"> plog：</span> &nbsp;&nbsp;&nbsp;某个应用，所有线上机器，批量查询日志命令,其中grep查询条件为必填。命令输入：plog 应用名 'grep查询条件' 日期 </p>
                </div>
                <p class="bottom-imgWrap"><img src='../assets/pssh.gif' alt=""></p>
            </div>
            <br><br><br>
            <div class="item" id="G7">
                <h2>sftp文件中转</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p style="color: red;">注意: 用户名和密码是和Jumper一样的, 没有Jumper账号是无法使用的</p>
                    <p style="color: black">PS：无论在本地还是线上或测试机器上，都必须先以Jumper账号密码登录jumper.ftp.dp，再上传下载文件！</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;（命令行）连接sftp服务器成功后，'help' 命令查看更多sftp使用命令。</p>
                    <p class="bottom-imgWrap"><img src='../assets/sftp-exp.png' style="width: 30rem; height: 13rem;"></p>
                </div>
                <p><i class="blue arrow right icon"></i>命令行（local）</p><p class="bottom-imgWrap"><img src='../assets/sftp-local.gif' alt=""></p>
                <p><i class="blue arrow right icon"></i>命令行（remote）</p><p class="bottom-imgWrap"><img src='../assets/sftp-host.gif' alt=""></p>
                <p><i class="blue arrow right icon"></i>工具(filezilla)</p><p class="bottom-imgWrap"><img src='../assets/sftp-filezilla.gif' alt=""></p>
                <p><span style="font-size: smaller; left:70px">（*** 其他具体使用方式请自行百度 ***）</span></p>
            </div>
            <br><br><br>
            <div class="item" id="G8">
                <h2>登录机器</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>登陆目标机器，ppe、beta和线上机器登陆方式相同。\** 直接登陆，无需输入密码.**\</p>
                </div>
                <p class="bottom-imgWrap"><img src='../assets/ssh-host.gif' alt=""></p>
            </div>
            <br><br><br>
            <div class="item" id="G9">
                <h2>sudo权限</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p><i class="blue arrow right icon"></i><span>&nbsp;前往&nbsp;&nbsp;<a href="http://ttt.dp/?#!/start/32" target="_blank">http://ttt.dp/?#!/start/32</a></span>
                        提交流程，找对应SRE审批。
                        <span style="color: red">PS：sudo权限申请成功后，最晚20分钟后生效，有效期为一天。过期请重新提交流程.</span>
                    </p>
                </div>
                <p class="bottom-imgWrap"><img src='../assets/sudo.gif' alt=""></p>
            </div>
            <br><br><br>
            <div class="item" id="G10">
                <h2>windows SecureCRT设置</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>快速连接&nbsp;&nbsp;&nbsp;<i class="blue arrow right icon"></i>&nbsp;&nbsp;&nbsp;不保存密码！
                        &nbsp;&nbsp;&nbsp;<i class="blue arrow right icon"></i>&nbsp;&nbsp;&nbsp;输入密码和验证码
                        &nbsp;&nbsp;&nbsp;<i class="blue arrow right icon"></i>&nbsp;&nbsp;&nbsp;登录成功
                    </p>
                    <p class="bottom-imgWrap"><img src='../assets/windows-secure-1.png' style="width:22rem; height: 20rem;">
                        <img src='../assets/windows-secure-2.png' style="width:22rem; height: 20rem;">
                    &nbsp;&nbsp;&nbsp;<img src='../assets/windows-secure-3.png' style="width:22rem; height: 20rem;"></p>
                </div>
            </div>
            <br><br><br>
            <div class="item" id="G11">
                <h2>常见问题及解决方法</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p style="font-weight: 800; color: black;"><i class="blue arrow right icon"></i>secureCRT 中文乱码问题</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;详细操作步骤见链接： <a href="http://jingyan.baidu.com/article/948f59245be128d80ff5f9aa.html">http://jingyan.baidu.com/article/948f59245be128d80ff5f9aa.html</a></p>
                    <br>
                    <p style="font-weight: 800; color: black;"><i class="blue arrow right icon"></i>密码错误问题</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;忘记密码?<a href="http://ttt.dp/#!/start/32" target="_blank">http://ttt.dp/#!/start/32</a> 密码重置,</p>
                    <p style="color: red"> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;输入密码和验证码示例：</p>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;密 码: 12!@Test &nbsp;&nbsp;&nbsp;验证码:  398305</p>
                     <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;输 入：12!@Test398305     ［密码和验证码间无任何字符！］</p>
                    </div>
            </div>
            <br><br><br>
            <div class="item" id="G12">
                <h2>意见反馈</h2>
                <div class="ui divider"></div>
                <div class="ui basic segment">
                    <p>更多问题与建议，请大象扫码入群~（二维码见页尾）<i class="blue pointing down icon"></i></p>
                </div>
            </div>
            <br><br>
        </div>
    </div>
</template>

<script>
    export default{
        data(){
            return{
                isToggle: true,
                active: 1,
                scrollTop: 0,
                ids: {}
            }
        },
        methods: {
            getTops() {
                for(var i=1; i <= 12; i++){
                    this.ids['#G' + i] = this.$el.querySelector('#G'+i).offsetTop;
                }
            },
            handleScroll () {
                this.scrollTop = document.body.scrollTop;
            },
            goAnchor(selector) {
                var anchor = this.$el.querySelector(selector);
                document.body.scrollTop = anchor.offsetTop + 10

            }
        },
        mounted(){
            this.getTops();
            window.addEventListener('scroll', this.handleScroll);
        },
    }
</script>

<style>
    #Content {
        left: 200px;
        max-width:85%;
        min-height: 500px;
    }
    #Content > .item > .ui.segment {
        font-weight: 400;
        color: dimgrey;
    }
    #Content > .item > .bottom-imgWrap {
        margin-left: 80px;
    }
    #Content > .item > .bottom-imgWrap > img {
        width:38rem;
        height: 28rem;
    }
    #Content > .item > .ui.divider {
        width: 600px
    }
</style>