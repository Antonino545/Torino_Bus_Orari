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
async function avvisi() {
    await axios.get('https://www.gtt.to.it/cms/index.php?option=com_gtt&view=avvisi&tmpl=raw&priorita=1').then(function (response) {
            var avvisi = response.data;
            var avvisiDiv = document.getElementById("avvisi");
            avvisiDiv.innerHTML = avvisi;
        }
    ).catch(function (error) {
        console.log(error);
    });
}

