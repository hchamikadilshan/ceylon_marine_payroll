console.log("Workingggg");
//Get employee name
var attendance_emp_id_input = document.getElementById("attendance_emp_id");
var attendance_emp_id_input_data_url = attendance_emp_id_input.data-url
console.log(attendance_emp_id_input_data_url)
attendance_emp_id_input.addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    attendance_emp_id = attendance_emp_id_input.value;


    $.ajax({url: "demo_test.txt", success: function(result){
    $("#div1").html(result);
  }});
  }
});

//Get Dates according to the month

function getYearMonth(){
    var attendance_month_year_select = document.getElementById("attendance_month_year");
    var attendance_month_date = attendance_month_year_select.value;
    var attendance_month_date_split = attendance_month_date.split('-');
    var attendance_year = attendance_month_date_split[0];
    var attendance_month = attendance_month_date_split[1];
    var attendance_set_date = attendance_year+"-"+attendance_month+"-01"
    document.getElementById("attendance_date").defaultValue = attendance_set_date;
    var attendance_date = new Date(document.getElementById("attendance_date").value);
    var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    var dayName = days[attendance_date.getDay()];
    document.getElementById("attendance_day").value = dayName;
}
function getAllDaysInMonth(year, month) {
  const date = new Date(year, month, 1);

  const dates = [];

  while (date.getMonth() === month) {
    dates.push(new Date(date));
    date.setDate(date.getDate() + 1);
  }

  return dates;
}




