var infos = JSON.parse(document.getElementById('infos').textContent);
let emailRegex = /.{4,20}@(qq|163|126|gmail|sina|hotmail|icould|foxmail)\.com/;
let phoneRegex = /1\d{10}/;
new Vue({
    el: '#app',
    data: {
        name: infos.name,
        no: infos.no,
        major: infos.major,
        stu_class: infos.stu_class,
        college: infos.college,
        email: infos.email,
        gender: infos.gender,
        phone: '',
        colleges: infos.colleges,
    },
    computed: {
        can_be_submit() {
            if(this.name && this.major && this.stu_class && this.college
                && emailRegex.test(this.email) && phoneRegex.test(this.phone)) {
                return 1;
            } else {
                return 0;
            }
        }
    },
    methods: {
        commit_info() {
            if (!(this.name && this.major && this.stu_class && this.college && this.email && this.gender && this.phone)) {
                new_alert.my_alert('信息不完整', 'error')
                return;
            }
            if (!emailRegex.test(this.email)) {
                new_alert.my_alert('邮箱格式不正确', 'error')
                return;
            }
            if(!phoneRegex.test(this.phone)) {
                new_alert.my_alert('手机号格式不正确', 'error');
                return;
            }
            request({
                url: '/user/modify',
                method: 'put',
                data: {
                    name: this.name,
                    major: this.major,
                    stu_class: this.stu_class,
                    college: this.college,
                    email: this.email,
                    gender: this.gender,
                    phone: this.phone
                }
            }).then(res => {
                if (res.data.success) {
                    new_alert.my_alert('信息修改成功，页面跳转中……', 'success')
                    setTimeout(() => {
                        window.location = '/user'
                    }, 2000);
                } else {
                    new_alert.my_alert(res.data.errmsg, 'error')
                }
            }).catch((errmsg) => {
                alert(`请求异常${errmsg}`)
            })
        }
    }
})
