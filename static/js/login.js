new Vue({
    el: '.main',
    methods: {
        login() {
            let stuid = document.getElementById('stuid').value
            let pwd = document.getElementById('pwd').value
            if (!(stuid && pwd)) {
                new_alert.my_alert('数据不完整', 'error');
                return
            }
            if (pwd.length < 6) {
                new_alert.my_alert('密码必须大于6位数', 'error');
                return
            }
            request({
                url: '/user/login',
                method: 'post',
                data: {
                    stuid: stuid,
                    pwd: pwd
                }
            }).then(res => {
                if(res.data.success) {
                    new_alert.my_alert('登录成功，页面正在跳转……', 'success');
                    setTimeout(() => {
                        var url = location.href;
                        window.location = url.split('?')[1] ? url.split('?')[1].split('=')[1]: '/user';
                    }, 2000)
                }
                else {
                    new_alert.my_alert(res.data.errmsg, 'error');
                }
            }).catch((error) => {
                alert(`请求异常${error}`)
            })
        }
    }
})
