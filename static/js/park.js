
$(document).ready(function() {
    const park_btn = document.getElementById("park_btn")
    const exit_btn = document.getElementById("exit_btn")
    const exit_sbmt = document.getElementById("exit_submit")
    const dynamic_area = document.getElementById("dynamic_wrapper")
    park_btn.addEventListener('click',function(event){
        fetch("/ticket",{method:"GET"})
        .then(response => {return response.text()})
        .then(html => {dynamic_area.innerHTML = html})
        event.preventDefault()
    })

    exit_btn.addEventListener('click',function(event){
        fetch("/exit",{method:"GET"})
        .then(response => {return response.text()})
        .then(html => {dynamic_area.innerHTML = html})
        event.preventDefault()
    })

})

function exit_submt(){
    var dynamic_area = document.getElementById("dynamic_wrapper")

    fetch("/payment",{method:"GET"})
    .then(response => {return response.text()})
    .then(html => {dynamic_area.innerHTML = html})
    .then($form.submit())
}
    
