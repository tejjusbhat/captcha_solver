function previewImage(file) {
  const reader = new FileReader();

  reader.onload = function () {
    const preview = document.getElementById("preview");
    preview.src = reader.result;
  };

  reader.readAsDataURL(file);
}

function dragOverHandler(event) {
  event.preventDefault();
  event.dataTransfer.dropEffect = "copy";
}

function dropHandler(event) {
  event.preventDefault();
  const files = event.dataTransfer.files;
  const imageInput = document.getElementById("image-input");
  imageInput.files = files;
  previewImage(files[0]);
}

document.getElementById('image-input').addEventListener('change', function (event) {
  const file = event.target.files[0];
  if (file) {
      previewImage(file);
  }
});

function processImage() {
  const fileInput = document.getElementById("image-input");
  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onload = function (event) {
    const image = event.target.result.split(",")[1];
    const target = document.getElementById("target-select").value;
    fetch("/process_image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image: image,
        target: target,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const annotated_image = document.getElementById("preview");
        annotated_image.src = `data:image/jpeg;base64,${data.annotated_image}`;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  reader.readAsDataURL(file);
}
