"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    // Display error messages
    let closeAlert = "<button type='button' class='close' data-dismiss='alert' aria-label='Close' style='margin-top: -1px;'>"
                    + "<span aria-hidden='true'>&times;</span>"
                    + "</button>"
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<div class='alert alert-danger' role='alert'>" + msg + closeAlert +"</div>");
}

function renderMsg(msg, type) {
    // Display messages, type for different Bootstrap styles (primary, success)
    let closeAlert = "<button type='button' class='close' data-dismiss='alert' aria-label='Close' style='margin-top: -1px;'>"
                    + "<span aria-hidden='true'>&times;</span>"
                    + "</button>"
    $("div.notification").html("<div class='alert alert-" + type + "' role='alert'>" + msg + closeAlert +"</div>");
}

function getResource(href, renderer) {
    // console.log('getResource ' + href);
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
    // console.log('renderer ' + renderer);
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

$(document).ready(function() {
    $("form[name='postEventForm']").submit(function(e) { // Submit postEventForm
        e.preventDefault();
        $('#postEventModal').modal('toggle'); // Close the modal
        let data = {};
        let form = $("form[name='postEventForm']");
        data.name = $("input[name='eventName']").val();
        data.time = $("input[name='eventTime']").val();
        data.description = $("textarea[name='eventDesc']").val();
        data.location = $("input[name='eventLocation']").val();
        data.organization = parseInt($("select[name='eventOrg']").val());
        // console.log("Post event: " + data.name + " "+ data.time + " "+ data.description + " "+ data.location + " "+ data.organization);
        submitEventData(form.attr("action"), form.attr("method"), data, getSubmittedEvent);
    });
});

function submitEventData(href, method, item, postProcessor) {
    // console.log("submitEventData")
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
    // console.log("url: " + href);
    // console.log("type: " + method);
    // console.log("data: " + item);
    // console.log("JSON.stringify: " + JSON.stringify(item));
    renderMsg("Event Posted", "success"); // Show a message
    $("form[name='postEventForm']").find("input[type=text], textarea, select").val(""); // Clear form
}

function getSubmittedEvent(data, status, jqxhr) {
    // console.log("getSubmittedEvent");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, prependEvent);
    }
}

function refreshEventList(data, status, jqxhr) {
    // Refresh the event list
    $("#event-list").empty();
    getResource("http://localhost:5000/api/events/", listEvents);
}

function prependEvent(body) {
    // Add event cards to the top of #event-list
    // console.log("Append eventCard(body) to #event-list");
    $("#event-list").prepend(eventCard(body));
}

function eventCard(eventItem) {
    // Build event cards
    let followEventBtn = "<a href='#' class='btn btn-secondary mr-3'>Follow</a>";
    let unfollowEventBtn = "<a href='#' class='btn btn-success mr-3'><svg class='bi bi-check' width='1em' height='1em' viewBox='0 0 16 16' fill='currentColor' xmlns='http://www.w3.org/2000/svg'><path fill-rule='evenodd' d='M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z' clip-rule='evenodd'/></svg> Followed</a>";
    let editEventBtn = "<a onclick='editEvent(\"" + eventItem["@controls"].self.href + "\")' class='btn btn-light'>Edit</a>";
    
    let followers = 1;
    let followersText = " follower";
    
    if (followers == 1) {
        let followersText = " follower";
    } else {
        let followersText = " followers";
    }
    
    return "<div class='card mt-4'>"
              + "<div class='card-body'>"
                + "<h5 class='card-title'>"+ eventItem.name +"</h5>"
                + "<h6 class='card-subtitle mb-4 text-muted'>"+ eventItem.time +"</h6>"
                + "<p class='card-text'>"+ eventItem.description +"</p>"
                + "<p class='card-text'><span class='text-muted'>Location:</span> "+ eventItem.location +"</p>"
                + "<p class='card-text mb-4 text-muted'>Organizer: <a href='#'>"+ eventItem.organization +"</a></p>"
                + "<div class='row'>"
                  + "<div class='col-sm'>" + followEventBtn + "" + followers + "" + followersText + "</div>"
                  + "<div class='col-sm text-right'>" + editEventBtn + "</div>"
                + "</div>"
              + "</div>"
            + "</div>";
}

function editEvent(href) {
    $("#editEventModal").modal();
    $("form[name='editEventForm']").attr("action", "http://localhost:5000" + href, editEventForm);
    getResource("http://localhost:5000" + href, editEventForm);
}

function deleteEvent(href) {
    $("form[name='editEventForm']").attr("method", "delete");
    $("form[name='editEventForm']").attr("action", "http://localhost:5000" + href, editEventForm);
    let form = $("form[name='editEventForm']");
    deleteEventData(form.attr("action"), form.attr("method"), refreshEventList);
}

function editEventForm(body) {
    $("#updateEventTitle").val(body.name);
    $("#updateEventDesc").val(body.description);
    $("#updateEventTimeInput").val(body.time);
    $("#updateEventLocation").val(body.location);
    $("#updateEventOrganization").val(body.organization);
    $("#deleteEventBtn").attr("onclick", "deleteEvent(\"" + body["@controls"].self.href + "\")");
}

$(document).ready(function() {
    $("form[name='editEventForm']").submit(function(e) { // Submit editEventForm
        e.preventDefault();
        $('#editEventModal').modal('toggle'); // Close the modal
        let data = {};
        let form = $("form[name='editEventForm']");
        data.name = $("input[name='updateEventTitle']").val();
        data.time = $("input[name='updateEventTime']").val();
        data.description = $("textarea[name='updateEventDesc']").val();
        data.location = $("input[name='updateEventLocation']").val();
        data.organization = parseInt($("select[name='updateEventOrg']").val());
        // console.log("Update event: " + data.name + " "+ data.time + " "+ data.description + " "+ data.location + " "+ data.organization);
        editEventData(form.attr("action"), form.attr("method"), data, refreshEventList);
    });
});

function editEventData(href, method, item, postProcessor) {
    console.log("editEventData")
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
    // console.log("url: " + href);
    // console.log("type: " + method);
    // console.log("data: " + item);
    // console.log("JSON.stringify: " + JSON.stringify(item));
    renderMsg("Event Saved", "success"); // Show a message
}

function deleteEventData(href, method, postProcessor) {
    console.log("deleteEventData")
    $.ajax({
        url: href,
        type: method,
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
    // console.log("url: " + href);
    // console.log("type: " + method);
    // console.log("data: " + item);
    // console.log("JSON.stringify: " + JSON.stringify(item));
    renderMsg("Event Deleted", "success"); // Show a message
}

function listEvents(body) {
    // Get events
    // console.log("listEvents");
    // console.log("body: " + body);
    // console.log("body.event_list: " + body.event_list);
    body.event_list.forEach(function (eventItem) {
        $("#event-list").prepend(eventCard(eventItem));
    });
}

$(document).ready(function() {
    // console.log("Document ready");
    getResource("http://localhost:5000/api/events/", listEvents);
});