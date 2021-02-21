
Vue.use(VueLoading);
var Chrome = window.VueColor.Compact

var vue = new Vue({
    el: '#display',
    delimiters: ['[[', ']]'],
    components: {
        'color-picker': Chrome,
    },
    data: function() {
        return {
            imageFile: null,
            scalingFactor: 0.5,
            imageURL: null,
            background: '',
            blob: null,
            firstColor: {
                hex: '#000000'
            },
            secondColor: {
                hex: '#000000'
            },
            firstPickerToggled: false,
            secondPickerToggled: false,
        }
    },
    mounted: function() {
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
            data.append('scaling_factor', this.scalingFactor);
            data.append('image_file', this.imageFile);
            data.append('from_color', this.firstColor.hex);
            data.append('to_color', this.secondColor.hex);

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
        pickColor: function(id) {
            if (id === 0) {
                this.firstPickerToggled = !this.firstPickerToggled;
            } else {
                this.secondPickerToggled = !this.secondPickerToggled;
            }
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
