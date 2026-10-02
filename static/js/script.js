document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("resume");
    const filename = document.getElementById("filename");

    if (input && filename) {
        input.addEventListener("change", function () {
            filename.textContent = this.files.length
                ? this.files[0].name
                : "No file selected";
        });
    }
});
