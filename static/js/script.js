function changeScreen(screen) {
    fetch(`/change_screen/${screen}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log(`Changed to ${screen} screen`);
            } else {
                console.error('Error:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));
}

function uploadPhoto() {
    const fileInput = document.getElementById('photo-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Veuillez sélectionner une photo');
        return;
    }

    const formData = new FormData();
    formData.append('photo', file);

    fetch('/upload_photo', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Photo téléchargée avec succès');
            fileInput.value = '';
        } else {
            alert('Erreur lors du téléchargement');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors du téléchargement');
    });
} 