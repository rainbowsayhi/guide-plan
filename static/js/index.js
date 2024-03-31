const chars = 'abcdefghijklmnopqrstuvwxyz';
const sign = '!&%#';
const logo = '/';

function getRandomNum() {
    return Math.floor(Math.random() * (999 - 100 + 1)) + 100;
}

function getRandomChars() {
    const length = 10;
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars[Math.floor(Math.random() * chars.length)];
    }
    return result;
}

function getTimestamp() {
    const timestamp = Date.now().toString();
    return hex_md5(timestamp);
}

function getSign() {
    return sign[Math.floor(Math.random() * sign.length)];
}

function encode(id, time_index) {
    const randomNum = getRandomNum();
    const timestamp = getTimestamp();
    const sign = getSign();
    const randomChars = getRandomChars();
    const info = `id=${id}&time=${time_index}`
    const b64_info = btoa(info);
    const string = `${randomNum}${timestamp}${sign}${logo}${b64_info}${logo}${randomChars}`;
    return btoa(string);
}

new Vue({
    el: '.body-content',
    data: {
        course_periods: null,
        course_time: null,
        student_choice_courses_list: null,
        course_stock: null,
        is_login: null
    },
    delimiters: ['{$', '$}'],
    created() {
        this.init_index_page();
    },
    methods: {
        init_index_page() {
            request({
                url: '/api/index',
                method: 'get'
            }).then((res) => {
                var data = res.data;
                this.course_periods = data.course_periods;
                this.course_time = data.course_time;
                this.student_choice_courses_list = data.student_choice_courses_list;
                this.course_stock = data.course_stock;
                this.is_login = data.is_login;
            }).catch((errmsg) => {
                alert(`请求异常${errmsg}`);
            })
        },
        choice_course(course_id) {
            this.$confirm('是否选择该课程？', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }).then(() => {
                const loading = this.$loading({
                    lock: true,
                    text: '排队选课中……',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                request({
                    url: '/api/course',
                    method: 'post',
                    data: {
                        secret: encode(course_id, this.course_time.index)
                    }
                }).then(res => {
                    loading.close();
                    if(res.data.success) {
                        new_alert.my_alert('选课成功，手动刷新页面以显示操作结果。', 'success');
                    }
                    else {
                        new_alert.my_alert(res.data.errmsg, 'error');
                    }
                }).catch((errmsg) => {
                    loading.close();
                    alert(`请求异常${errmsg}`);
                })
            })
        },
        quit_course(course_id) {
            this.$confirm('是否退掉该课程？', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                request({
                    url: '/api/course',
                    method: 'delete',
                    data: {
                        secret: encode(course_id, this.course_time.index)
                    }
                }).then(res => {
                    if(res.data.success) {
                        new_alert.my_alert('退课成功，手动刷新页面以显示操作结果。', 'success');
                    }
                    else {
                        new_alert.my_alert(res.data.errmsg, 'error');
                    }
                }).catch((errmsg) => {
                    alert(`请求异常${errmsg}`);
                })
            })
        },
    }
})
// const chars = 'abcdefghijklmnopqrstuvwxyz';
// const sign = '!&%#';
// const logo = '/';

// function getRandomNum() {
//     return Math.floor(Math.random() * (999 - 100 + 1)) + 100;
// }

// function getRandomChars() {
//     const length = 10;
//     let result = '';
//     for (let i = 0; i < length; i++) {
//       result += chars[Math.floor(Math.random() * chars.length)];
//     }
//     return result;
// }

// function getTimestamp() {
//     const timestamp = Date.now().toString();
//     return hex_md5(timestamp);
// }

// function getSign() {
//     return sign[Math.floor(Math.random() * sign.length)];
// }

// function encode(id, time_index) {
//     const randomNum = getRandomNum();
//     const timestamp = getTimestamp();
//     const sign = getSign();
//     const randomChars = getRandomChars();
//     const info = `id=${id}&time=${time_index}`
//     const b64_info = btoa(info);
//     const string = `${randomNum}${timestamp}${sign}${logo}${b64_info}${logo}${randomChars}`;
//     return btoa(string);
// }

// new Vue({
//     el: '.body-content',
//     data: {
//         course_periods: null,
//         course_time: null,
//         student_choice_courses_list: null,
//         course_stock: null,
//         is_login: null
//     },
//     delimiters: ['{$', '$}'],
//     created() {
//         this.init_index_page();
//     },
//     methods: {
//         init_index_page() {
//             request({
//                 url: '/api/index',
//                 method: 'get'
//             }).then((res) => {
//                 var data = res.data;
//                 this.course_periods = data.course_periods;
//                 this.course_time = data.course_time;
//                 this.student_choice_courses_list = data.student_choice_courses_list;
//                 this.course_stock = data.course_stock;
//                 this.is_login = data.is_login;
//             }).catch((errmsg) => {
//                 alert(`请求异常${errmsg}`);
//             })
//         },
//         choice_course(course_id) {
//             this.$confirm('是否选择该班级？', '提示', {
//                 confirmButtonText: '确定',
//                 cancelButtonText: '取消',
//                 type: 'warning',
//             }).then(() => {
//                 const loading = this.$loading({
//                     lock: true,
//                     text: '正在排队……',
//                     spinner: 'el-icon-loading',
//                     background: 'rgba(0, 0, 0, 0.7)'
//                 });
//                 request({
//                     url: '/api/course',
//                     method: 'post',
//                     data: {
//                         secret: encode(course_id, this.course_time.index)
//                     }
//                 }).then(res => {
//                     loading.close();
//                     if(res.data.success) {
//                         new_alert.my_alert('选择成功，手动刷新页面以显示操作结果。', 'success');
//                     }
//                     else {
//                         new_alert.my_alert(res.data.errmsg, 'error');
//                     }
//                 }).catch((errmsg) => {
//                     loading.close();
//                     alert(`请求异常${errmsg}`);
//                 })
//             })
//         },
//         quit_course(course_id) {
//             this.$confirm('是否退出该班级（该操作可能不可逆，是否继续？）', '提示', {
//                 confirmButtonText: '确定',
//                 cancelButtonText: '取消',
//                 type: 'warning'
//             }).then(() => {
//                 request({
//                     url: '/api/course',
//                     method: 'delete',
//                     data: {
//                         secret: encode(course_id, this.course_time.index)
//                     }
//                 }).then(res => {
//                     if(res.data.success) {
//                         new_alert.my_alert('退出成功，手动刷新页面以显示操作结果。', 'success');
//                     }
//                     else {
//                         new_alert.my_alert(res.data.errmsg, 'error');
//                     }
//                 }).catch((errmsg) => {
//                     alert(`请求异常${errmsg}`);
//                 })
//             })
//         },
//     }
// })
