document.getElementById('fetch-btn').addEventListener('click', async () => {
    const url = document.getElementById('url-input').value;
    const formatsContainer = document.getElementById('formats-container');
    formatsContainer.innerHTML = 'Loading formats...';

    try {
        const response = await fetch('/get_formats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();

        if (data.status === 'success') {
            const videoFormats = data.video_formats;
            const audioFormats = data.audio_formats;

            let html = '<h3>Video Formats</h3>';
            videoFormats.forEach(fmt => {
                html += `<button onclick="selectFormat('${fmt.format_id}')">${fmt.resolution} ${fmt.ext} ${fmt.has_audio ? '🔊' : '🔇'}</button>`;
            });

            html += '<h3>Audio Formats</h3>';
            audioFormats.forEach(fmt => {
                html += `<button onclick="selectFormat('${fmt.format_id}')">${fmt.ext}</button>`;
            });

            formatsContainer.innerHTML = html;
            document.getElementById('download-btn').disabled = false;
        } else {
            formatsContainer.innerHTML = data.message;
        }
    } catch (err) {
        formatsContainer.innerHTML = 'Error fetching formats!';
    }
});

function selectFormat(format) {
    sessionStorage.setItem('selectedFormat', format);
}

document.getElementById('download-btn').addEventListener('click', async () => {
    const url = document.getElementById('url-input').value;
    const quality = sessionStorage.getItem('selectedFormat');

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, quality })
        });
        const data = await response.json();

        if (data.status === 'success') {
            window.location.href = data.download_link;
        } else {
            alert(data.message);
        }
    } catch (err) {
        alert('Error downloading file!');
    }
});
      
