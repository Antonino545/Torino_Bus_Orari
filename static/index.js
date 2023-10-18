function init() {
    document.getElementById("stopForm").addEventListener("submit", listener);

}
//even listener
function listener(e){
        e.preventDefault();
    var stopValue = document.getElementById("stop").value;
    if (stopValue) {
        window.location.href = "fermata/" + stopValue;
    }
}
