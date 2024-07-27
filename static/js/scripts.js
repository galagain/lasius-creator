var socket = io();

socket.on("log_message", function (data) {
  var logs = document.getElementById("logs");
  logs.classList.remove("hidden");
  logs.innerHTML += data.message + "<br>";
  logs.scrollTop = logs.scrollHeight;
});

function generateJson() {
  const form = document.getElementById("jsonForm");
  const formData = new FormData(form);
  fetch("/generate_json", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Error generating JSON");
      } else {
        document.getElementById("jsonval").value = data.json_data;
        const title = document.getElementById("title").value.replace(/ /g, "_");
        document.getElementById("filename").value = title + ".json";
        document.getElementById("downloadForm").classList.remove("hidden");
      }
    })
    .catch((error) => console.error("Error:", error));
}

function setDownloadFilename() {
  const title = document.getElementById("title").value.replace(/ /g, "_");
  const filename = title + ".json";
  document.getElementById("downloadForm").action = "/download_json?filename=" + filename;
}

function fillExample1() {
  document.getElementById("queries").value =
    "visual dynamic SLAM, visual semantic SLAM, semantic aware dynamic SLAM, semantic SLAM for embedded system";
  document.getElementById("total_papers").value = 200;
  document.getElementById("title").value = "Semantic SLAM";
}

function fillExample2() {
  document.getElementById("queries").value =
    "NERF SLAM, Neural Radiance Fields SLAM";
  document.getElementById("total_papers").value = 200;
  document.getElementById("title").value = "NeRF SLAM";
}
