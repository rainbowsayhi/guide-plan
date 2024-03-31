var emailRegex = /.{5,20}@(qq|163|126|gmail|sina|hotmail|icould|foxmail)\.com/;
new Vue({
    el: '#app',
    data: {
        email: '',
        code: '',
        new_pwd1: '',
        new_pwd2: '',
    },
    computed: {
        can_be_submit() {
            if(emailRegex.test(this.email) && this.code && this.new_pwd1 && this.new_pwd2) {
                return 1;
            } else {
                return 0;
            }
        },
    },
    methods: {
        modify_button_content() {
            var sendElement = document.getElementById('send')
            sendElement.className = "el-button el-button--primary is-disabled";
            sendElement.disabled = true;

            var count = 59;

            const timer = setInterval(() => {
                sendElement.textContent = `${count}秒`;
                count -= 1;
            }, 1000);

            setTimeout(() => {
                clearInterval(timer);
                sendElement.className = "el-button el-button--primary";
                sendElement.disabled = false;
                sendElement.textContent = '发送';
            }, 60000);
        },
        send_code() {
            if (!this.email) {
                new_alert.my_alert('请输入邮箱', 'error');
                return;
            }
            if (!emailRegex.test(this.email)) {
                new_alert.my_alert('邮箱格式不正确', 'error');
                return;
            }
            request({
                url: '/api/code',
                method: 'post',
                data: {
                    email: this.email
                }
            }).then(res => {
                if (res.data.success) {
                    this.modify_button_content();
                    new_alert.my_alert('验证码发送成功，请前往对应邮箱查看', 'success');
                } else {
                    new_alert.my_alert(res.data.errmsg, 'error')
                }
            }).catch((errmsg) => {
                alert(`请求异常${errmsg}`)
            })
        },
        commit_info() {
            if (!(this.email && this.code && this.new_pwd1 && this.new_pwd2)) {
                new_alert.my_alert('信息不完整', 'error');
                return;
            }
            if (this.new_pwd1 != this.new_pwd2) {
                new_alert.my_alert('两次密码输入不一致', 'error');
                return;
            }
            if (this.new_pwd1.length < 6) {
                new_alert.my_alert('密码位数必须大于6位', 'error');
                return;
            }
            request({
                url: '/user/change-password',
                method: 'put',
                data: {
                    code: this.code,
                    new_pwd1: this.new_pwd1,
                    new_pwd2: this.new_pwd2
                }
            }).then(res => {
                if (res.data.success) {
                    new_alert.my_alert('密码修改成功，请重新登录……', 'success')
                    setTimeout(() => {
                        window.location = '/user'
                    }, 2000)
                } else {
                    new_alert.my_alert(res.data.errmsg, 'error')
                }
            }).catch((errmsg) => {
                alert(`请求异常${errmsg}`)
            })
        }
    }
})
