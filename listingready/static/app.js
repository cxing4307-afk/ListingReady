const input = document.querySelector("#images");
const zone = document.querySelector("#drop-zone");
const summary = document.querySelector("#file-summary");
const prefix = document.querySelector("#prefix");
const preview = document.querySelector("#name-preview");

function updateSummary() {
  const count = input.files.length;
  summary.textContent = count ? `${count} photo${count === 1 ? "" : "s"} ready` : "No photos selected";
}

input.addEventListener("change", updateSummary);
prefix.addEventListener("input", () => {
  preview.textContent = `${prefix.value.trim() || "myshop"}-001.jpg`;
});

for (const eventName of ["dragenter", "dragover"]) {
  zone.addEventListener(eventName, (event) => {
    event.preventDefault();
    zone.classList.add("is-over");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  zone.addEventListener(eventName, (event) => {
    event.preventDefault();
    zone.classList.remove("is-over");
  });
}

zone.addEventListener("drop", (event) => {
  input.files = event.dataTransfer.files;
  updateSummary();
});

// TODO: Let users remove one mistaken file without reopening the picker.
