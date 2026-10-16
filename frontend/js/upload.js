const uploadForm = document.getElementById("uploadForm");
const documentFile = document.getElementById("documentFile");
const uploadStatus = document.getElementById("uploadStatus");

uploadForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const file = documentFile.files[0];

    if (!file) {
        uploadStatus.innerText = "Please select a document.";
        return;
    }


    const formData = new FormData();

    formData.append("file", file);


    uploadStatus.innerText = "Analyzing document...";


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/upload",
            {
                method: "POST",
                body: formData
            }
        );


        const result = await response.json();


        if (!response.ok) {

            uploadStatus.innerText =
                result.detail || "Document analysis failed.";

            return;
        }


        sessionStorage.setItem(
            "analysisResult",
            JSON.stringify(result)
        );


        window.location.href = "dashboard.html";


    } catch (error) {

        console.error(error);

        uploadStatus.innerText =
            "Unable to connect to the Law2Life AI server.";

    }

});