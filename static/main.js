
Vue.use(VueLoading);

var vue = new Vue({
    el: '#display',
    delimiters: ['[[', ']]'],
    data: function() {
        return {
            imageFile: null,
            csrfToken: '',
            scalingFactor: 0.5,
            imageURL: null,
            background: '',
            blob: null,
        }
    },
    mounted: function() {
        this.csrfToken = document.getElementById('csrf_token').value;
        var self = this;
        document.getElementById('image_file').addEventListener('change', function(e) {
            self.imageFile = e.target.files[0];
            self.imageURL = URL.createObjectURL(self.imageFile);
        });
        document.getElementById('scaling_factor').addEventListener('input', function(e) {
            self.scalingFactor = e.target.value * 0.01;
        });
    },
    methods: {
        postImage: function() {
            var loader = this.$loading.show({
                container: null,
                canCancel: false,
            });
            var data = new FormData()
            data.append('csrf_token', this.csrfToken);
            data.append('scaling_factor', this.scalingFactor);
            data.append('image_file', this.imageFile);

            var self = this;
            fetch('/', { method: 'POST', body: data })
            .then(response => response.blob())
            .then(blob => {
                self.imageURL = URL.createObjectURL(blob);
                loader.hide();
            })
            .catch((err) => {
                loader.hide();
                alert('An error has occurred');
            });
        },
    },
    watch: {
        imageURL: function() {
            if (!this.imageURL) return;
            this.background = {
                backgroundImage: `url(${this.imageURL})`,
            }
        },
    },
});
