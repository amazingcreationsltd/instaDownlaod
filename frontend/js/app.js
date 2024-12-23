// frontend/js/app.js
async function downloadFile(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        
        // Create download link
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename || 'instagram-download';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        a.remove();
    } catch (error) {
        console.error('Download failed:', error);
    }
}

// Update the displayResult function
function displayResult(data) {
    result.innerHTML = `
        <div class="bg-white p-4 rounded shadow">
            <img src="${data.url}" alt="Downloaded content" class="max-w-full">
            <div class="mt-4">
                <button onclick="downloadFile('${data.url}', 'instagram-content')" 
                        class="bg-green-500 text-white px-4 py-2 rounded">
                    Download to My Computer
                </button>
            </div>
        </div>
    `;
    result.classList.remove('hidden');
}