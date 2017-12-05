var Vue = require('vue');
exports.user = Vue.resource('/api/user');
exports.user_my = Vue.resource('/api/user/my');
exports.cmdb = Vue.resource('/api/cmdb');


//User
exports.delUser = Vue.resource('/api/user');                        // DELETE 批量删除用户
exports.getUser = Vue.resource('/api/web/user');                    // GET  查询用户
exports.updateUser = Vue.resource('/api/user/{id}');                // PUT  禁用账号，修改source， role
exports.syncUser = Vue.resource('/api/user/sync');                  // PUT  校准企业系统信息
exports.unlockUser = Vue.resource('/api/user/unlocking');           // PUT  解锁账号
exports.resetPassword = Vue.resource('/api/user/reset/password');   // POST 重置密码
exports.userRelate = Vue.resource('/api/user/relate/{uid}');        // GET 获取用户所在组列表，sudo，权限


// Group [save 增加组(可携带用户)],[get 查询组],[update 更新组], [delete 删除组]
exports.group = Vue.resource('/api/group');
exports.member_detail = Vue.resource('/api/group/detail/{id}');  // GET 展示组员相关信息


exports.web_user = Vue.resource('/api/user/web/{id}');
exports.user_admin = Vue.resource('/api/jumper/user');
exports.get_login_history = Vue.resource('/api/jumper/login_history');
exports.get_all_history = Vue.resource('/api/history');

//Sudo
exports.sudo = Vue.resource('/api/sudo');
exports.sudo_admin = Vue.resource('/api/sudo/{id}');
exports.sh_add_sudo = Vue.resource('/api/sh/sudo');

//Home
exports.get_top_users = Vue.resource('/api/user/top');
exports.monitor = Vue.resource('/api/monitor?smoke=true');

//workflow
exports.reset = Vue.resource('/api/user/reset/password');

//ttt
exports.my_mark = Vue.resource('/api/mark/my');

//terminal
exports.get_uuid = Vue.resource('/api/web/code');

//file
exports.file_upload = Vue.resource('/api/file/upload');
