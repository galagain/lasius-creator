var socket = io();

// Listen for log messages specific to this session
socket.on("log_message", function (data) {
  var logs = document.getElementById("logs");
  logs.classList.remove("hidden"); // Ensure the logs section is visible
  logs.innerHTML += data.message + "<br>"; // Append the new log message
  logs.scrollTop = logs.scrollHeight; // Scroll to the bottom of the log container
});

function generateJson() {
  const form = document.getElementById("jsonForm");
  const formData = new FormData(form);

  // Append the socket ID (sid) to the form data
  formData.append("sid", socket.id);

  // Send the form data to the server to generate JSON, including the sid in the request
  fetch(`/generate_json?sid=${socket.id}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Error generating JSON"); // Alert the user if there was an error
      } else {
        // Populate the hidden input with the generated JSON data
        document.getElementById("jsonval").value = data.json_data;
        // Set the filename for the download, replacing spaces with underscores
        const title = document.getElementById("title").value.replace(/ /g, "_");
        document.getElementById("filename").value = title + ".json";
        // Make the download form visible
        document.getElementById("downloadForm").classList.remove("hidden");
      }
    })
    .catch((error) => console.error("Error:", error)); // Log any errors that occur
}

function setDownloadFilename() {
  // Set the filename for the JSON download based on the title input value
  const title = document.getElementById("title").value.replace(/ /g, "_");
  const filename = title + ".json";
  // Set the action attribute for the download form to include the filename
  document.getElementById("downloadForm").action =
    "/download_json?filename=" + filename;
}

function fillExample1() {
  // Pre-fill the form with example queries and settings for "Semantic SLAM"
  document.getElementById("queries").value =
    "visual dynamic SLAM, visual semantic SLAM, semantic aware dynamic SLAM, semantic SLAM for embedded system";
  document.getElementById("total_papers").value = 200;
  document.getElementById("title").value = "Semantic SLAM";
}

function fillExample2() {
  // Pre-fill the form with example queries and settings for "NeRF SLAM"
  document.getElementById("queries").value =
    "NERF SLAM, Neural Radiance Fields SLAM";
  document.getElementById("total_papers").value = 200;
  document.getElementById("title").value = "NeRF SLAM";
}
