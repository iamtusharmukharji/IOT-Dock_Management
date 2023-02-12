var lastClick = 0;
var delay = 1000;



function stream_data(){

    var eventSource = new EventSource("/stream")
    var dock_count_display = document.getElementById("dock_count");
    eventSource.onmessage = function (e) {

        var json_data = JSON.parse(e.data);
        var device_id = json_data.device_id;
        var dock_count = 1;
        
        for (let dock in json_data.payload) {
            
            var status = json_data.payload[dock];

           

            var dock_div = document.getElementById(dock);
            
            if (dock_div == null){
                var dock_div = document.createElement("div");
                dock_div.className = "dock";
                dock_div.id = dock;
                dock_div.innerHTML = "Dock "+dock.charAt(dock.length-1);
                dock_div.addEventListener("click", function(){
                    
                    dock_control(device_id, dock);
                });

                document.getElementById("main").appendChild(dock_div);
            }

            
            if (status == 1) {
                dock_div.style.backgroundColor = "#bf604d";}
            else if(status == -1){

                dock_div.style.backgroundColor = "#b0aaa5";
                
            }
            else {
                dock_div.style.backgroundColor = "#66b367";}
            
            
            
            dock_count+=1
            }
        dock_count_display.innerHTML = "Active Docks: "+String(dock_count-1);

    }
}

async function dock_control(device_id, dock){
    if (lastClick >= (Date.now() - delay)){
        return;
    }
    lastClick = Date.now();
    var status = document.getElementById(dock);
    console.log(status.style.backgroundColor);

    if (status.style.backgroundColor == "rgb(176, 170, 165)"){
        var alert_msg = "Are you sure to ENABLE the dock ?"
        var data = {"device_id":device_id, "dock": dock, "state": "enable"};
    }
    else{
        var alert_msg = "Are you sure to DISABLE the dock ?"
        var data = {"device_id":device_id, "dock": dock, "state": "disable"};
    }
    
    if (confirm(alert_msg)){
        console.log(data);
        await fetch('/dockcontrol/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
        cache: 'default'
        })
    }
}