// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

// Check if session cookie is present
let re = new RegExp('(?<=session=)[^ ;]+');
var session_token = document.cookie.toString().match(re);
if (session_token !== null){
    $('.loginBtn').css('display', 'none');
    $('.createTalent').css('display', 'block');
    $('.manageBillBtn').css('display', 'block');
    $('.logoutBtn').css('display', 'block');
}

//LOGOUT
const logoutBtn = document.querySelector('.logoutBtn');
logoutBtn.addEventListener('click', function (e) {
    e.preventDefault();
    fetch('/dev/api/logout', {
        method: 'POST',
        credentials: "include",
    })
        .then((response) => response.json())
        .then((json) => { return json.data })
        .then((data) => {
            window.location.href = "/dev/Index.html"
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});

//MANAGE BILLING
const manageBillBtn = document.querySelector('.manageBillBtn');
manageBillBtn.addEventListener('click', function (e) {
    e.preventDefault();
    fetch('/dev/api/manage-billing', {
        method: 'POST',
        credentials: "include",
    })
        .then((response) => response.json())
        .then((json) => { return json.data })
        .then((data) => {
            window.location.href = data.url;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});

$("#submitTalent").click((e) => { 
    e.preventDefault(); 
 
    var file = document.getElementById('formFile').files[0] + ''; 
    var str64 = file.split(','); 
    // console.log(str64)[1]; 
    var talentName = document.getElementById("formName").value; 
    var talentBio = document.getElementById("formBio").value; 
    let $result = $("#result"); 
    if (str64 !== undefined || talentName !== undefined || talentBio !== undefined) { 
        let formData = new FormData(); 
        formData.append("photo", str64);
        formData.append("talentName", talentName);
        formData.append("talentBio", talentBio);
        // var object = {}; 
        // for (var value of formData.values()) { 
        //     console.log(value); 
        // } 
 
        var jsonForm = JSON.stringify(Object.fromEntries(formData)); 
        console.log("jsonForm: " + jsonForm); 
        // fetch('/dev/api/uploadImage', { 
        //     method: 'POST', 
        //     headers: { 
        //         'Content-Type': 'application/json' 
        //     }, 
        //     credentials: "include", 
        //     body: JSON.stringify({ 
        //         talentName: talentName, 
        //         talentBio: talentBio, 
        //         file: base64File 
        //     }), 
        //     }) 
        //     .then((response) => response.json()) 
        //     .then((json) => { return json.data }) 
        //     .then((data) => { 
        //         console.log(data); 
        //         $result.text("Talent successfully created."); 
        //     }) 
        //     .catch((error) => { 
        //         console.error('Error:', error); 
        // }); 
        $.ajax({ 
            url: "https://1lwasg3h0j.execute-api.us-east-1.amazonaws.com/dev/api/uploadImage", // Change to own endpoint 
            method: "POST", 
            processData: false, 
            contentType: false, 
            data: jsonForm 
        }).done((data) => { 
            console.log(data); 
            $result.text("Talent successfully created."); 
        }).fail((data) => { 
            console.log(data); 
            $result.text(data.responseJSON.Message); 
        }); 
    } else { 
        $result.text("Check your inputs."); 
    } 
}); 

function getBase64Image(element) { 
    // var preview = document.getElementById('preview'); 
    // var file = document.getElementById('formFile').files[0]; 
    // var reader = new FileReader(); 
    // let str; 
    // console.log(file); 
    // reader.addEventListener("load", function () { // Setting up base64 URL on image 
    //     preview.src = reader.result; 
    //     str = reader.result; 
    //     console.log(reader.result); 
    // }, false); 
    var file = element.files[0]; 
    var reader = new FileReader(); 
    reader.onloadend = function () { 
        console.log('RESULT', reader.result) 
    } 
    reader.readAsDataURL(file); 
    // console.log(str); 
    // var str64 = str.split(','); 
    // console.log(str64); 
} 

//SEARCH Method
$('#search').keyup(function () {
    //get data from json file
    //var urlForJson = "data.json";

    //get data from Restful web Service in development environment
    var urlForJson = "data.json"; // Change to own endpoint

    //Url for the Cloud image hosting
    var urlForCloudImage = "http://res.cloudinary.com/doh5kivfn/image/upload/v1460006156/talents/"; // Change to own bucket name

    var searchField = $('#search').val();
    var myExp = new RegExp(searchField, "i");
    $.getJSON(urlForJson, function (data) {
        var output = '<ul class="searchresults">';
        $.each(data, function (key, val) {
            //for debug
            console.log(data);
            if ((val.Name.search(myExp) != -1) ||
			(val.Bio.search(myExp) != -1)) {
                output += '<li>';
                output += '<h2>' + val.Name + '</h2>';
                //get the absolute path for local image
                //output += '<img src="images/'+ val.ShortName +'_tn.jpg" alt="'+ val.Name +'" />';

                //get the image from cloud hosting
                output += '<img src=' + urlForCloudImage + val.ShortName + "_tn.jpg alt=" + val.Name + '" />';
                output += '<p>' + val.Bio + '</p>';
                output += '</li>';
            }
        });
        output += '</ul>';
        $('#update').html(output);
    }); //get JSON
});
