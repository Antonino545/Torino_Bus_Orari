function init() {
    document.getElementById("stopForm").addEventListener("submit", listener);

}
//even listener
function listener(e){
        e.preventDefault();
    const stopValue = document.getElementById("stop").value;
    const lineValue = document.getElementById("line").value;
    if (lineValue&&stopValue) {
        window.location.href = "fermata/" + stopValue + "/" + lineValue;
    }
    else if (stopValue) {
        window.location.href = "fermata/" + stopValue;
    }
}
