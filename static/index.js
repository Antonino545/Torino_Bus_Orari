function init() {
    document.getElementById("stopForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var stopValue = document.getElementById("stop").value;
    if (stopValue) {
        window.location.href = "fermata/" + stopValue;
    }
});

}

