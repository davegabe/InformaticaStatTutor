// Select the input element using
// document.querySelector
var input = document.querySelector(
    "#file-with-js>.file-label>.file-input"
);

// Bind an listener to onChange event of the input
input.onchange = function () {
    if (input.files.length > 0) {
        var fileNameContainer =
            document.querySelector(
                "#file-with-js>.file-label>.file-name"
            );
        // set the inner text of fileNameContainer
        // to the name of the file
        fileNameContainer.textContent =
            input.files[0].name;
    }
};