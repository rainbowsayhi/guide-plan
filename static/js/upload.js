var datas = JSON.parse(document.getElementById('history_datas').textContent)
new Vue({
    el: '#app',
    data: {
        fileList: [],
        count: 0,
        upload_history: datas
    },
    computed: {
        query_file_title() {
            if(this.fileList.length > 0) {
                return this.fileList[0].name;
            }
        },
    },
    methods: {
        exceed() {
            new_alert.my_alert('超出文件添加数量范围', 'error');
        },
        add_file(file, fileList) {
            if(file.size > 104857600) {
                new_alert.my_alert('文件大小不能超过100MB。', 'error');
                return
            }
            this.fileList = fileList;
            this.count++;
            new_alert.my_alert('文件添加成功！', 'success');
        },
        submit_homework() {
            if (this.fileList.length == 0) {
                new_alert.my_alert('请先添加文件再提交', 'error');
                return;
            }
            var formData = new FormData();
            formData.append("homework", this.fileList[0].raw);
            const loading = this.$loading({
                lock: true,
                text: '正在上传文件，请稍后……',
                spinner: 'el-icon-loading',
                background: 'rgba(0, 0, 0, 0.7)'
            });
            request({
                url: '/user/upload',
                method: 'post',
                data: formData
            }).then((res) => {
                loading.close();
                if (res.data.success) {
                    new_alert.my_alert('作业提交成功！', 'success');
                    setTimeout(() => {
                        location.reload()
                    }, 2000)
                } else {
                    new_alert.my_alert(res.data.errmsg, 'error');
                }
            }).catch((errmsg) => {
                loading.close();
                alert(errmsg)
            })
        },
        delete_homework(row) {
            this.$confirm('是否撤销该文件？（该操作不可逆）', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }).then(() => {
                const loading = this.$loading({
                    lock: true,
                    text: '正在撤销文件，请稍后……',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                request({
                    url: '/user/upload',
                    method: 'delete',
                    data: {
                        id: row.id
                    }
                }).then((res) => {
                    loading.close();
                    if(res.data.success) {
                        new_alert.my_alert('文件撤销成功！', 'success');
                        setTimeout(() => {
                            location.reload()
                        }, 2000)
                    } else {
                        new_alert.my_alert(res.data.errmsg, 'error');
                    }
                }).catch((errmsg) => {
                    loading.close();
                    alert(errmsg);
                })
            })
        }
    }
})

