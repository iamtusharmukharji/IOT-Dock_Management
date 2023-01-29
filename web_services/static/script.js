
function stream_data(){

    var eventSource = new EventSource("/stream")
    var dock_count_display = document.getElementById("dock_count");
    eventSource.onmessage = function (e) {

        var json_data = JSON.parse(e.data);
        var dock_count = 1;
        
        for (let dock in json_data.payload) {
            
            var status = json_data.payload[dock];

            var dock_div = document.getElementById(dock);
            
            if (dock_div == null){
                var dock_div = document.createElement("div");
                dock_div.className = "dock";
                dock_div.id = dock;
                dock_div.innerHTML = "Dock "+String(dock_count);
                document.getElementById("main").appendChild(dock_div);}

            
            if (status == 1) {
                dock_div.style.backgroundColor = "red";}
            else {
                dock_div.style.backgroundColor = "green";}
                
            dock_count+=1
            }
        dock_count_display.innerHTML = "Active Docks: "+String(dock_count-1);

    }
}