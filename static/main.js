
const imageFileField = document.getElementById('image_file');
const scalingFactor = document.getElementById('sf');
const pixelLevity = document.getElementById('pl')

const token = document.getElementById('csrf_token');
const display = document.querySelector('.canvas');

const data = new FormData()
data.append('scaling_factor', scalingFactor.value * 0.01);
data.append('pixel_levity', pixelLevity.value * 0.02);
data.append('csrf_token', token.value);

const postForm = () => {
    fetch('/', { method: 'POST', body: data })
        .then(response => response.json())
        .then(response => {
            const imageURL = response.image_url;
            const session = response.session;
            const time = new Date().getTime();
            data.append('session', session);
            display.style.backgroundImage = `url("${imageURL + '?rand=' + time}") no-repeat`;
        })
        .catch((err) => {
            console.log(err);
        });
};

imageFileField.addEventListener('change', (e) => {
    data.append('image_file', e.target.files[0]);
    postForm();
});

scalingFactor.addEventListener('input', (e) => {
    const scale = 0.01;
    data.set('scaling_factor', e.target.value * scale);
    if (data.image_file || data.get('session')) {
        postForm();
    }
})

pixelLevity.addEventListener('input', (e) => {
    const scale = 0.02;
    data.set('pixel_levity', e.target.value * scale);
    if (data.image_file || data.get('session')) {
        postForm();
    }
})
