people_range = document.getElementById("people_range");
people_result = document.getElementById("people_result");

people_range.addEventListener("input", function () {
    people_result.innerHTML = people_range.value;
})

days_range = document.getElementById("days_range");
days_result = document.getElementById("days_result");

days_range.addEventListener("input", function () {
    days_result.innerHTML = days_range.value;
})
