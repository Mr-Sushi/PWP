"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<div class='alert alert-primary' role='alert'>" + msg + "</div>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function postEvent(event) {
    event.preventDefault();
    let data = {};
    let form = $("form[name='postEventForm']");
    data.name = $("input[name='eventName']").val();
    data.time = $("input[name='eventTime']").val();
    data.description = $("input[name='eventDesc']").val();
    data.location = $("input[name='eventLocation']").val();
    data.organization = $("input[name='eventOrg']").val();
    submitEventData(form.attr("action"), form.attr("method"), data, getSubmittedEvent);
}

function submitEventData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function showEvents(body) {
    body.events.forEach(function (event) {
        $("#event-list").append(showEvent(event));
    }
}

function showEvent(event) {
    let followEventBtn = "<a href='#' class='btn btn-secondary mr-3'>Follow</a>";
    let unfollowEventBtn = "<a href='#' class='btn btn-success mr-3'>
                            <svg class='bi bi-check' width='1em' height='1em' viewBox='0 0 16 16' fill='currentColor' xmlns='http://www.w3.org/2000/svg'>
                              <path fill-rule='evenodd' d='M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z' clip-rule='evenodd'/>
                            </svg> Followed</a>";
    let editEventBtn = "<a href='#' class='btn btn-light' data-toggle='modal' data-target='#editEventModal'>Edit</a>";
    
    let followers = "1"; // placeholder
    if (followers == 1) {
        let followersText = "follower";
    } else {
        let followers = "followers";
    }

    return "<div class='card mt-4'>
              <div class='card-body'>
                <h5 class='card-title'>"+ event.name +"</h5>
                <h6 class='card-subtitle mb-4 text-muted'>"+ event.time +"</h6>
                <p class='card-text'>"+ event.description +"</p>
                <p class='card-text'><span class='text-muted'>Location:</span> "+ event.location +"</p>
                <p class='card-text mb-4 text-muted'>Organizer: <a href='#'>"+ event.organization +"</a></p>
                <div class='row'>
                  <div class='col-sm'>" + followEventBtn + "" + followers + "" + followersText + "</div>
                  <div class='col-sm text-right'>" + editEventBtn + "</div>
                </div>
              </div>
            </div>";
}

$(document).ready(function () {
    getResource("http://localhost:5000/eventhub/", renderSensors);
});