
const imageFileField = document.getElementById('image_file');
const rangeWidthField = document.getElementById('range_width');
const desiredWidthField = document.getElementById('desired_width');
const token = document.getElementById('csrf_token');

const output = document.getElementById('output');

const data = new FormData()
data.append('range_width', rangeWidthField.value);
data.append('desired_width', desiredWidthField.value);
data.append('csrf_token', token.value);

const postForm = () => {
    fetch('/', { method: 'POST', body: data })
        .then(response => response.json())
        .then(response => {
            const imageText = response.image_text;
            const session = response.session;
            data.append('session', session);
            output.innerHTML = imageText;
        })
        .catch((err) => {
            output.innerHTML = 'An error has occurred';
            console.log(err)
        });
};


imageFileField.addEventListener('change', (e) => {
    data.append('image_file', e.target.files[0]);
    postForm();
});

rangeWidthField.addEventListener('change', (e) => {
    data.set('range_width', e.target.value);
    if (data.image_file || data.get('session')) {
        output.innerHTML = ''
        postForm();
    }
});

desiredWidthField.addEventListener('change', (e) => {
    data.set('desired_width', e.target.value);
    if (data.image_file || data.get('session')) {
        output.innerHTML = ''
        postForm();
    }
});
