document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = document.getElementById('file').files[0];
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/uploadfile/', {
        method: 'POST',
        body: formData,
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
    });

    const result = await response.json();
    document.getElementById('result').innerHTML = `<a href="${result.file_url}">Download Processed File</a>`;
});

async function login() {
    const response = await fetch('/auth/login', {
        method: 'POST',
        body: new URLSearchParams({
            'username': 'user1',
            'password': 'password1'
        })
    });
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
}

login();
